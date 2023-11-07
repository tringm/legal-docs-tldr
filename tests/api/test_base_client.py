import aiohttp
import pytest
import requests

from src.data.api.client import BaseAPIClient, BaseAPIOperation

TEST_API_URL = "https://api.apis.guru"


@pytest.fixture
def client() -> BaseAPIClient:
    return BaseAPIClient(base_url=TEST_API_URL)


@pytest.fixture
def api_op() -> BaseAPIOperation:
    return BaseAPIOperation(path="/v2/metrics.json", method="get")


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


def test_call_api(client: BaseAPIClient, api_op: BaseAPIOperation) -> None:
    resp = client.call_api(api_op=api_op)
    assert resp.status_code == requests.codes["ok"]
    json_resp = resp.json()
    assert json_resp, "Non empty response"


@pytest.mark.asyncio
async def test_async_call_api(client: BaseAPIClient, api_op: BaseAPIOperation) -> None:
    async with aiohttp.ClientSession() as session, client.async_call_api(session=session, api_op=api_op) as resp:
        assert resp.status == requests.codes["ok"]
        json_resp = await resp.json()
        assert json_resp, "Non empty response"
