from urllib.parse import urlencode


class TeamCityRoutes:
    NEW_RUNNER_ID = "__NEW_RUNNER__"

    @classmethod
    def create_build_step(
        cls,
        build_configuration_id: str,
    ) -> str:
        query = urlencode(
            {
                "id": f"buildType:{build_configuration_id}",
                "runnerId": cls.NEW_RUNNER_ID,
            }
        )

        return f"/admin/editRunType.html?{query}"
