from pytest import mark
from treasurechest.utils.helpers import get_date_from_timestamp


@mark.parametrize(
    "ts,out", [(1000000000, "2001-09-09 03:46:40"), (0, "1970-01-01 01:00:00")]
)
def test_get_date_from_timestamp(ts: int, out: str):
    assert get_date_from_timestamp(ts) == out
