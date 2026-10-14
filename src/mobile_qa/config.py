"""Load mobile settings from JSON, with CLI and environment overrides."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_FILE = PROJECT_ROOT / "config" / "config.json"
load_dotenv(PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class MobileSettings:
    platform: str
    server_url: str
    device_name: str
    platform_version: str
    automation_name: str
    app_path: str
    timeout_seconds: int = 12
    no_reset: bool = False


def _read_config() -> dict[str, Any]:
    with CONFIG_FILE.open(encoding="utf-8") as config_file:
        return json.load(config_file)


def _value(cli_value: str | None, env_name: str, fallback: Any) -> Any:
    """Prefer a CLI value, then an environment variable, then the config value."""
    if cli_value not in (None, ""):
        return cli_value
    env_value = os.getenv(env_name)
    return env_value if env_value not in (None, "") else fallback


def load_settings(pytest_config: Any) -> MobileSettings:
    config = _read_config()
    platform = str(
        _value(pytest_config.getoption("--platform"), "MOBILE_PLATFORM", config["platform"])
    ).lower()
    if platform not in {"android", "ios"}:
        raise ValueError(f"Unsupported platform '{platform}'. Use 'android' or 'ios'.")

    device_defaults = config["devices"][platform]
    app_env = "ANDROID_APP_PATH" if platform == "android" else "IOS_APP_PATH"
    app_path = _value(
        pytest_config.getoption("--app-path"), app_env, device_defaults["app_path"]
    )

    return MobileSettings(
        platform=platform,
        server_url=str(
            _value(pytest_config.getoption("--appium-url"), "APPIUM_SERVER_URL", config["server_url"])
        ),
        device_name=str(
            _value(pytest_config.getoption("--device-name"), "DEVICE_NAME", device_defaults["device_name"])
        ),
        platform_version=str(
            _value(pytest_config.getoption("--platform-version"), "PLATFORM_VERSION", device_defaults["platform_version"])
        ),
        automation_name=device_defaults["automation_name"],
        app_path=str(app_path),
        timeout_seconds=int(os.getenv("MOBILE_TIMEOUT_SECONDS", config.get("timeout_seconds", 12))),
        no_reset=os.getenv("MOBILE_NO_RESET", str(config.get("no_reset", False))).lower() == "true",
    )


def resolve_app_path(app_path: str) -> str:
    """Resolve a local app build, accepting either an iOS .app bundle or its ZIP archive.

    App binaries are intentionally not tracked by Git, so fail with an actionable message
    when the selected build has not been downloaded locally.
    """
    if app_path.startswith(("http://", "https://", "storage:")):
        return app_path

    path = Path(app_path).expanduser()
    if not path.is_absolute():
        path = PROJECT_ROOT / path

    candidates = [path]
    # Release downloads may be an archived .app bundle while local setup may use the
    # extracted .app directory. Resolve either form without requiring config edits.
    if path.name.endswith(".app"):
        candidates.append(path.with_name(path.name + ".zip"))
        candidates.append(path.with_suffix(".zip"))
    elif path.name.endswith(".app.zip"):
        candidates.append(path.with_name(path.name[:-4]))
    elif path.suffix == ".zip" and ".app" in path.name:
        candidates.append(path.with_suffix(""))

    for candidate in candidates:
        if candidate.exists():
            return str(candidate.resolve())

    checked = "\n".join(f"  - {candidate}" for candidate in candidates)
    raise FileNotFoundError(
        f"App build not found. Checked:\n{checked}\n"
        "Download the simulator-compatible iOS .app ZIP or Android .apk from "
        "https://github.com/saucelabs/sample-app-mobile/releases and place it in apps/, "
        "or set IOS_APP_PATH / ANDROID_APP_PATH to the exact local path. "
        "For iOS Simulator, do not use a real-device .ipa build."
    )
