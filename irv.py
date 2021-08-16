import copy
import csv
import numpy as np
import pandas as pd

class IRVElection:
    """
    WIP IRV
    Design decisions/known limitations:
        - Only supports one election
        - Ballot format must have the most full ballot first
        - Is somewhat conservative in ties (see run() for details)

    Ballot format refrence:
        - CSV with each line a ballot, ranking candidates from left to right
        -Example:
            A,B,C
            C,B
    """

    # TODO list:
    #   - implement functions
    #   - Support longer ballots than first
    #   - test test test

    def __init__(self, file, remove_exhausted_ballots=False, verbose=False):
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
        """

        self.ballots = pd.read_csv(file, header=None, index_col=False)
        self.candidates = set()

        for col in self.ballots:
            self.candidates.update(self.ballots[col].unique())
        self.candidates.remove(np.nan)

        self.ballots = self.ballots.to_numpy()
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

        tallies = {}
        for name in self.candidates:
            tallies[name] = 0
        steps = []

        rund = 0
        while len(tallies) > 1:
            tallies, removed = self.one_round(tallies, rund=rund)
            complete_step = removed
            complete_step.update(tallies)
            steps.append(complete_step)
            rund += 1

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
        tallies : dictornary
            - Dictornary, with candidates as keys, representing how many votes
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
        new_tallies = {}
        for name in active_candidates:
            new_tallies[name] = 0

        # for each ballot, count first choice that has not been eliminated
        for i in range(self.ballots.shape[0]):
            tocount = 0
            # is this good or bad practice?
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
                    print(self.ballots[i,tocount])
                    raise e

        if self.verbose:
            print(f"Round {rund}: New tallies are {new_tallies}")

        min_names = [] # could have multiple last place
        for name in active_candidates:
            if len(min_names) == 0 or new_tallies[name] < new_tallies[min_names[0]]:
                min_names = [name]
            elif new_tallies[name] == new_tallies[min_names[0]]:
                min_names.append(name)

        if len(min_names) == 1:
            loser = min_names[0]
        else:
            loser = self.break_ties(min_names)
        removed = {loser : new_tallies.pop(loser)}

        return new_tallies, removed

    def break_ties(self, tied_candidates):
        """
        Helper to break ties between candidates, returning the loser
        Does so by comparing number of 1st choice votes, then 2nd, etc
        If still tied (hopefully unlikely), error

        Parameters
        ----------
        tied_candidates : list
            - List of the candidates tied.  Modified to reflect tie-breaking progress

        Returns
        -------
        loser : string
            - The losing candidate in the tie break
        """

        if self.verbose:
            print(f"Breaking ties between {tied_candidates}!")

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

        raise ValueError(f"Unbreakable tie between {tied_candidates}, new election needed")
