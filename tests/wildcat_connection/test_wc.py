import pytest
from . import get_test_cases, invalid_ranks_test_cases
from wildcat_connection import WildcatConnectionCSV
from wildcat_connection.utils import ParsingException


@pytest.mark.parametrize("test_case", [get_test_cases()[-1]])
def test_ballot_format(test_case):
    wc_csv = WildcatConnectionCSV(test_case.filepath)
    for key in test_case.ballot_format.keys():
        assert wc_csv.question_formatted_ballots[key].votes == test_case.ballot_format[key].votes

@pytest.mark.parametrize("test_case", get_test_cases())
def test_spoilt_ballots(test_case):
    wc_csv = WildcatConnectionCSV(test_case.filepath)
    assert wc_csv.question_spoilt_ballots == test_case.spoilt_ballots


def test_duplicate_questions(duplicate_question_test_case):
    with pytest.raises(ParsingException):
        WildcatConnectionCSV(duplicate_question_test_case.filepath)


@pytest.mark.parametrize("test_case", invalid_ranks_test_cases())
def test_invalid_ranks(test_case):
    with pytest.raises(ParsingException):
        WildcatConnectionCSV(test_case.filepath)
