import pytest
import requests

from src.data.api.client import BaseAPIClient, BaseAPIOperation

TEST_API_URL = "https://api.apis.guru"


@pytest.fixture
def client() -> BaseAPIClient:
    return BaseAPIClient(base_url=TEST_API_URL)


def test_client_request(client: BaseAPIClient) -> None:
    resp = client.request(url=f"{client.base_url}/v2/metrics.json", method="get")
    assert resp.status_code == requests.codes["ok"]
    json_resp = resp.json()
    assert json_resp, "Non empty response"


def test_client_request_with_session(client: BaseAPIClient) -> None:
    with requests.Session() as session:
        resp = client.request(session=session, url=f"{client.base_url}/v2/metrics.json", method="get")
        assert resp.status_code == requests.codes["ok"]
        json_resp = resp.json()
        assert json_resp, "Non empty response"


def test_call_api(client: BaseAPIClient) -> None:
    op = BaseAPIOperation(path="/v2/metrics.json", method="get")
    resp = client.call_api(api_op=op)
    assert resp.status_code == requests.codes["ok"]
    json_resp = resp.json()
    assert json_resp, "Non empty response"
