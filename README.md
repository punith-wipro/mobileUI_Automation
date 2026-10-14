# Mobile UI Automation Framework

> Cross-platform mobile UI automation using Appium, Python, pytest, and pytest-bdd.

## Overview

This framework automates the Sauce Labs sample mobile app on Android and iOS. It uses readable BDD scenarios, the Page Object Model (POM), and configuration-driven execution so the same test suite can run against different devices.

The goal is to keep the framework straightforward to maintain and make test failures easier to investigate.

## Coverage

Mobile scenarios:

- Successful login
- Login with invalid credentials
- Logout
- Add a product to the cart

The mobile scenarios use `@smoke` and/or `@regression` tags. Two example API smoke tests are also included and use the `@api` tag.

The API examples use JSONPlaceholder because no target API specification was provided. They demonstrate separate API-test execution and configuration; they are not validation of a product backend. The demo POST endpoint does not persist data.

## Framework design

- **Python and pytest** provide test execution, fixtures, and reporting.
- **Appium** provides a common WebDriver interface for Android (UiAutomator2) and iOS (XCUITest).
- **pytest-bdd** keeps the main user journeys in Gherkin feature files.
- **Page Object Model** keeps locators and screen actions in page objects; step definitions focus on user behaviour.
- **Centralised locators** make it easier to update selectors when the app changes.
- **Configuration and environment overrides** allow platform, device, app path, and Appium URL to change without editing test code.
- **Failure artifacts** help with diagnosis by collecting screenshots, page source, and Android logcat output when available.

Accessibility IDs are preferred where the app exposes them. Small fallback locator lists handle known platform differences. If a selector stops matching, inspect the current hierarchy with Appium Inspector and update the locator centrally rather than adding fixed sleeps or brittle XPath to test steps.

## Project structure

```text
config/config.json               Platform, device, and app defaults
features/authentication.feature  BDD scenarios and tags
src/mobile_qa/config.py          Configuration loading and overrides
src/mobile_qa/driver_factory.py  Android/iOS Appium capabilities
src/mobile_qa/pages/             Base page, locators, and screen objects
tests/steps/                     BDD step definitions and fixtures
tests/api/                       API smoke-test examples
reports/                         Generated reports and failure artifacts
apps/                            Local app builds (not committed in Git)
```

## Prerequisites

1. Python 3.10 or newer.
2. Node.js and Appium 2.
3. An Android emulator/device or an iOS Simulator. iOS Simulator execution requires macOS and Xcode.
4. The matching Appium driver.
5. The sample app build for the platform being tested.

Install Appium and its drivers:

```bash
npm install -g appium
appium driver install uiautomator2
# On macOS for iOS Simulator:
appium driver install xcuitest
```

