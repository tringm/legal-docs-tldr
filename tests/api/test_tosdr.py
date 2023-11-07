import pytest

from src.data.api.tosdr import Client, Service

TEST_SERVICE_ID = 222
TEST_SERVICE_NAME = "DuckDuckGo"


@pytest.fixture
def client() -> Client:
    return Client()


def test_get_service(client: Client) -> None:
    service = client.get_service(service_id=TEST_SERVICE_ID)
    assert isinstance(service, Service)
    assert service.name == TEST_SERVICE_NAME
