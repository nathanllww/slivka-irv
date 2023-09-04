class RankedChoiceBallots:
    """
    RankedChoiceBallots is a representation of a single elections ballots.

    Attributes
    ----------
    votes : list[list[str]]
        2D list of votes. `votes[i][j]` is the candidate name that the `i`th voter ranked as `(j+1)`th.
    """
    def __init__(self, votes):
        self.votes: list[list[str]] = votes

        for single_ballot in votes:
            for candidate in single_ballot:
                if single_ballot.count(candidate) > 1:
                    raise ValueError("There are duplicate votes in a single ballot!")

            typecheck = all(isinstance(candidate, str) for candidate in single_ballot)
            if not typecheck:
                raise ValueError("Not every value is a string!")

    def get_candidates(self) -> set[str]:
        """Gets all unique candidate names"""
        candidates = set()
        for single_ballot in self.votes:
            for candidate in single_ballot:
                candidates.add(candidate)
        return candidates

    def get_appearances_in_rank(self, candidate: str, rank: int):
        """Gets the number times `candidate` was ranked `rank` before eliminations"""
        rank_tally = 0
        for single_ballot in self.votes:
            if len(single_ballot) < rank:
                continue
            elif single_ballot[rank-1] == candidate:
                rank_tally += 1
        return rank_tally
