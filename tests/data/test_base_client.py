from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
import requests
from aiohttp import ClientResponseError, ClientSession

from src.data.base_client import BaseAPIClient, BaseAPIOperation

TEST_API_URL = "https://api.apis.guru"


@pytest.fixture
def client() -> BaseAPIClient:
    return BaseAPIClient(base_url=TEST_API_URL)


@pytest.fixture
def api_op() -> BaseAPIOperation:
    return BaseAPIOperation(path="/v2/metrics.json", method="get")


@pytest.fixture
def invalid_api_op() -> BaseAPIOperation:
    return BaseAPIOperation(path="/invalid_path", method="get")


@pytest_asyncio.fixture
async def async_session() -> AsyncIterator[ClientSession]:
    async with ClientSession() as sess:
        yield sess


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
    resp = client.request(api_op=api_op)
    assert resp.status_code == requests.codes["ok"]
    json_resp = resp.json()
    assert json_resp, "Non empty response"


@pytest.mark.parametrize("raise_for_status", [True, False])
def test_call_api_fail(client: BaseAPIClient, invalid_api_op: BaseAPIOperation, raise_for_status: bool) -> None:
    if raise_for_status:
        with pytest.raises(requests.exceptions.HTTPError):
            client.request(api_op=invalid_api_op, raise_for_status=True)
    else:
        resp = client.request(api_op=invalid_api_op, raise_for_status=raise_for_status)
        assert resp.status_code == requests.codes["not_found"]


@pytest.mark.asyncio
async def test_async_call_api(async_session: ClientSession, client: BaseAPIClient, api_op: BaseAPIOperation) -> None:
    async with client.async_request(session=async_session, api_op=api_op) as resp:
        assert resp.status == requests.codes["ok"]
        json_resp = await resp.json()
        assert json_resp, "Non empty response"


@pytest.mark.asyncio
@pytest.mark.parametrize("raise_for_status", [True, False])
async def test_async_call_api_fail(
    client: BaseAPIClient, async_session: ClientSession, invalid_api_op: BaseAPIOperation, raise_for_status: bool
) -> None:
    if raise_for_status:
        with pytest.raises(ClientResponseError):
            await client.async_request(session=async_session, api_op=invalid_api_op, raise_for_status=raise_for_status)
    else:
        async with client.async_request(
            session=async_session, api_op=invalid_api_op, raise_for_status=raise_for_status
        ) as resp:
            assert resp.status == requests.codes["not_found"]
