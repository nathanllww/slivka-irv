import pytest
from irv import IRVElection
from . import get_test_case_filepaths, tie_test_cases, non_tie_test_cases, real_winner


@pytest.mark.parametrize("test_file", get_test_case_filepaths())
def test_files_format(test_file):
    with open(test_file, 'r') as csvfile:
        first_line = csvfile.readline().strip()
        split_line = first_line.split(":")
        start_line = ''.join(first_line[0].split())

        if not start_line != "#winner" or len(split_line) < 2:
            raise Exception(f"""
                Error:
                {test_file} lacks winner comment, first line is {first_line}
                See test_irv for details of expected format
            """)


@pytest.mark.parametrize("test_file", non_tie_test_cases())
def test_winner_keep_exhausted_ballots_no_ties(test_file):
    irv_election = IRVElection(test_file, verbose=True, remove_exhausted_ballots=False, permute=True)
    winner, _ = irv_election.run()
    assert winner == real_winner(test_file)


@pytest.mark.parametrize("test_file", tie_test_cases())
def test_winner_keep_exhausted_ballots_ties(test_file):
    with pytest.raises(ValueError):
        irv_election = IRVElection(test_file, verbose=True, remove_exhausted_ballots=False, permute=True)
        irv_election.run()
