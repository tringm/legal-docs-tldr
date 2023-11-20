import asyncio

import pytest

from src.data.tosdr import CasePoint, EditSiteClient

TEST_CASE_ID = 175
EXPECTED_CASE_POINTS_COUNT = 144


@pytest.fixture
def client() -> EditSiteClient:
    return EditSiteClient()


def test_get_case_points(client: EditSiteClient) -> None:
    case_points = list(client.get_case_points(case_id=TEST_CASE_ID))
    assert (
        len(case_points) >= EXPECTED_CASE_POINTS_COUNT
    ), f"Expected return at least {EXPECTED_CASE_POINTS_COUNT} case points"
    assert all(isinstance(point, CasePoint) for point in case_points), "Expected return all CasePoint models"
    assert all(
        point.case_id == TEST_CASE_ID for point in case_points
    ), f"Expected all has correct case_id {TEST_CASE_ID}"


def test_get_multiple_case_points(client: EditSiteClient) -> None:
    case_ids = [173, 174, 175]
    case_points = asyncio.run(client.async_get_multiple_case_points(case_ids=case_ids))
    assert all(isinstance(cp, CasePoint) for cp in case_points), "Expected all returned are CasePoint models"
    for c_id in case_ids:
        assert any(cp.case_id == c_id for cp in case_points), f"Expected at at least one CasePoint with case_id {c_id}"
