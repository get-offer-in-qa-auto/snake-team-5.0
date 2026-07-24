import allure

from src.main.api.database import DatabaseClient, DBRequest, create_database_client
from src.main.api.database.dao import BuildConfigurationDao, ProjectDao, UserDao
from src.main.api.models.create_user_response import CreateUserResponse
from src.main.api.models.project_response import ProjectResponse


class DatabaseSteps:
    def __init__(self, client: DatabaseClient | None = None):
        self.client = client or create_database_client()

    @staticmethod
    def _verify_active_entity(
        entity: ProjectDao | BuildConfigurationDao,
        *,
        expected_external_id: str,
        internal_id_prefix: str,
        entity_name: str,
    ) -> None:
        assert entity.delete_time is None, (
            f"{entity_name} {expected_external_id!r} is marked as deleted in the "
            f"database: delete_time={entity.delete_time}"
        )
        assert entity.external_id == expected_external_id, (
            f"{entity_name} external id mismatch: expected {expected_external_id!r}, "
            f"got {entity.external_id!r}"
        )
        assert entity.internal_id.startswith(internal_id_prefix), (
            f"{entity_name} {expected_external_id!r} has unexpected internal id "
            f"{entity.internal_id!r}; expected prefix {internal_id_prefix!r}"
        )
        assert entity.config_id, (
            f"{entity_name} {expected_external_id!r} has an empty config id"
        )

    def get_project_by_external_id(self, external_id: str) -> ProjectDao:
        with self.client.snapshot() as executor:
            mapping = executor.fetch_one(
                DBRequest.select(
                    "project_mapping", {"ext_id": external_id, "main": True}
                )
            )
            assert mapping is not None, (
                f"Project {external_id!r} was not found in PROJECT_MAPPING"
            )

            project = executor.fetch_one(
                DBRequest.select("project", {"int_id": mapping["INT_ID"]})
            )
            assert project is not None, (
                f"Project {external_id!r} has mapping {mapping['INT_ID']!r}, "
                "but no PROJECT row"
            )

        delete_time = project["DELETE_TIME"]
        return ProjectDao(
            internal_id=str(project["INT_ID"]),
            external_id=str(mapping["EXT_ID"]),
            config_id=str(project["CONFIG_ID"]),
            origin_project_id=project["ORIGIN_PROJECT_ID"],
            delete_time=int(delete_time) if delete_time is not None else None,
        )

    @allure.step("Verify project is persisted in TeamCity database")
    def verify_project_persisted(self, project_response: ProjectResponse) -> ProjectDao:
        project = self.get_project_by_external_id(project_response.id)
        self._verify_active_entity(
            project,
            expected_external_id=project_response.id,
            internal_id_prefix="project",
            entity_name="Project",
        )
        return project

    @allure.step("Verify project {external_id} is deleted in TeamCity database")
    def verify_project_deleted(self, external_id: str) -> ProjectDao:
        project = self.get_project_by_external_id(external_id)
        assert project.delete_time is not None, (
            f"Project {external_id!r} is still active in the database"
        )
        return project

    @allure.step("Verify project {external_id} was not created in TeamCity database")
    def verify_project_not_created(self, external_id: str) -> None:
        with self.client.snapshot() as executor:
            mapping = executor.fetch_one(
                DBRequest.select(
                    "project_mapping", {"ext_id": external_id, "main": True}
                )
            )
        assert mapping is None, (
            f"Project {external_id!r} should not exist in PROJECT_MAPPING, "
            f"but row was found: {mapping}"
        )

    def get_build_configuration_by_external_id(
        self, external_id: str
    ) -> BuildConfigurationDao:
        with self.client.snapshot() as executor:
            mapping = executor.fetch_one(
                DBRequest.select(
                    "build_type_mapping", {"ext_id": external_id, "main": True}
                )
            )
            assert mapping is not None, (
                f"Build configuration {external_id!r} was not found in "
                "BUILD_TYPE_MAPPING"
            )

            build_configuration = executor.fetch_one(
                DBRequest.select("build_type", {"int_id": mapping["INT_ID"]})
            )
            assert build_configuration is not None, (
                f"Build configuration {external_id!r} has mapping "
                f"{mapping['INT_ID']!r}, but no BUILD_TYPE row"
            )

        delete_time = build_configuration["DELETE_TIME"]
        return BuildConfigurationDao(
            internal_id=str(build_configuration["INT_ID"]),
            external_id=str(mapping["EXT_ID"]),
            config_id=str(build_configuration["CONFIG_ID"]),
            origin_project_id=build_configuration["ORIGIN_PROJECT_ID"],
            delete_time=int(delete_time) if delete_time is not None else None,
        )

    @allure.step(
        "Verify build configuration {external_id} is persisted in TeamCity database"
    )
    def verify_build_configuration_persisted(
        self, external_id: str
    ) -> BuildConfigurationDao:
        build_configuration = self.get_build_configuration_by_external_id(external_id)
        self._verify_active_entity(
            build_configuration,
            expected_external_id=external_id,
            internal_id_prefix="bt",
            entity_name="Build configuration",
        )
        return build_configuration

    @allure.step(
        "Verify build configuration {external_id} is deleted in TeamCity database"
    )
    def verify_build_configuration_deleted(
        self, external_id: str
    ) -> BuildConfigurationDao:
        build_configuration = self.get_build_configuration_by_external_id(external_id)
        assert build_configuration.delete_time is not None, (
            f"Build configuration {external_id!r} is still active in the database"
        )
        return build_configuration

    @allure.step(
        "Verify build configuration {external_id} was not created in TeamCity database"
    )
    def verify_build_configuration_not_created(self, external_id: str) -> None:
        with self.client.snapshot() as executor:
            mapping = executor.fetch_one(
                DBRequest.select(
                    "build_type_mapping", {"ext_id": external_id, "main": True}
                )
            )
        assert mapping is None, (
            f"Build configuration {external_id!r} should not exist in "
            f"BUILD_TYPE_MAPPING, but row was found: {mapping}"
        )

    def get_user_by_username(self, username: str) -> UserDao:
        with self.client.snapshot() as executor:
            user = executor.fetch_one(DBRequest.select("users", {"username": username}))
        assert user is not None, f"User {username!r} was not found in USERS"

        last_login_timestamp = user["LAST_LOGIN_TIMESTAMP"]
        return UserDao(
            id=int(user["ID"]),
            username=str(user["USERNAME"]),
            name=user["NAME"],
            email=user["EMAIL"],
            last_login_timestamp=(
                int(last_login_timestamp) if last_login_timestamp is not None else None
            ),
            algorithm=user["ALGORITHM"],
        )

    @allure.step("Verify user is persisted in TeamCity database")
    def verify_user_persisted(self, user_response: CreateUserResponse) -> UserDao:
        user = self.get_user_by_username(user_response.username)
        assert user.id == user_response.id
        assert user.username == user_response.username
        assert user.algorithm == "BCRYPT"
        return user

    @allure.step("Verify user {username} is deleted from TeamCity database")
    def verify_user_deleted(self, username: str) -> None:
        with self.client.snapshot() as executor:
            user = executor.fetch_one(DBRequest.select("users", {"username": username}))
        assert user is None, (
            f"User {username!r} should be deleted from USERS, but row was found: {user}"
        )

    @allure.step("Verify user {username} was not created in TeamCity database")
    def verify_user_not_created(self, username: str) -> None:
        with self.client.snapshot() as executor:
            user = executor.fetch_one(DBRequest.select("users", {"username": username}))
        assert user is None, (
            f"User {username!r} should not exist in USERS, but row was found: {user}"
        )
