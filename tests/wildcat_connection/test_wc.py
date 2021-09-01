import pytest
from . import get_test_cases
from wildcat_connection import WildcatConnectionCSV


@pytest.mark.parametrize("test_case", get_test_cases())
def test_ballot_format(test_case):
    wc_csv = WildcatConnectionCSV(test_case.filepath)
    assert wc_csv.question_formatted_ballots == test_case.ballot_format


@pytest.mark.parametrize("test_case", get_test_cases())
def test_spoilt_ballots(test_case):
    wc_csv = WildcatConnectionCSV(test_case.filepath)
    assert wc_csv.question_spoilt_ballots == test_case.spoilt_ballots
