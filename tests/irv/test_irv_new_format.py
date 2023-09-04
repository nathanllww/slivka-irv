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
                               remove_exhausted_ballots=False)
    winner, _ = irv_election.run()
    assert winner == actual_winner

@pytest.mark.parametrize("array_with_empty_ballots,no_confidence", [
    ([["Norm"]], "No Confidence"),
    (
        [
            ["Norm"],
            [],
            [],
        ],
        "No Confidence"
    )
])

def test_empty_ballots_are_no_confidence(array_with_empty_ballots, no_confidence):
    ballot_list = [
        ["Norm"],
        [],
        [],
    ]
    ballot = RankedChoiceBallots(ballot_list)
    irv_election = IRVElection(ballot, log_to_stderr=True,
                               remove_exhausted_ballots=False)
    winner, _ = irv_election.run()
    assert winner == no_confidence


@pytest.mark.parametrize("test_array_elim,winner_after_elim", [
    # ([["winner", "loser1", "loser2"]], "winner"),
    (
        [
            ["winner", "loser1"],
            ["winner", "loser1", "loser2"],
            ["loser2", "winner", "loser1"],
            ["loser2", "loser1", "winner"],
            ["loser2", "winner", "loser1"],
            ["loser1", "winner", "loser2"],
            ["loser1", "winner", "loser2"]
        ],
        "winner"
    )
])


def test_candidates_eliminated(test_array_elim, winner_after_elim):
    print(test_array_elim)
    print(winner_after_elim)
    ballot = RankedChoiceBallots(test_array_elim)
    irv_election = IRVElection(ballot, log_to_stderr=True,
                               remove_exhausted_ballots=False)
    winner, _ = irv_election.run()
    assert winner == winner_after_elim


def test_candidate_ranking():
    ballot_list = [
        ["Norm", "Normie", "Norman"],
        ["Norm", "Normie"],
        ["Norman", "Norm", "Normie"]
    ]
    ballot = RankedChoiceBallots(ballot_list)
    assert ballot.get_appearances_in_rank("Normie", 3) == 1
    assert ballot.get_appearances_in_rank("Norm", 1) == 2
    assert ballot.get_appearances_in_rank("Norman", 2) == 0
    assert ballot.get_appearances_in_rank("Normie", 5) == 0

