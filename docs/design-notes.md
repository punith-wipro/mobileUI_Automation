# Design notes

I kept the first version deliberately small. There are only two screen objects because the required flows use the login screen and the product list/menu. A larger app would get separate objects for the cart and checkout screens rather than adding more unrelated methods to `InventoryPage`.

The feature file describes user-visible behaviour. Step definitions translate those sentences into page-object calls, and page objects own the actions and the waits. Configuration and driver creation are separate, which makes it possible to change the device without editing the scenarios.

The locator helper tries a short list of candidates during one explicit wait. That is more forgiving than a single hard-coded selector, but it is not a substitute for checking the real hierarchy. Accessibility identifiers should remain the first choice, and fallbacks should be pruned when we confirm what a given app build exposes.

On failure, artifact collection is best effort. I would rather retain the original assertion/driver error than fail a second time while trying to save a screenshot. I did not add automatic retries at the test level because retries can make a stateful UI failure look intermittent without explaining it.
