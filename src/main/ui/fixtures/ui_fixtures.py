from collections.abc import Iterator
from typing import Any

import pytest
from playwright.sync_api import BrowserContext, Page

from src.main.api.classes.session_storage import SessionStorage
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.ui.auth.session_client import UiAuthClient

_DISABLE_VIEW_TRANSITIONS_SCRIPT = """
window.addEventListener(
    "DOMContentLoaded",
    () => {
        const style = document.createElement("style");
        style.textContent = "@view-transition { navigation: none; }";
        document.head.append(style);
    },
    { once: true },
);
"""


@pytest.fixture(autouse=True)
def disable_ui_view_transitions(request: pytest.FixtureRequest) -> None:
    """Keep TeamCity page navigation paintable in headed UI test runs."""
    if request.node.get_closest_marker("ui") is None:
        return

    context: BrowserContext = request.getfixturevalue("context")
    context.add_init_script(_DISABLE_VIEW_TRANSITIONS_SCRIPT)


def _resolve_source(request: pytest.FixtureRequest, source: str) -> Any:
    parts = [part for part in source.split(".") if part]
    if not parts:
        raise ValueError("User session source cannot be empty")

    root = parts[0]
    callspec = getattr(request.node, "callspec", None)
    if callspec is not None and root in getattr(callspec, "params", {}):
        value = callspec.params[root]
    else:
        value = request.getfixturevalue(root)

    for attribute in parts[1:]:
        value = getattr(value, attribute)
    return value


def _materialize_user(value: Any) -> CreateUserRequest:
    if isinstance(value, CreateUserRequest):
        return value
    if callable(value):
        created_user = value()
        if isinstance(created_user, CreateUserRequest):
            return created_user
    raise TypeError(
        "user_session sources must resolve to CreateUserRequest or a user factory"
    )


@pytest.fixture(autouse=True)
def ui_session(request: pytest.FixtureRequest) -> Iterator[None]:
    """Apply marker-driven UI login without starting browsers for API tests."""
    admin_mark = request.node.get_closest_marker("admin_session")
    user_mark = request.node.get_closest_marker("user_session")
    if admin_mark is not None and user_mark is not None:
        raise ValueError("admin_session and user_session cannot be used together")
    if admin_mark is None and user_mark is None:
        yield
        return

    if admin_mark is not None:
        users = [request.getfixturevalue("admin_user_request")]
        auth_index = 0
    else:
        assert user_mark is not None
        if not user_mark.args:
            raise ValueError("user_session requires at least one fixture source")
        users = [
            _materialize_user(_resolve_source(request, str(source)))
            for source in user_mark.args
        ]
        auth_index = int(user_mark.kwargs.get("auth", 0))

    if auth_index < 0 or auth_index >= len(users):
        raise IndexError(
            f"Authenticated user index out of range: {auth_index}; total={len(users)}"
        )

    SessionStorage.clear()
    try:
        SessionStorage.add_users(users)
        page: Page = request.getfixturevalue("page")
        UiAuthClient().authenticate(page.context, SessionStorage.get_user(auth_index))
        yield
    finally:
        SessionStorage.clear()
