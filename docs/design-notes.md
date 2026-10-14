# Design notes

## Framework design

I kept the framework modular and focused on the required scenarios
rather than introducing unnecessary layers. The framework uses Python,
Appium, pytest, and pytest-bdd to support mobile UI automation on both
Android and iOS. Python keeps the test code readable, while pytest
provides fixtures, assertions, test selection, and reporting support.
BDD feature files describe the expected behaviour in plain language,
making the scenarios easier to understand and review.

## Page Object Model and separation of concerns

The framework follows the Page Object Model (POM). The login screen and
product list/navigation menu are represented by separate page objects
because these cover the main screens involved in the required flows.
Step definitions translate the BDD scenarios into page-object calls,
while page objects manage element identification, interactions, waits,
and screen-level behaviour.

This separation keeps test scenarios focused on business behaviour
instead of implementation details. If the application grows, additional
page objects can be introduced for the cart, checkout, or other screens
without expanding `InventoryPage` with unrelated responsibilities.

## Cross-platform support

Android and iOS have different accessibility hierarchies, locator
strategies, keyboard behaviour, and application capabilities. The
framework keeps platform-specific configuration and locator differences
separate from the test scenarios wherever possible. This allows the same
behavioural scenarios to be executed on both platforms without
duplicating the entire test suite.

Platform, device name, OS version, and application path are configurable
through the framework's configuration, environment variables, and
command-line options. This makes it easier to switch devices or
application builds without changing the test logic. Platform-specific
locator fallbacks are retained only where needed, with accessibility
identifiers preferred whenever available.

## Synchronisation and test reliability

Mobile UI interactions are asynchronous, so the framework uses explicit
waits to check that elements are available before interacting with them.
The locator helper tries a controlled list of candidate selectors within
a bounded wait rather than relying on fixed sleeps or a single selector
that may not work across platforms.

Text entry and navigation require particular care because a successful
tap or keyboard action does not necessarily mean the application reached
the expected state. The framework verifies the resulting state and
raises an assertion when the expected behaviour is not observed. Locator
fallbacks should be reviewed against the actual accessibility hierarchy
and kept only when they provide a clear benefit.

I have avoided automatic test-level retries because they can hide
intermittent failures without explaining their cause. Recovery is
appropriate for specific, well-understood interactions, but the final
assertion must still verify the expected outcome.

## Test coverage and tagging

The BDD scenarios cover successful login, rejection of invalid
credentials, logout, and adding a product to the cart. These flows
exercise authentication, validation, navigation, session handling, and a
basic product interaction on both platforms.

Smoke and regression tags allow the suite to be selected according to
the purpose of a run. Smoke tests provide a focused check of essential
functionality, while regression execution provides broader coverage. The
same scenarios and assertions should remain meaningful across Android
and iOS; platform-specific differences should be handled by the
framework rather than by weakening the expected behaviour.

## Configuration and execution

Driver creation and configuration are kept separate from the scenarios.
This avoids hard-coding device details into individual tests and makes
local execution easier to configure. The framework can be run against an
Android emulator or an iOS Simulator by supplying the appropriate
platform and device settings.

For repeatable execution, the required application build must exist at
the configured path, and the corresponding simulator or emulator and
Appium server must be available. Keeping these prerequisites explicit
makes setup failures easier to distinguish from application or test
failures.

## Failure handling and reporting

When a test fails, the framework attempts to capture a screenshot and
the page source to help identify the screen and accessibility elements
available at the time of failure. Artifact collection is best effort: a
secondary error while saving diagnostics should not replace the original
test or driver failure.

HTML reports are generated for test runs, and timestamped filenames can
be used to retain reports from separate Android and iOS executions.
Keeping the reports separate makes it easier to compare platform
behaviour and investigate regressions. Logs, screenshots, and
page-source artifacts provide additional context when an assertion
fails.

## API testing

API testing is kept separate from the mobile UI scenarios so that
service-level checks and UI behaviour can be investigated independently.
API tests can help distinguish a service or response problem from an
issue in the mobile interface. The README documents the relevant setup
and execution commands so that API and UI checks can be run as
appropriate.

## AI-assisted development

I used AI as a development aid to explore framework structure, review
implementation choices, improve documentation, and investigate test
failures. When failures occurred, I used the reported stack traces and
execution logs to identify likely causes and guide code changes.

AI suggestions were treated as hypotheses to verify rather than proof
that a fix worked. In particular, changes to locators, synchronisation,
and logout handling need to be validated against the actual Android and
iOS accessibility hierarchies. I also used AI to improve readability and
reduce unnecessary complexity while keeping the framework aligned with
the assessment requirements. No proprietary or confidential employer
code or data should be included in the submission.

## Trade-offs and future improvements

The current framework is intentionally small enough to understand and
maintain without adding abstractions that the required scenarios do not
yet need. The main trade-off is that cross-platform applications may
expose different accessibility elements, so some platform-specific
handling remains necessary.

Further improvements could include expanding page-object coverage as
more screens are added, validating locator strategies against additional
app versions and device sizes, and integrating execution into a CI
pipeline with retained reports and failure artifacts. These improvements
should build on reliable assertions and clear diagnostics rather than
relying on retries to make the test results appear stable.
