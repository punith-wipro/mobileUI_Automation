# Mobile UI Automation — Appium + Python

This is a small, practical framework for exercising the Sauce Labs sample mobile app on Android and iOS. I picked the sample app because both platforms have the same core login and shopping flows, so the code can show cross-platform design without spending the assessment building an app first.

The focus is on keeping tests readable and making failures useful to investigate. The scenarios are written in Gherkin, the page objects own UI interactions, and platform settings live outside the test code.

## What is covered

- Successful login
- Rejected login with invalid credentials
- Logout
- Add a product to the cart
- Two small API smoke tests, kept separate from mobile tests

The mobile scenarios carry `@smoke` and/or `@regression` tags. API checks use `@api`.

## Framework choices

- **Python + pytest**: familiar test tooling, fixtures for setup/teardown, and straightforward reporting.
- **Appium Python Client**: one WebDriver API for Android's UiAutomator2 and iOS's XCUITest.
- **pytest-bdd**: gives the four user journeys a readable feature file while retaining pytest fixtures and tags.
- **Page Object Model**: locators and screen actions stay with the page they belong to; step definitions describe the behaviour, not the mechanics.
- **JSON config + environment overrides**: the same code can run on different devices without editing Python files.

I prefer accessibility IDs first. They are normally more resilient than XPath and can be shared across platforms when the app exposes the same accessibility identifier. A small fallback list is kept for the sample app's platform differences. If a selector still does not match a new build, inspect the UI hierarchy with Appium Inspector and update the locator in one place rather than adding sleeps or XPath to a test step.

## Prerequisites

1. Python 3.10 or newer.
2. Node.js and Appium 2.
3. An Android emulator/device **or** an iOS simulator. iOS simulator tests require macOS and Xcode; they cannot run on Windows/Linux.
4. The matching Appium driver:

   ```bash
   npm install -g appium
   appium driver install uiautomator2
   # On macOS when running iOS:
   appium driver install xcuitest
   ```

