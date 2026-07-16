from src.main.api.database import DatabaseClient, create_database_client
from src.main.api.database.dao import ProjectDao


class DatabaseSteps:
    def __init__(self, client: DatabaseClient | None = None):
        self.client = client or create_database_client()

    def get_project_by_external_id(self, external_id: str) -> ProjectDao:
        with self.client.snapshot() as database:
            mapping = database.fetch_one(
                "project_mapping", {"ext_id": external_id, "main": True}
            )
            assert mapping is not None, (
                f"Project {external_id!r} was not found in PROJECT_MAPPING"
            )

            project = database.fetch_one("project", {"int_id": mapping["INT_ID"]})
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

    def verify_project_persisted(self, external_id: str) -> ProjectDao:
        project = self.get_project_by_external_id(external_id)
        assert project.delete_time is None, (
            f"Project {external_id!r} is marked as deleted in the database: "
            f"delete_time={project.delete_time}"
        )
        return project
