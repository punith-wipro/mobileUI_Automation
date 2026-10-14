"""Build an Appium driver for the selected mobile platform."""

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions

from mobile_qa.config import MobileSettings, resolve_app_path


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

    return webdriver.Remote(command_executor=settings.server_url, options=options)
