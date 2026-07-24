import pytest

from src.main.api.constants.teamcity import TeamCityAgentLocator, TeamCityLocator


@pytest.mark.parametrize(
    ("locator_type", "raw_value", "expected"),
    [
        (TeamCityLocator.ID, 42, "id:42"),
        (TeamCityLocator.ID, "ProjectId", "id:ProjectId"),
        (TeamCityLocator.USERNAME, "test-user", "username:test-user"),
    ],
)
def test_locator_builds_prefixed_value(
    locator_type: TeamCityLocator,
    raw_value: int | str,
    expected: str,
):
    assert locator_type.build(raw_value) == expected


def test_locator_keeps_already_formatted_value():
    assert TeamCityLocator.ID.build("username:test-user") == "username:test-user"


@pytest.mark.parametrize(
    ("raw_user", "expected"),
    [
        (42, "id:42"),
        ("test-user", "username:test-user"),
        ("id:42", "id:42"),
        ("username:test-user", "username:test-user"),
    ],
)
def test_user_locator_selects_locator_type(raw_user: int | str, expected: str):
    assert TeamCityLocator.for_user(raw_user) == expected


def test_locator_matches_and_extracts_its_value():
    locator = "id:BuildConfigurationId"

    assert TeamCityLocator.ID.matches(locator)
    assert not TeamCityLocator.USERNAME.matches(locator)
    assert TeamCityLocator.ID.extract(locator) == "BuildConfigurationId"


def test_agent_locator_includes_all_authorization_states():
    assert (
        TeamCityAgentLocator.ALL_AUTHORIZATION_STATES
        == "authorized:any,defaultFilter:false"
    )
