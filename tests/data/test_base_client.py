from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
import requests
from aiohttp import ClientResponseError, ClientSession
from pytest_mock import MockFixture

from src.data.base_client import DEFAULT_TIMEOUT, BaseAPIClient, BaseAPIOperation

TEST_API_URL = "https://jsonplaceholder.typicode.com"
TEST_POST_ID = 1


class GetPostOp(BaseAPIOperation):
    method: str = "GET"
    path: str = "/posts"


GET_POSTS_OP = GetPostOp()
INVALID_API_OP = BaseAPIOperation(method="get", path="/invalid_path")


@pytest.fixture
def client() -> BaseAPIClient:
    return BaseAPIClient(base_url=TEST_API_URL)


@pytest_asyncio.fixture
async def async_session() -> AsyncIterator[ClientSession]:
    async with ClientSession() as sess:
        yield sess


@pytest.fixture
def default_get_posts_kwargs() -> dict:
    return {"timeout": DEFAULT_TIMEOUT, "method": GET_POSTS_OP.method, "url": TEST_API_URL + GET_POSTS_OP.path}


def validate_get_posts_resp(json_resp: list[dict]) -> None:
    assert json_resp, "Non empty response"
    assert isinstance(json_resp, list)
    assert all(field in json_resp[0] for field in ("id", "userId"))


def test_client_request(client: BaseAPIClient) -> None:
    resp = client.request(url=f"{client.base_url}{GET_POSTS_OP.path}", method="get")
    assert resp.status_code == requests.codes["ok"]
    validate_get_posts_resp(json_resp=resp.json())


def test_client_request_with_session(client: BaseAPIClient) -> None:
    with requests.Session() as session:
        resp = client.request(session=session, url=f"{client.base_url}{GET_POSTS_OP.path}", method="get")
        assert resp.status_code == requests.codes["ok"]
        validate_get_posts_resp(json_resp=resp.json())


def test_call_api(client: BaseAPIClient) -> None:
    resp = client.request(api_op=GET_POSTS_OP)
    assert resp.status_code == requests.codes["ok"]
    validate_get_posts_resp(json_resp=resp.json())


@pytest.mark.parametrize("raise_for_status", [True, False])
def test_call_api_fail(client: BaseAPIClient, raise_for_status: bool) -> None:
    if raise_for_status:
        with pytest.raises(requests.exceptions.HTTPError):
            client.request(api_op=INVALID_API_OP, raise_for_status=True)
    else:
        resp = client.request(api_op=INVALID_API_OP, raise_for_status=raise_for_status)
        assert resp.status_code == requests.codes["not_found"]


@pytest.mark.asyncio
async def test_async_call_api(client: BaseAPIClient, async_session: ClientSession) -> None:
    async with client.async_request(session=async_session, api_op=GET_POSTS_OP) as resp:
        assert resp.status == requests.codes["ok"]
        json_resp = await resp.json()
        validate_get_posts_resp(json_resp=json_resp)


@pytest.mark.asyncio
@pytest.mark.parametrize("raise_for_status", [True, False])
async def test_async_call_api_fail(client: BaseAPIClient, async_session: ClientSession, raise_for_status: bool) -> None:
    if raise_for_status:
        with pytest.raises(ClientResponseError):
            await client.async_request(session=async_session, api_op=INVALID_API_OP, raise_for_status=raise_for_status)
    else:
        async with client.async_request(
            session=async_session, api_op=INVALID_API_OP, raise_for_status=raise_for_status
        ) as resp:
            assert resp.status == requests.codes["not_found"]


@pytest.mark.parametrize(
    "api_op,exp_request_kwargs",
    [
        (GetPostOp(params={"id": 1}), {"params": {"id": 1}}),
        (GetPostOp(json={"id": 1}), {"json": {"id": 1}}),
        (GetPostOp(data=b'{"id": 1}'), {"data": b'{"id": 1}'}),
    ],
)
def test_api_op_as_req_kwargs(
    client: BaseAPIClient,
    default_get_posts_kwargs: dict,
    mocker: MockFixture,
    api_op: GetPostOp,
    exp_request_kwargs: dict,
) -> None:
    req_mock = mocker.patch("requests.request")
    client.request(api_op=api_op)
    req_mock.assert_called_once_with(**{**default_get_posts_kwargs, **exp_request_kwargs})
