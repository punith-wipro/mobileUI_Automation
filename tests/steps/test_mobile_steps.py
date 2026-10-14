"""Gherkin step definitions; screen interactions stay in page objects."""

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from mobile_qa.config import PROJECT_ROOT
from mobile_qa.pages.inventory_page import InventoryPage
from mobile_qa.pages.login_page import LoginPage

FEATURE_FILE = PROJECT_ROOT / "features" / "authentication.feature"
scenarios(str(FEATURE_FILE))


@pytest.fixture
def login_page(driver, mobile_settings):
    return LoginPage(driver, mobile_settings.platform, mobile_settings.timeout_seconds)


@pytest.fixture
def inventory_page(driver, mobile_settings):
    return InventoryPage(driver, mobile_settings.platform, mobile_settings.timeout_seconds)


@given("the app is on the login screen")
def app_is_on_login_screen(login_page):
    assert login_page.is_open(), "Login screen was not visible when the app started"


@when(parsers.parse('I sign in with username "{username}" and password "{password}"'))
def sign_in(login_page, username, password):
    login_page.sign_in(username, password)


@then("the products screen is displayed")
def products_screen_is_displayed(inventory_page):
    assert inventory_page.is_open(), "Expected the products screen after a successful login"


@then("a login error is displayed")
def login_error_is_displayed(login_page):
    assert login_page.has_error(), "Expected the app to reject invalid credentials"


@when("I log out")
def log_out(inventory_page):
    inventory_page.sign_out()


@then("the app returns to the login screen")
def login_screen_returns(login_page):
    assert login_page.is_open(), "Expected the login fields after logging out"


@when("I add the first product to the cart")
def add_first_product(inventory_page):
    inventory_page.add_first_product_to_cart()


@then("the first product can be removed from the cart")
def product_was_added(inventory_page):
    assert inventory_page.first_product_is_in_cart(), "The add-to-cart action did not change to a remove action"
