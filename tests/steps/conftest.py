"""Reuse one Appium session and isolate each scenario at the app level."""

import logging
import re

import pytest
from selenium.common.exceptions import TimeoutException, WebDriverException

from mobile_qa.config import PROJECT_ROOT
from mobile_qa.driver_factory import create_driver
from mobile_qa.pages.inventory_page import InventoryPage
from mobile_qa.pages.login_page import LoginPage

LOGGER = logging.getLogger(__name__)
FAILURES_DIR = PROJECT_ROOT / "reports" / "failures"
IOS_BUNDLE_ID = "com.saucelabs.SwagLabsMobileApp"


@pytest.fixture(scope="session")
def appium_session(mobile_settings):
    """Create one Appium session for the whole test run; quit it at session end."""
    settings = mobile_settings
    LOGGER.info(
        "Starting reusable Appium session: platform=%s device=%s app=%s",
        settings.platform,
        settings.device_name,
        settings.app_path,
    )
    session = create_driver(settings)
    session.implicitly_wait(0)
    yield session
    try:
        session.quit()
    except Exception:
        LOGGER.exception("Appium session could not be closed cleanly")


def _return_to_login(session, settings) -> None:
    """Restore the app to its login screen without rebooting the simulator."""
    login_page = LoginPage(session, settings.platform, settings.timeout_seconds)
    inventory_page = InventoryPage(session, settings.platform, settings.timeout_seconds)

    if login_page.is_open():
        return

    # Most scenarios leave the app on the products screen. Log out normally so
    # the next scenario starts at login and keeps a realistic user flow.
    if inventory_page.is_open():
        inventory_page.sign_out()
        if login_page.is_open():
            return

    # Unexpected screen fallback: restart only the AUT, not the iOS Simulator.
    # Keep the Appium session alive to avoid repeatedly booting/reinstalling the app.
    if settings.platform == "ios":
        session.terminate_app(IOS_BUNDLE_ID)
        session.activate_app(IOS_BUNDLE_ID)
    else:
        # Android app reset is performed by its package/activity via the session's
        # app capability; activate_app is supported by UiAutomator2 as well.
        app_id = session.capabilities.get("appPackage") or "com.swaglabsmobileapp"
        session.terminate_app(app_id)
        session.activate_app(app_id)

    if not login_page.is_open():
        raise AssertionError(
            f"Could not restore {settings.platform} app to the login screen between scenarios"
        )


@pytest.fixture
def driver(request, mobile_settings, appium_session):
    """Share the session while resetting app navigation between scenarios."""
    session = appium_session
    settings = mobile_settings
    _return_to_login(session, settings)
    yield session

    report = getattr(request.node, "rep_call", None)
    if report is not None and report.failed:
        FAILURES_DIR.mkdir(parents=True, exist_ok=True)
        safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", request.node.nodeid).strip("_")
        try:
            session.save_screenshot(str(FAILURES_DIR / f"{safe_name}.png"))
            (FAILURES_DIR / f"{safe_name}.xml").write_text(session.page_source, encoding="utf-8")
            LOGGER.error("Saved screenshot and page source for failed test: %s", safe_name)
        except Exception:
            LOGGER.exception("Could not collect screenshot/page source after failure")
        if settings.platform == "android":
            try:
                log_entries = session.get_log("logcat")[-250:]
                (FAILURES_DIR / f"{safe_name}-logcat.txt").write_text(
                    "\n".join(str(item) for item in log_entries), encoding="utf-8"
                )
            except Exception:
                LOGGER.info("Android logcat was not available from this Appium session")
