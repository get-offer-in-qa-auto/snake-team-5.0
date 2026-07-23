from urllib.parse import urlsplit, urlunsplit

from src.main.api.configs.config import Config


def teamcity_ui_base_url() -> str:
    """Return the TeamCity origin without a page path or trailing slash."""
    configured_url = (
        Config.get("TEAMCITY_UI_BASE_URL")
        or Config.get("TEAMCITY_URL")
        or Config.get("TEAMCITY_BASE_URL")
        or Config.get("server")
    )
    if not configured_url:
        raise ValueError("TeamCity UI base URL is not configured")

    parts = urlsplit(str(configured_url))
    if not parts.scheme or not parts.netloc:
        raise ValueError(f"TeamCity UI base URL is invalid: {configured_url!r}")
    return urlunsplit((parts.scheme, parts.netloc, "", "", "")).rstrip("/")
