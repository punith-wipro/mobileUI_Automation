"""Build an Appium driver for the selected mobile platform."""

import logging
import time

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions
from appium.webdriver.common.appiumby import AppiumBy

from mobile_qa.config import MobileSettings, resolve_app_path

LOGGER = logging.getLogger(__name__)


def _dismiss_android_compatibility_dialog(driver, timeout: float = 5.0) -> None:
    """Dismiss Android's known 16 KB compatibility warning if it is displayed.

    This only dismisses the OS warning so UI tests can continue. It does not
    rebuild or make the APK's native libraries 16 KB aligned. The sample APK
    bundled with this assessment is a prebuilt binary, so a true binary-level
    fix requires a compatible upstream build or rebuilding the app and native
    dependencies from source.
    """
    deadline = time.monotonic() + timeout
    title_selector = 'new UiSelector().textContains("Android App Compatibility")'

    while time.monotonic() < deadline:
        try:
            title_matches = driver.find_elements(AppiumBy.ANDROID_UIAUTOMATOR, title_selector)
            page_has_title = "Android App Compatibility" in (driver.page_source or "")
            if title_matches or page_has_title:
                # Prefer the explicit opt-out button so the same modal does not
                # interrupt every scenario on this emulator. Fall back to OK.
                for selector in (
                    'new UiSelector().textContains("Show Again")',
                    'new UiSelector().text("OK")',
                ):
                    buttons = driver.find_elements(AppiumBy.ANDROID_UIAUTOMATOR, selector)
                    if buttons:
                        buttons[0].click()
                        LOGGER.warning(
                            "Dismissed Android App Compatibility dialog. "
                            "The APK may still run in 16 KB compatibility mode."
                        )
                        return
                LOGGER.warning("Detected Android compatibility dialog but could not find its dismiss button")
                return
        except Exception as exc:
            # Some Appium versions temporarily cannot read the system window
            # while the app is starting. Keep polling; do not hide startup errors.
            LOGGER.debug("Waiting for Android compatibility dialog state: %s", exc)
        time.sleep(0.4)


def create_driver(settings: MobileSettings):
    app = resolve_app_path(settings.app_path)
    capabilities = {
        "platformName": "Android" if settings.platform == "android" else "iOS",
        "automationName": settings.automation_name,
        "deviceName": settings.device_name,
        "newCommandTimeout": 120,
        "noReset": settings.no_reset,
        "app": app,
    }
    if settings.platform_version:
        capabilities["platformVersion"] = settings.platform_version

    if settings.platform == "android":
        options = UiAutomator2Options().load_capabilities(capabilities)
    else:
        options = XCUITestOptions().load_capabilities(capabilities)

    driver = webdriver.Remote(command_executor=settings.server_url, options=options)
    if settings.platform == "android":
        _dismiss_android_compatibility_dialog(driver)
    return driver
