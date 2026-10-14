# Design Notes – Mobile UI Automation Framework

## 1. Why I built the framework this way

I put this framework together to cover the main mobile UI automation flows requested for the assessment using the Sauce Labs sample app. I wanted the tests to be readable enough that someone could understand the user journey without having to read Appium code first, while still keeping the Python implementation straightforward to maintain.

The main flows I am covering are:

- Sign in with valid credentials.
- Try to sign in with invalid credentials and verify that the app shows an error.
- Sign out and confirm that the app returns to the login screen.
- Add a product to the cart and verify that the product action changes as expected.

I chose Python with Appium, pytest, and pytest-bdd. Python keeps the framework relatively lightweight, pytest gives me fixtures and useful failure output, and BDD lets me describe the scenarios in terms of what a user is doing. Appium gives me a route to run the same high-level flows on Android and iOS, while allowing platform-specific capabilities and locators where the two platforms behave differently.

I have kept the implementation focused on the assessment rather than trying to build a large, generic automation library. If the number of screens or flows grows, I can add more page objects and supporting utilities without having to rewrite the feature scenarios.

## 2. Where the project stands right now

I am treating the current state as a work in progress. The latest execution output gives me a useful baseline, but it does not yet prove that the full suite works on both platforms.

| Scenario / platform | Current result | What I know so far |
|---|---|---|
| Valid login – iOS | Passed | The login flow completed successfully in the supplied run. |
| Invalid login – iOS | Passed | The invalid-credentials scenario completed successfully in the supplied run. |
| Logout – iOS | Failed | After the logout flow, the test could not find the expected username field on the login screen. |
| Add product to cart – iOS | Failed | The test timed out while looking for the `add_to_cart` control. |
| Android startup | Needs investigation | The app displays an Android App Compatibility dialog about 16 KB page-size alignment. The functional Android flows cannot be considered verified until startup is understood and the scenarios are run. |

These results are based on the report and screenshot available to me. I have not marked Android as passed, and I have not assumed that either iOS failure is definitely caused by a locator alone. A timeout tells me what the framework could not find; it does not, by itself, tell me why the element was missing.

My next step is to use the screenshots and page-source files captured during the failed tests to establish what screen the app was actually showing. After that, I can update the selectors or test flow based on evidence instead of adding more guesses.

## 3. How a test moves through the framework

I have separated the framework into a few layers so that each file has a clear responsibility. A typical BDD scenario follows this path:

1. **Feature file – `features/authentication.feature`**  
   This is where I describe the user journey in Gherkin. The steps should say what the user is trying to do and what result is expected, rather than explain how Appium finds or taps a control.

2. **Step definitions – `tests/steps/test_mobile_steps.py`**  
   These connect the Gherkin steps to Python code. I keep them fairly thin: they call a page-object method and check the outcome. I do not want raw locator definitions or long sequences of low-level Appium commands scattered through the step definitions.

3. **Fixtures and test setup – `tests/conftest.py` and `tests/steps/conftest.py`**  
   The fixtures provide the driver and page objects to the tests. They also help keep setup and cleanup out of the scenario steps. The teardown path attempts to collect useful evidence when a test fails.

4. **Configuration – `config/config.json` and `src/mobile_qa/config.py`**  
   This is where the framework gets details such as the platform, device, app path, and timeouts. I can change the target device or app build without changing the test scenario itself.

5. **Driver creation – `src/mobile_qa/driver_factory.py`**  
   This creates the Appium session with Android UiAutomator2 or iOS XCUITest options, depending on the selected platform.

6. **Page objects and locators – `src/mobile_qa/pages/`**  
   These classes contain the actions and selectors used to interact with the app. This is the layer I expect to update when a verified locator changes or a screen gains a new behaviour.

7. **Test results – `reports/`**  
   The test run can produce an HTML report and failure artifacts. I use those results to decide what to investigate next.

The main benefit of this split is that a change to a selector should normally stay inside the locator or page-object layer. It should not require me to rewrite the feature file or every test that uses that screen.

## 4. How I am using the Page Object Model

I have used the Page Object Model (POM) by putting screen-specific behaviour into page classes and keeping the BDD steps focused on the user journey. The current page objects are intentionally small because the assessment only covers a few flows.

