import pytest

from src.main.api.generators.random_model_generator import RandomModelGenerator
from src.main.api.models.build_configuration_request import BuildConfigurationRequest


@pytest.fixture(scope="function")
def build_configuration_request() -> BuildConfigurationRequest:
    generated_build_configuration = RandomModelGenerator.generate(BuildConfigurationRequest)
    return BuildConfigurationRequest(
        id=generated_build_configuration.id,
        name=generated_build_configuration.id,
    )
