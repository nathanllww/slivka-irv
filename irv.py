import copy
import csv
import collections
import pandas as pd
import numpy as np
from numpy.random import default_rng

class IRVElection:
    """
    Instant-Runoff Voting (IRV) election counter
    Design decisions/known limitations:
        - Only supports one election
        - If a candidate gets a majority, immediate win

    Ballot format refrence:
        - CSV with each line a ballot, ranking candidates from left to right
        - Lines starting with # are comments and ignored
        -Example:
            # this is a comment
            A,B,C
            C,B
    """

    # TODO list:
    #   - implement write functions
    #   - use Counter instead of dict for tallies

    def __init__(self, file, remove_exhausted_ballots=False, verbose=False, permute=False):
        """
        Initilize an election, reading ballots into numpy array, creating
        list of candidates and setting parameters

        Parameters
        ----------
        file : string
            - Path to the file, which should be in ballot format
        remove_exhausted_ballots : boolean, optional
            - Whether to remove exhausted ballots from the count or count them
            as ``no confidence''. Default of False does the latter
        verbose : boolean, optional
            - Whether to print certain progress info.  Default False
        permute : boolean, optional
            - Whether to randomly permute the order of ballots before processing.
            Potentially useful in testing.  Default False
        """

        # first determine longest ballot (num_col), so that pandas can read properly
        # unfornuatly doesn't seem to be a way around this
        num_col = 0
        with open(file, 'r') as csvfile:
            lines = csv.reader(csvfile)
            for row in lines:
                if num_col < len(row):
                    num_col = len(row)

        self.ballots = pd.read_csv(file, header=None, names=range(num_col), index_col=False, dtype='str', comment='#')
        self.candidates = set()

        for col in self.ballots:
            self.candidates.update(self.ballots[col].unique())
        if np.nan in self.candidates:
            self.candidates.remove(np.nan)

        self.ballots = self.ballots.to_numpy()
        if permute:
            default_rng().shuffle(self.ballots)

        self.remove_exhausted_ballots = remove_exhausted_ballots
        self.verbose = verbose

    def run_and_write(self, winner_file="winner.txt", steps_file="steps.txt"):
        """
        Wrapper around run and write_results that runs and then writes results to
        winner.txt and steps.txt

        Parameters
        ----------
        winner_file : string, optional
            - File to write the winner to. Default winner.txt
        steps_file : string, optional
            - File to write the steps to. Default steps.txt
        """

        winner_data, steps_data = self.run()
        self.write_results(winner_data, steps_data, winner_data, winner_file)

    def write_results(self, winner, steps, winner_file, steps_file):
        """
        Writes winner and steps to winner_file and steps_file

        Parameters
        ----------
        winner : string
            - Winner of the election
        steps : list of dictornary
            - Array of dictornaries storing candidate tallies at each stage
        winner_file : string
            - File to which to write the winner
        steps_file : string
            - File to which to write the steps
        """

        raise NotImplementedError()

    def run(self):
        """
        Runs the election

        Algorthmic details:
            - If multiple candidates are tied for last, tries to break ties
            using break_ties

        Returns
        -------
        winner : string
            - Winner of the election. In the event of a no confidence result, this is 
            "No Confidence"
        steps : list of dictornary
            - Array of dictornaries storing candidate tallies at each stage
        """

        tallies = collections.Counter()
        for name in self.candidates:
            tallies[name] = 0
        steps = []

        rund = 0
        while len(tallies) > 1:
            tallies, removed = self.one_round(tallies, rund=rund)
            rem_len = len(removed)
            complete_step = removed
            complete_step.update(tallies)
            steps.append(dict(complete_step))
            rund += 1
            if rem_len == 0: # we only have nothing removed if majority
                return tallies.most_common(1)[0][0], steps

        # if remove_exhausted_ballots, we have a winner regardless of exhausted ballots
        winner = list(tallies.keys())[0]
        if not self.remove_exhausted_ballots and tallies[winner]/(self.ballots.shape[0]) < 0.5:
            if self.verbose:
                print(f"No confidence vote! Winner, {winner}, recieved only {tallies[winner]} votes out of {self.ballots.shape[0]} ballots")
            winner = "No Confidence"

        return winner, steps

    def one_round(self, tallies, rund=-1):
        """
        Helper to run one round of IRV
        Algo is essentially "remove and make 2nd place 1st" but without modifying ballots

        Parameters
        ----------
        tallies : Counter
            - Counter, with candidates as keys, representing how many votes
            a candidate currently has
        rund : int, optional
            - For debugging: round number, starting at zero like python arrays
            Default -1

        Returns
        -------
        new_tallies : dictornary
            - Updated tallies with new vote counts, and lowest candidate removed
        removed : dictornary
            - Dictornary with removed candidate and their tally count at this stage
        """

        active_candidates = set(tallies.keys()) # set for ``permutation independence''
        new_tallies = collections.Counter()
        for name in active_candidates:
            new_tallies[name] = 0

        # for each ballot, count first choice that has not been eliminated
        # this might have been more elegant by changing self.ballots so the first
        # column is always such a choice, but I perfer not having to change ballots
        # as this opens up to very subtle errors
        for i in range(self.ballots.shape[0]):
            tocount = 0
            # is this method of escaping from the loop good or bad practice?
            try:
                while not (self.ballots[i,tocount] in active_candidates):
                    # check if nan if is float rather than string
                    if type(self.ballots[i,tocount]) == float or tocount == self.ballots.shape[1]-1:
                        raise Exception("exhausted ballot")
                    tocount += 1
                new_tallies[self.ballots[i,tocount]] += 1
            except Exception as e:
                # don't ignore real errors
                if str(e) != "exhausted ballot":
                    raise e

        if self.verbose:
            print(f"Round {rund}: New tallies are {new_tallies}")

        # determine all min tallies, of which there could be many
        sort_tallies = new_tallies.most_common()[::-1]
        min_names = []
        i = 0
        while i < len(sort_tallies) and sort_tallies[0][1] == sort_tallies[i][1]:
            min_names.append(sort_tallies[i][0])
            i += 1

        removed = {}
        # don't bother removing if one candidate already has a majority
        if sort_tallies[-1][1] <= self.ballots.shape[0]/2 :
            if len(min_names) == 1:
                loser = min_names[0]
                removed = {loser : new_tallies.pop(loser)}
            else:
                losers = self.break_ties(min_names, new_tallies)
                for name in losers:
                    removed[name] = new_tallies.pop(name)

        return new_tallies, removed

    def break_ties(self, tied_candidates, tallies):
        """
        Helper to break ties between candidates, returning the loser
        Compares the number of 1st choice votes, then 2nd, etc

        If the sum of the tallies of subset of tied_candidates is less than
        the min non-tied tally, remove all these candidates; this helps reduce
        the number of unbreakable ties

        In the (hopefully unlikely) case neither of these can break the tie, error

        Parameters
        ----------
        tied_candidates : list
            - List of the candidates tied.  Modified to reflect tie-breaking progress
        tallies : Counter
            - The current tallies of all candidates

        Returns
        -------
        loser : list of string
            - The losing candidate(s) in the tie break
        """

        if self.verbose:
            print(f"Breaking ties between {tied_candidates}!")

        # determine min non-tied tally
        sort_tallies = tallies.most_common()[::-1]
        tied_val = sort_tallies[0][1]
        tied_sum = 0 # to double check computation of tied vals (mainly for debugging)

        i = 0
        while i < len(sort_tallies) and sort_tallies[0][1] == sort_tallies[i][1]:
            tied_sum += sort_tallies[i][1]
            i+=1

        if i == len(sort_tallies):
            min_nt = -1
        else:
            min_nt = sort_tallies[i][1]

        if tied_sum != len(tied_candidates)*tied_val:
            raise Exception(f"PROBLEM: tied_sum is {tied_sum} while len*tied_val is {len(tied_candidates)*tied_val}!")

        # check at the beginning as well
        if len(tied_candidates)*tied_val < min_nt:
            if self.verbose:
                print(f"Removed all of {tied_candidates}, since their sum tally ({len(tied_candidates)*tied_val}) was less than the min non-tied ({min_nt})")
            return tied_candidates

        for place in range(self.ballots.shape[1]):
            min_names = []
            min_val = -1
            for name in tied_candidates:
                place_votes = len(self.ballots[self.ballots[:,place]==name,place])
                if min_val == -1 or place_votes < min_val:
                    min_names = [name]
                    min_val = place_votes
                elif place_votes == min_val:
                    min_names.append(name)

            tied_candidates = min_names
            if len(min_names) == 1:
                return min_names[0]
            elif len(min_names)*tied_val < min_nt:
                if self.verbose:
                    print(f"Removed all of {min_names}, since their sum tally ({len(min_names)*tied_val}) was less than the min non-tied ({min_nt})")
                return min_names

        raise ValueError(f"Unbreakable tie between {tied_candidates}, new election needed")
