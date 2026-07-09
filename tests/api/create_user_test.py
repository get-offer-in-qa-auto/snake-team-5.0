import pytest

from src.main.api.classes.api_manager import ApiManager


@pytest.mark.api
class TestCreateUser:
    @pytest.mark.usefixtures('api_manager')
    @pytest.mark.debug
    def test_get_all_users(self, api_manager: ApiManager):
        pass