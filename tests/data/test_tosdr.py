import pytest
from pytest_mock import MockFixture

from src.data.tosdr import Client, Service, ServiceMetadata

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
        target="src.data.tosdr.client.GetServiceMetadataPageResponse.total_page_count", new_callable=mocker.PropertyMock
    )
    mock_page_count = 2
    total_page_count_mock.return_value = mock_page_count
    services_metadata = client.get_all_services_metadata()

    page_size = 100
    expected_service_count = page_size * mock_page_count
    assert len(services_metadata) == expected_service_count, f"Expected return {expected_service_count} services"
    assert all(
        isinstance(serv, ServiceMetadata) for serv in services_metadata
    ), "Expected all objects are Service model"
    assert len({ser.id for ser in services_metadata}) == expected_service_count, "Expected all services id are unique"
