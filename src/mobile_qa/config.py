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
    """Resolve local paths from the repo root; leave URLs/cloud storage IDs alone."""
    if app_path.startswith(("http://", "https://", "storage:")):
        return app_path
    path = Path(app_path).expanduser()
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    if not path.exists():
        raise FileNotFoundError(
            f"App build not found: {path}\n"
            "Download the appropriate build from https://github.com/saucelabs/sample-app-mobile/releases "
            "or set ANDROID_APP_PATH / IOS_APP_PATH."
        )
    return str(path.resolve())
