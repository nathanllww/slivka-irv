import pytest
from irv import IRVElection
from irv.ballots import RankedChoiceBallots


def test_validate_ranked_choice_ballots_correct():
    ballot_list = [
        ["Norm", "Normie", "Norman"],
        ["Norm", "Normie"],
        ["Norman", "Norm", "Normie"]
    ]
    ballot = RankedChoiceBallots(ballot_list)
    assert ballot.votes == ballot_list


@pytest.mark.parametrize(
    "bad_ballot",
    [
        ["Normie", 1],
        [1, 3, 45, 6, 6]
    ]
)
def test_validate_ranked_choice_ballots_not_string(bad_ballot):
    ballot_list = [
        ["Norm", "Normie"],
        ["Norm", "Normie"],
        ["Norman", "Norm", "Normie"],
        bad_ballot
    ]
    with pytest.raises(ValueError):
        ballot = RankedChoiceBallots(ballot_list)


@pytest.mark.parametrize("test_array,actual_winner", [
    ([["winner", "loser"]], "winner"),
    (
        [
            ["winner", "loser"],
            ["winner", "loser"]
        ],
        "winner"
    )
])
def test_winner_keep_exhausted_ballots_no_ties(test_array, actual_winner):
    print(test_array)
    print(actual_winner)
    ballot = RankedChoiceBallots(test_array)
    irv_election = IRVElection(ballot, log_to_stderr=True,
                               remove_exhausted_ballots=False, permute=True)
    winner, _ = irv_election.run()
    assert winner == actual_winner