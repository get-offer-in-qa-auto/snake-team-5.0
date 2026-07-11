from typing import Annotated

from src.main.api.generators.generating_rule import GeneratingRule
from src.main.api.models.base_model import BaseModel


class CreateBuildConfigurationRequest(BaseModel):
    id: Annotated[str, GeneratingRule(regex=r"^AutotestApiBuild[A-Za-z0-9]{8}$")]
    name: Annotated[str, GeneratingRule(regex=r"^[A-Za-z]{4}[0-9]{2} [A-Za-z]{4} [0-9]{2}$")]
