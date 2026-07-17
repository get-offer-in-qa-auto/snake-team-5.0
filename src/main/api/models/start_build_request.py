from src.main.api.models.base_model import BaseModel


class BuildTypeReference(BaseModel):
    id: str


class BuildProperty(BaseModel):
    name: str
    value: str


class BuildProperties(BaseModel):
    property: list[BuildProperty]


class StartBuildRequest(BaseModel):
    buildType: BuildTypeReference
    properties: BuildProperties | None = None


class BuildCancelRequest(BaseModel):
    comment: str
    readdIntoQueue: bool = False