### `BasePage`

`BasePage` holds behaviour that more than one screen can use. It has access to the Appium driver and the selected platform, and it provides helper methods such as finding an element, checking whether an element exists, tapping a control, and entering text.

The main reason I put these common actions in one place is to avoid repeating slightly different wait and locator logic in every page class. If I need to improve the way elements are found or how timeouts are reported, I can make that change centrally.

The current `find()` method tries the candidate locators registered for a semantic locator name and uses an explicit wait with polling. This is better than relying on a fixed sleep, but it still depends on the locator candidates being correct. Waiting longer will not fix a selector that does not match the app's accessibility tree.

### `LoginPage`

`LoginPage` represents the login screen. It contains the behaviour needed to check whether the login form is present, enter the username and password, submit the form, and look for invalid-login feedback.

The step definition should not need to know whether the username field is found by accessibility ID or an iOS predicate. It should be able to call something like `sign_in()` and then check the result. That is the separation I want from POM.

### `InventoryPage`

`InventoryPage` represents the products screen and currently covers the main inventory checks, adding the first product to the cart, checking for the changed button state, and opening the menu to sign out.

For the current scope, I have kept the cart action here because the test only adds one item and checks the immediate UI change. If I extend the flow to open the cart, check multiple items, update quantities, or go through checkout, I would introduce a separate `CartPage`. That would keep `InventoryPage` from becoming a page object that handles too many unrelated screens.

### Is the POM followed?

Yes, the project uses POM: screen interactions live in page classes, selectors are centralised, and the BDD steps call page-object methods rather than interacting with elements directly. I would still consider it an initial implementation rather than a finished POM design. The failed logout and add-to-cart tests show that I need to validate the selectors and screen-state checks against the real app hierarchy. Once the current flows are stable, I can refine the page boundaries further if the suite grows.

## 5. Locator strategy: what I prefer and what I need to verify

I have centralised selectors in `src/mobile_qa/pages/locators.py` and given them semantic names such as `username`, `login_button`, `logout_button`, and `add_to_cart`. This means a test asks for the control by its purpose, rather than carrying platform-specific selector strings around the codebase.

My preferred locator order is:

1. An accessibility ID or content description that is deliberately exposed by the app and remains stable.
2. A platform-specific selector based on the actual accessibility hierarchy, such as Android UIAutomator or an iOS predicate.
3. A narrow fallback when I have checked that it matches the current app version.

I do not want to keep adding alternative selectors just to make a test pass. Several unverified fallbacks can make the test slower and harder to debug, and they can hide a change in the app. When a locator fails, I want to inspect the page source or use Appium Inspector, find the real identifier, and update the central locator definition.

### What happened with logout on iOS

The test failed at the final assertion because `login_page.is_open()` returned `False`. The log also shows a timeout while trying to find the `username` element. That means the expected login field was not found at the time the assertion ran.

At this stage, I cannot say for certain whether the logout tap failed, the app was still transitioning, or the login field has a different accessible identifier on this iOS build. I need to inspect the saved screenshot and XML/page source from this exact failure. I will then check the menu-opening locator, the logout control, and the username/password controls separately.

I do not plan to fix this by adding a fixed delay without evidence. If the app needs time to transition, I should wait for a meaningful condition, such as the login form becoming visible. If the wrong screen is displayed, I need to fix the action or state handling instead.

### What happened with add-to-cart on iOS

The log says the framework tried several candidates for `add_to_cart`, including accessibility IDs resembling `test-ADD TO CART` and `ADD TO CART`, plus an iOS predicate looking for a button label containing “add to cart”. None of those candidates matched before the wait timed out.

My first check is to confirm that the test is actually on the products screen and that the product list has loaded. Then I will inspect the captured page source or Appium Inspector to see the real element type, label, and identifier. If the button is exposed within each product row, I will use a product-row-specific locator so that the test taps the correct product's button instead of relying on a broad label match.

## 6. Synchronisation and handling flaky tests

I am using explicit waits because mobile screens do not always become ready immediately after a tap or navigation. Fixed sleeps are easy to add, but they make tests slower when the app is fast and still unreliable when the app is slower than expected.

