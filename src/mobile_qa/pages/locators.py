"""Selectors are centralised here so app-version changes are easy to review."""

from appium.webdriver.common.appiumby import AppiumBy

# Most builds of the Sauce Labs sample app expose test-* accessibility identifiers.
# The text-based fallbacks help when a packaged build exposes the visible label instead.
SELECTORS = {
    "username": {
        "shared": [
            (AppiumBy.ACCESSIBILITY_ID, "test-Username"),
            (AppiumBy.ID, "test-Username"),
            (AppiumBy.ACCESSIBILITY_ID, "Username"),
        ],
        "android": [
            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().className("android.widget.EditText").instance(0)'),
        ],
        "ios": [
            (AppiumBy.IOS_PREDICATE, 'type == "XCUIElementTypeTextField" AND (label CONTAINS[c] "Username" OR name CONTAINS[c] "Username")'),
        ],
    },
    "password": {
        "shared": [
            (AppiumBy.ACCESSIBILITY_ID, "test-Password"),
            (AppiumBy.ID, "test-Password"),
            (AppiumBy.ACCESSIBILITY_ID, "Password"),
        ],
        "android": [
            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().className("android.widget.EditText").instance(1)'),
        ],
        "ios": [
            (AppiumBy.IOS_PREDICATE, 'type == "XCUIElementTypeSecureTextField" OR (type == "XCUIElementTypeTextField" AND (label CONTAINS[c] "Password" OR name CONTAINS[c] "Password"))'),
        ],
    },
    "login_button": {
        "shared": [
            (AppiumBy.ACCESSIBILITY_ID, "test-LOGIN"),
            (AppiumBy.ID, "test-LOGIN"),
            (AppiumBy.ACCESSIBILITY_ID, "LOGIN"),
            (AppiumBy.ACCESSIBILITY_ID, "Log In"),
        ],
        "android": [(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textMatches("(?i)log ?in")')],
        "ios": [(AppiumBy.IOS_PREDICATE, 'type == "XCUIElementTypeButton" AND (label CONTAINS[c] "login" OR name CONTAINS[c] "login")')],
    },
    "login_error": {
        "shared": [
            (AppiumBy.ACCESSIBILITY_ID, "test-Error message"),
            (AppiumBy.ACCESSIBILITY_ID, "test-Error"),
            (AppiumBy.ACCESSIBILITY_ID, "Username and password do not match any user in this service."),
        ],
        "android": [(AppiumBy.XPATH, "//*[contains(@text, 'match') or contains(@text, 'error') or contains(@content-desc, 'Error')]")],
        "ios": [(AppiumBy.IOS_PREDICATE, 'label CONTAINS[c] "match" OR label CONTAINS[c] "error"')],
    },
    "products_heading": {
        "shared": [
            (AppiumBy.ACCESSIBILITY_ID, "test-PRODUCTS"),
            (AppiumBy.ACCESSIBILITY_ID, "PRODUCTS"),
        ],
        "android": [(AppiumBy.XPATH, "//*[@text='PRODUCTS' or @content-desc='PRODUCTS']")],
        "ios": [(AppiumBy.IOS_PREDICATE, 'label == "PRODUCTS" OR name == "PRODUCTS"')],
    },
    "menu_button": {
        "shared": [
            (AppiumBy.ACCESSIBILITY_ID, "test-Menu"),
            (AppiumBy.ACCESSIBILITY_ID, "Menu"),
        ],
        "android": [(AppiumBy.XPATH, "//*[@content-desc='Open Menu' or @text='Open Menu' or @content-desc='Menu']")],
        "ios": [(AppiumBy.IOS_PREDICATE, 'label CONTAINS[c] "menu" OR name CONTAINS[c] "menu"')],
    },
    "logout_button": {
        "shared": [
            (AppiumBy.ACCESSIBILITY_ID, "test-LOGOUT"),
            (AppiumBy.ACCESSIBILITY_ID, "LOGOUT"),
            (AppiumBy.ACCESSIBILITY_ID, "Log Out"),
        ],
        "android": [(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textMatches("(?i)log ?out")')],
        "ios": [(AppiumBy.IOS_PREDICATE, 'label CONTAINS[c] "logout" OR label CONTAINS[c] "log out" OR name CONTAINS[c] "logout"')],
    },
    "add_to_cart": {
        "shared": [
            (AppiumBy.ACCESSIBILITY_ID, "test-ADD TO CART"),
            (AppiumBy.ACCESSIBILITY_ID, "ADD TO CART"),
            (AppiumBy.ACCESSIBILITY_ID, "Add to cart"),
        ],
        "android": [(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textMatches("(?i)add to cart")')],
        "ios": [(AppiumBy.IOS_PREDICATE, 'type == "XCUIElementTypeButton" AND label CONTAINS[c] "add to cart"')],
    },
    "remove_from_cart": {
        "shared": [
            (AppiumBy.ACCESSIBILITY_ID, "test-REMOVE"),
            (AppiumBy.ACCESSIBILITY_ID, "REMOVE"),
            (AppiumBy.ACCESSIBILITY_ID, "REMOVE FROM CART"),
        ],
        "android": [(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textMatches("(?i)remove( from cart)?")')],
        "ios": [(AppiumBy.IOS_PREDICATE, 'type == "XCUIElementTypeButton" AND label CONTAINS[c] "remove"')],
    },
}
