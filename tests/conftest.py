"""Shared pytest options and light-weight test reporting hooks."""

import pytest

from mobile_qa.config import load_settings


def pytest_addoption(parser):
    group = parser.getgroup("mobile")
    group.addoption("--platform", choices=("android", "ios"), default=None, help="Mobile platform")
    group.addoption("--device-name", default=None, help="Emulator or simulator name")
    group.addoption("--platform-version", default=None, help="OS version to request from Appium")
    group.addoption("--app-path", default=None, help="Local app path or remote app URL")
    group.addoption("--appium-url", default=None, help="Appium server URL")


@pytest.fixture(scope="session")
def mobile_settings(request):
    return load_settings(request.config)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


def pytest_report_header(config):
    return "Mobile UI suite: Appium + pytest-bdd; device settings loaded from config/env/CLI"