The important point is to wait for the right condition. For example, after submitting the login form, I should wait for a reliable indication that the inventory screen is open. After logging out, I should wait for the login form to become visible. Waiting only for an element to exist may not be enough if it is hidden or disabled, so I may need to use visibility or enabled-state checks for interactions where that matters.

When a test fails, this is the order I intend to follow:

1. Check the first meaningful exception and the semantic locator name in the log.
2. Look at the screenshot captured at the time of failure.
3. Inspect the saved page source to see what elements were actually available.
4. Confirm that the app was on the expected screen before the failed action.
5. Verify the locator in Appium Inspector or against the page source.
6. Update the page object or locator and rerun just that scenario.
7. Once the scenario passes consistently, run the full suite on that platform.

I want to avoid blanket retries. A retry can be useful for a known, temporary device-provisioning issue, but it should not hide a repeatable locator problem or an actual app defect. If I add retries in CI later, I will keep them limited to clearly identified infrastructure failures and make sure the first failure is still recorded.

## 7. Android startup issue: 16 KB page-size compatibility dialog

The screenshot supplied with the current run shows an **Android App Compatibility** dialog. It says the app is not 16 KB compatible and lists native libraries that are not 16 KB aligned, including React Native-related libraries. The dialog says Android will run the app in page-size compatibility mode and recommends rebuilding the app with 16 KB support.

I am treating this as an app binary and runtime compatibility issue to investigate, rather than a locator problem in the automation code. The dialog can cover the app's normal first screen, so a test that expects to find the username field immediately may fail before the login flow has even started.

My investigation plan is:

1. Record the Android emulator API level, system image, CPU architecture, Appium version, UiAutomator2 driver version, and exact APK being used.
2. Dismiss the dialog manually once and check whether the app continues to launch and the login screen becomes usable.
3. Check whether the dialog appears on every fresh launch or only on this emulator configuration. I will treat selecting “Don't Show Again” as a temporary diagnostic, not as a fix for the underlying compatibility warning.
4. Check whether there is a newer Sauce Labs sample-app build intended to work with the chosen Android environment.
5. If the app source or build pipeline is available, investigate rebuilding the native libraries with 16 KB page-size support. If the binary is supplied and cannot be rebuilt, record the limitation and use a compatible app build/emulator combination where possible.
6. Once the app starts without blocking the test, rerun the four Android flows and save the actual results.

I do not want to add an unconditional “tap OK” action to every test unless I establish that the dialog is an expected and stable part of the environment. It may not appear on another emulator, and a blind tap could interact with the wrong screen. The better outcome is a clean, repeatable startup. If that is not possible with the supplied binary, I will document the limitation clearly rather than claim Android coverage that I have not verified.

## 8. Android and iOS support

The driver factory selects the appropriate Appium automation backend: UiAutomator2 for Android and XCUITest for iOS. The common configuration covers values such as platform, device name, app path, reset behaviour, and timeouts, while platform-specific capabilities are supplied where needed.

I have designed the tests so that the same user-level scenario can be used on both platforms. That does not mean Android and iOS are identical. They expose accessibility elements differently, use different app package formats, and have different simulator/device setup requirements. The test intent and page-object API can be shared, while the selectors and driver configuration can differ when there is a real platform difference.

For local execution, I need to use an Android APK that is compatible with the selected emulator and an iOS `.app` bundle built for the iOS Simulator. An `.ipa` intended for a physical iPhone is not automatically interchangeable with a simulator `.app`; real-device execution also involves signing and provisioning requirements. I will record the actual device and app build used for a run so a result can be reproduced later.

## 9. Configuration and credentials

I have moved device and app settings out of the test steps so that I can change execution targets without editing the tests. The intended configuration order is command-line options first, then environment variables / `.env`, then `config/config.json`. This lets me use a sensible local default and override it for another simulator or for CI.

The configuration file is also a way to make the setup easier for someone else to follow. The README should explain which values need to be changed, where the Android APK or iOS simulator app should be placed, and how to select the target platform.

I will not commit machine-specific secrets, private signing material, or real cloud-device credentials. The Sauce Labs sample app's published demo credentials are test data, but keeping credentials in configuration rather than hard-coding them into page methods makes the framework easier to maintain if the test data changes.

