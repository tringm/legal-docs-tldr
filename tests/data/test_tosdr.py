import pytest
from pytest_mock import MockFixture

from src.data.tosdr import Client, Service

TEST_SERVICE_ID = 222
TEST_SERVICE_NAME = "DuckDuckGo"


@pytest.fixture
def client() -> Client:
    return Client()


def test_get_service(client: Client) -> None:
    service = client.get_service(service_id=TEST_SERVICE_ID)
    assert isinstance(service, Service)
    assert service.name == TEST_SERVICE_NAME


def test_get_all_services(client: Client, mocker: MockFixture) -> None:
    total_page_count_mock = mocker.patch(
        target="src.data.tosdr.client.GetServicePageResponse.total_page_count", new_callable=mocker.PropertyMock
    )
    total_page_count_mock.return_value = 2
    services = client.get_all_services()

    page_size = 100
    assert len(services) == page_size * 2
    assert all(isinstance(serv, Service) for serv in services)
