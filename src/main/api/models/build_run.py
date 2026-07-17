from src.main.api.models.base_model import BaseModel


class BuildRunResponse(BaseModel):
    id: int
    state: str
    status: str | None = None
    buildTypeId: str | None = None
    statusText: str | None = None