## 10. BDD scenarios and tags

I am using Gherkin to keep the scenarios understandable without requiring the reader to know Appium. The feature file should describe the user action and expected result; the step definitions should connect that statement to the relevant page object. This keeps the BDD layer useful instead of turning it into a second place where UI automation code is written.

I use tags to make it possible to select a smaller set of tests or a wider regression run:

- `@smoke` is for a small set of high-value checks, such as successful login.
- `@regression` is for the broader functional scenarios, including invalid login, logout, and adding a product to the cart.
- `@api` is for API checks that can run independently of a mobile device session.

A tag only tells me how a test is categorised; it does not prove that the test is stable or that a platform is covered. I have also kept the API example separate from the mobile app flows. The current API test uses JSONPlaceholder because an API specification for the Sauce Labs sample app was not supplied. It is an example of API test structure, not an integration test of the mobile app's backend.

## 11. Failure evidence and reports

When a test fails, the teardown logic attempts to save a screenshot and page source, and to collect Android logcat where it is available. I have added this because a timeout by itself does not tell me whether the app was showing a compatibility dialog, had opened a different screen, or had changed an accessibility label.

For a useful investigation, I want to retain the following information together:

- The scenario name and the original exception.
- A screenshot from the point of failure.
- The page source or accessibility hierarchy from the same point.
- Appium server logs around session creation and the failed command.
- Android logcat when the issue is specific to Android.
- The device, OS, app, Appium, and driver versions used for the run.

Artifact collection is best-effort. If saving a screenshot fails, I do not want that secondary problem to hide the original test failure. I also need to distinguish reports produced by a real test run from example output included for demonstration. Only actual execution results should be presented as evidence that a scenario passed.

## 12. Current action plan

I am prioritising the work based on what is blocking meaningful verification rather than adding more scenarios before the current ones are stable.

| Priority | Item | What I plan to do | What will count as done |
|---|---|---|---|
| P0 | Android compatibility dialog | Confirm the emulator and APK details, check whether the app can continue past the dialog, and look for a compatible app build or emulator setup. | App starts in a predictable state, or the external compatibility blocker is clearly documented. |
| P1 | iOS logout | Inspect the failed screenshot and page source, verify the menu/logout controls, and check the real post-logout state. | The logout scenario passes repeatedly on iOS. |
| P1 | iOS add-to-cart | Inspect the product list hierarchy, confirm the app is on the inventory screen, and use a verified locator. | The first product's action changes to the expected remove state. |
| P2 | Android functional scenarios | Run login, invalid login, logout, and add-to-cart after startup is resolved. | The report contains real, per-scenario Android results. |
| P2 | Repeatability | Rerun the scenarios on each platform and keep environment details with the reports. | Results are repeatable and intermittent failures can be investigated from saved evidence. |

## 13. How I use AI while working on this

I use AI as a development aid to help structure the framework, review the separation between the feature file and page objects, explore Appium capability options, and turn long failure logs into a more focused debugging checklist. It is useful for quickly generating possible explanations and identifying what evidence I should collect next.

I do not treat an AI suggestion as proof that a locator is correct or that a scenario has passed. For example, the iOS add-to-cart locator needs to be checked against the actual page source, and the Android compatibility warning needs to be understood in the context of the APK and emulator being used. I use the tool to help decide what to inspect, then I validate the change by running the test and checking the result.

This is also how I want to handle fixes: make one targeted change, rerun the affected scenario, review the artifacts, and only then run the broader suite. That gives me a clearer idea of whether the change solved the problem or simply moved the failure somewhere else.

## 14. Current assessment

At this point, I have a working starting structure with BDD scenarios, page objects, centralised locators, external configuration, platform-specific Appium setup, and failure-artifact collection. The latest iOS report confirms that valid login and invalid login are working in that run. Logout and add-to-cart still need investigation, and Android functional coverage has not yet been verified because the app displays the 16 KB compatibility dialog.

I consider the framework structure to be in place, but the implementation is not finished. My immediate focus is to use the captured failure evidence to fix the iOS flows and to establish a clean Android startup. After those changes, I will rerun the scenarios on both platforms and update the status based on the actual results. I would rather document an unresolved issue honestly than make the framework look more complete than it is.