5. The Sauce Labs sample app build for the platform under test. Download the simulator/device-appropriate build from the [sample app releases](https://github.com/saucelabs/sample-app-mobile/releases) and place it in `apps/` (or point the configuration at wherever you saved it).

   - Android: use the `.apk` build.
   - iOS Simulator: use the simulator `.app` archive, not a real-device `.ipa` build. Real-device iOS signing is a separate setup.

   The upstream sample app repository is archived, but its release builds remain useful for this exercise.

## Install Python dependencies

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate           # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Copy `.env.example` to `.env` if you want to use environment variables. The framework loads `.env` automatically. Environment variables override `config/config.json` values.

## Run the mobile tests

Start the emulator/simulator, then start Appium in a separate terminal:

```bash
appium
```

Update `config/config.json` to use the build path and device name available on your machine, or override them from the shell.

### Android

```bash
export MOBILE_PLATFORM=android
export ANDROID_APP_PATH="$PWD/apps/Android.SauceLabs.Mobile.Sample.app.2.7.1.apk"
pytest tests/steps -m "smoke or regression" --html=reports/android-report.html --self-contained-html
```

If Appium reports that `com.swaglabsmobileapp.SplashActivity` never started, first confirm that the emulator is booted and the APK can launch outside Appium. The Android driver configuration allows the app to transition from its splash activity and gives installation/startup commands a bounded timeout; it does not suppress a failed session or turn a failed scenario into a pass. To capture launch/crash evidence, run:

```bash
adb devices
adb -s <device-id> shell monkey -p com.swaglabsmobileapp 1
adb -s <device-id> logcat -d -t 500 > reports/android-launch-logcat.txt
```

Replace `<device-id>` with the device identifier shown by `adb devices`. If the app still closes, inspect the logcat crash before changing locators or weakening assertions.

### iOS Simulator (macOS only)

```bash
export MOBILE_PLATFORM=ios
export IOS_APP_PATH="$PWD/apps/iOS.Simulator.SauceLabs.Mobile.Sample.app.2.7.1.app"
export DEVICE_NAME="iPhone 16"
pytest tests/steps -m "smoke or regression" --html=reports/ios-report.html --self-contained-html
```

The build file names above are examples; use the exact names of the downloaded release assets.

The iOS page interactions now wait for visible, enabled elements, and text entry is verified before the login action proceeds. This addresses the observed partial username entry (`sndard_user`) and prevents taps on hidden menu items.

You can override settings without changing the config file:

```bash
pytest tests/steps --platform android \
  --device-name "Pixel_8_API_35" \
  --platform-version "15" \
  --app-path "$PWD/apps/my-android-build.apk" \
  --appium-url http://127.0.0.1:4723 \
  --html=reports/mobile-report.html --self-contained-html
```

The available CLI switches are `--platform`, `--device-name`, `--platform-version`, `--app-path`, and `--appium-url`. Environment variables are `MOBILE_PLATFORM`, `DEVICE_NAME`, `PLATFORM_VERSION`, `ANDROID_APP_PATH`, `IOS_APP_PATH`, and `APPIUM_SERVER_URL`.

### Run by tag

```bash
pytest tests/steps -m smoke
pytest tests/steps -m regression
```

`smoke` is intended for a short confidence check after a build; `regression` covers all four listed user journeys. These tags are not a claim that this is a complete product regression suite.

## Run the API tests

The brief did not define a product API, so I added two independent examples against JSONPlaceholder. They demonstrate separate API execution and configuration; replace the base URL and assertions with the target service if an API spec is supplied.

```bash
export API_BASE_URL=https://jsonplaceholder.typicode.com
pytest tests/api -m api --html=reports/api-report.html --self-contained-html
```

These tests need network access. The POST endpoint is a demo endpoint and does not persist data.

## Configuration

`config/config.json` contains platform defaults, Appium URL, device name, platform version, and app path. The selection order is:

1. pytest command-line option
2. environment variable / `.env`
3. `config/config.json`

No device-specific data is embedded in a feature file. A remote Appium URL can be supplied as well. Provider-specific cloud authentication/capabilities (for example, Sauce Labs credentials and `sauce:options`) are not wired into this starter; add those in `driver_factory.py` if you choose a hosted device cloud.

## Project layout

```text
config/config.json              Device and app defaults
features/authentication.feature Gherkin scenarios and tags
src/mobile_qa/config.py          Config loading and override rules
src/mobile_qa/driver_factory.py  Android/iOS capability setup
src/mobile_qa/pages/              Base page and screen objects
 tests/steps/                     BDD step definitions and pytest fixtures
 tests/api/                       API smoke tests
reports/                          Generated reports and failure artifacts
apps/                             Put downloaded app builds here (not committed)
```

On a failed mobile test, the fixture attempts to save a screenshot, the current page source, and (on Android, when available) recent logcat output under `reports/failures/`. The test still fails normally if those diagnostics cannot be collected; artifact collection should not hide the original failure.

## Reliability and known trade-offs

- **No fixed sleeps in page actions.** Interactions use explicit waits with a bounded timeout.
- **Avoid blind retries.** Retrying a failed UI action can hide a real product issue or make a stateful flow worse. I would first classify the failure (app defect, environment, locator, timing) and only retry at the orchestration layer for a known transient infrastructure failure.
- **Fresh state per scenario.** `noReset` is false by default so one test should not depend on another. If the app keeps state despite that setting, add a documented reset step for that app/version.
- **Stable selectors first.** Accessibility IDs are preferred. The fallback selectors are deliberately small; if the app changes, confirm the current UI hierarchy instead of growing a long list of guesses.
- **Use the correct app build for the target.** An iOS Simulator `.app` build is different from a real-device `.ipa` build; use the artifact intended for the simulator or device you are running.
- **Tests are serial by default.** Parallel mobile sessions need unique devices and isolated app state; I would only enable them once the CI device allocation is reliable.
- **API checks are examples.** They are intentionally decoupled from the mobile suite and do not pretend to validate a backend for which no specification was provided.

## Failure report and sample output

Run commands above to generate an HTML report from the actual test run. Failed mobile scenarios create artifacts in `reports/failures/` when the driver still responds. No pre-generated passing report is included. HTML reports should be generated from your own test execution so their results reflect the device run.

I have not marked the mobile tests as device-verified in this package: running them requires a configured Appium server, a downloaded app build, and a matching emulator/simulator. The code can be syntax-checked without a device, but selector and end-to-end verification should be done on both platforms before treating the suite as green.

## AI use during the assessment

AI was used as a coding and research aid for the initial scaffold, checking current Appium configuration conventions, and suggesting failure cases worth documenting. The framework choices were kept intentionally plain so each layer is easy to explain and change. AI suggestions are not treated as test evidence: device execution, selector verification, and review of the generated report still need to happen on the target setup. No application secrets or personal credentials are required by this framework.

## Before submitting

After running on your machine, add a real HTML report or a couple of screenshots from `reports/failures/` only if useful, and update the README with the device/OS/Appium versions actually used. Do not claim Android or iOS passed until each has been run.
