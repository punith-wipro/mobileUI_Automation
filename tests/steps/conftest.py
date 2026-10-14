"""Appium session fixture used only by mobile UI scenarios."""

import logging
import re

import pytest

from mobile_qa.config import PROJECT_ROOT
from mobile_qa.driver_factory import create_driver

LOGGER = logging.getLogger(__name__)
FAILURES_DIR = PROJECT_ROOT / "reports" / "failures"


@pytest.fixture
def driver(request, mobile_settings):
    """Start a clean session per scenario and save diagnostics when a test fails."""
    settings = mobile_settings
    LOGGER.info(
        "Starting Appium session: platform=%s device=%s app=%s",
        settings.platform,
        settings.device_name,
        settings.app_path,
    )
    session = create_driver(settings)
    session.implicitly_wait(0)
    yield session

    try:
        report = getattr(request.node, "rep_call", None)
        if report is not None and report.failed:
            FAILURES_DIR.mkdir(parents=True, exist_ok=True)
            safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", request.node.nodeid).strip("_")
            try:
                session.save_screenshot(str(FAILURES_DIR / f"{safe_name}.png"))
                (FAILURES_DIR / f"{safe_name}.xml").write_text(session.page_source, encoding="utf-8")
                LOGGER.error("Saved screenshot and page source for failed test: %s", safe_name)
            except Exception:  # Keep the original test failure as the main failure.
                LOGGER.exception("Could not collect screenshot/page source after failure")
            if settings.platform == "android":
                try:
                    log_entries = session.get_log("logcat")[-250:]
                    log_lines = [str(item) for item in log_entries]
                    (FAILURES_DIR / f"{safe_name}-logcat.txt").write_text(
                        "\n".join(log_lines), encoding="utf-8"
                    )
                except Exception:
                    LOGGER.info("Android logcat was not available from this Appium session")
    finally:
        try:
            session.quit()
        except Exception:
            LOGGER.exception("Appium session could not be closed cleanly")
