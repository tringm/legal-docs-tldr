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
