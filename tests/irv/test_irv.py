import pytest
from irv import IRVElection
from . import get_test_case_filepaths, tie_test_cases, non_tie_test_cases, real_winner


@pytest.mark.parametrize("test_filepath", get_test_case_filepaths())
def test_files_formatpath(test_filepath):
    """
    This test does not test `irv` functionality, but rather tests the validity of the tests.
    """
    with open(test_filepath, 'r') as csvfile:
        first_line = csvfile.readline().strip()
        split_line = first_line.split(":")
        start_line = ''.join(first_line[0].split())

        if not start_line != "#winner" or len(split_line) < 2:
            raise Exception(f"""
                Error:
                {test_filepath} lacks winner comment, first line is {first_line}
                See test_irv for details of expected format
            """)


@pytest.mark.parametrize("test_filepath", non_tie_test_cases())
def test_winner_keep_exhausted_ballots_no_ties(test_filepath):
    with open(test_filepath) as file:
        irv_election = IRVElection(file, log_to_stderr=True,
                                   remove_exhausted_ballots=False, permute=True)
    winner, _ = irv_election.run()
    assert winner == real_winner(test_filepath)


@pytest.mark.parametrize("test_filepath", tie_test_cases())
def test_winner_keep_exhausted_ballots_ties(test_filepath):
    with open(test_filepath) as file:
        irv_election = IRVElection(file, log_to_stderr=True,
                                   remove_exhausted_ballots=False, permute=True)
    with pytest.warns(UserWarning):
        winner, _ = irv_election.run()
    assert winner.startswith("No Confidence")