Download the appropriate build from the [Sauce Labs sample app releases](https://github.com/saucelabs/sample-app-mobile/releases) and place it in `apps/`.

- **Android:** use the `.apk` build.
- **iOS Simulator:** use the simulator `.app` build or its ZIP archive, not a real-device `.ipa` build. Real-device iOS signing requires separate setup.

App binaries are excluded from Git. Download the required build after cloning the repository, or configure the path to a build already on your machine.

## Install dependencies

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

On Windows PowerShell, activate the environment with:

```powershell
.\.venv\Scripts\Activate.ps1
```

Update `.env` only if you want to override settings with environment variables. Do not commit credentials or other secrets.

## Configuration

`config/config.json` contains default settings such as platform, Appium URL, device name, platform version, and app path. The framework resolves settings in this order:

1. pytest command-line option
2. Environment variable or `.env`
3. `config/config.json`

Relevant environment variables:

- `MOBILE_PLATFORM`
- `DEVICE_NAME`
- `PLATFORM_VERSION`
- `ANDROID_APP_PATH`
- `IOS_APP_PATH`
- `APPIUM_SERVER_URL`
- `API_BASE_URL` for API examples

The app path can point to an extracted iOS `.app` directory or its ZIP archive. Use the exact filename of the build you downloaded.

## Running mobile tests

Start the Android emulator or iOS Simulator first. Start Appium in a separate terminal:

```bash
appium
```

Create the reports directory before running tests:

```bash
mkdir -p reports
```

### Android

```bash
export MOBILE_PLATFORM=android
export ANDROID_APP_PATH="$PWD/apps/Android.SauceLabs.Mobile.Sample.app.2.7.1.apk"

REPORT="reports/android-$(date +%Y%m%d-%H%M%S).html"
pytest tests/steps -m "smoke or regression" \
  --html="$REPORT" --self-contained-html
```

### iOS Simulator (macOS only)

```bash
export MOBILE_PLATFORM=ios
export IOS_APP_PATH="$PWD/apps/iOS.Simulator.SauceLabs.Mobile.Sample.app.2.7.1.app"
export DEVICE_NAME="iPhone 16"

REPORT="reports/ios-$(date +%Y%m%d-%H%M%S).html"
pytest tests/steps -m "smoke or regression" \
  --device-name "iPhone 16" \
  --platform-version "26" \
  --html="$REPORT" --self-contained-html
```

The build names and simulator version above are examples. Use the exact build path and device/OS version available on your machine. The timestamp in each report filename keeps earlier reports instead of overwriting them.

### Run by tag

```bash
pytest tests/steps -m smoke
pytest tests/steps -m regression
```

`smoke` is intended as a short confidence check. `regression` covers the four listed user journeys; it is not a claim of complete product regression coverage.

### Override settings from the command line

```bash
pytest tests/steps --platform android \
  --device-name "Pixel_8_API_35" \
  --platform-version "15" \
  --app-path "$PWD/apps/my-android-build.apk" \
  --appium-url http://127.0.0.1:4723 \
  --html=reports/mobile-report.html --self-contained-html
```

Available CLI options are `--platform`, `--device-name`, `--platform-version`, `--app-path`, and `--appium-url`.

### Android startup troubleshooting

If Appium reports that `com.swaglabsmobileapp.SplashActivity` did not start, confirm the emulator is booted and that the APK launches outside Appium. Then collect startup evidence:

```bash
adb devices
adb -s <device-id> shell monkey -p com.swaglabsmobileapp 1
adb -s <device-id> logcat -d -t 500 > reports/android-launch-logcat.txt
```

Replace `<device-id>` with the identifier shown by `adb devices`. If the app closes, inspect logcat for a crash before changing locators or assertions.

## Running API tests

The API examples use JSONPlaceholder and require network access:

```bash
export API_BASE_URL=https://jsonplaceholder.typicode.com
REPORT="reports/api-$(date +%Y%m%d-%H%M%S).html"
pytest tests/api -m api --html="$REPORT" --self-contained-html
```

These examples are separate from the mobile UI suite. Replace the demo URL and assertions when a target API specification is available.

## Reports and failure artifacts

Each mobile run creates a standalone HTML report under `reports/`. The recommended commands use timestamps so reports from earlier runs remain available:

```text
reports/
├── android-20261014-153000.html
├── ios-20261014-154500.html
└── failures/
```

When the driver is responsive, failure diagnostics are saved under `reports/failures/`, including screenshots and page source. Android logcat output is collected when available. Diagnostic collection should not hide or convert a test failure into a pass.

To retain a fixed report filename instead, use `--html=reports/android-report.html` or `--html=reports/ios-report.html`. Be aware that a later run with the same filename will overwrite the earlier report.

## Reliability and trade-offs

- **Explicit waits:** page interactions use bounded waits rather than fixed sleeps.
- **No blind retries:** retries can hide product defects or make stateful flows less reliable. Classify failures first; retry only known transient infrastructure issues at the orchestration level.
- **Test isolation:** `noReset` is false by default so scenarios should not rely on previous test state.
- **Serial execution:** tests run serially by default. Parallel mobile runs should be introduced only when each worker has a dedicated device and isolated app state.
- **Platform-specific builds:** iOS Simulator builds and real-device IPA builds are not interchangeable.
- **Cloud execution:** hosted device-cloud authentication and provider-specific capabilities (such as Sauce Labs `sauce:options`) are not configured in this starter. Add them in `driver_factory.py` if needed.
- **Device verification:** test results should be considered verified only after running the suite on the target Android and iOS environments. No pre-generated passing report is included.

## AI use during the assessment

AI was used as a development and research aid for the initial framework structure, reviewing Appium configuration options, and identifying useful failure-diagnostic steps. The framework uses straightforward components so the choices can be reviewed and maintained. AI suggestions are not treated as test evidence; the test suite and reports must be checked on the target devices.

## Before submitting

Run the mobile scenarios on both Android and iOS, retain the resulting HTML reports, and update any device, OS, and Appium version details to match the environment actually used. Do not report a platform as passing until its run has completed successfully.
