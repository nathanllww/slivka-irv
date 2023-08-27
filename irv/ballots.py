class RankedChoiceBallots:
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
        candidates = set()
        for single_ballot in self.votes:
            for candidate in single_ballot:
                candidates.add(candidate)
        return candidates

    def get_appearances_in_rank(self, candidate: str, rank: int):
        rank_talley = 0
        for single_ballot in self.votes:
            if len(single_ballot) < rank:
                continue
            elif single_ballot[rank-1] == candidate:
                rank_talley += 1
        return rank_talley

# votes = [
#     ["Norm", "Normie", "Norman"],
#     ["Norm", "Normie"],
#     ["Norman", "Norm", "Normie"]
# ]
#
#
# ballots = RankedChoiceBallots(votes)
# print(ballots.votes)
#
# votes = [
#     ["Norm", "Normie", "Norman"],
#     ["Norm", "Normie"],
#     ["Norman", "Norm", "Normie"],
#     ["Andreas"]
# ]
#
# ballots2 = RankedChoiceBallots(votes)
# print(ballots2.votes)

