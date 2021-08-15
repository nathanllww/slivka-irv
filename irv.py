import copy
import csv
import numpy as np
import pandas as pd

# ballots = pd.read_csv("test.csv", header=None, index_col=False)
# candidates = set()
# for col in ballots:
#     candidates.update(ballots[col].unique())
# candidates.remove(np.nan)

class IRVElection:
    """
    WIP IRV
    Design decisions/known limitations:
        - Only supports one election
        - Is somewhat conservative in ties (see run() for details)

    Ballot format refrence:
        - CSV with each line a ballot, ranking candidates from left to right
        -Example:
            A,B,C
            C,B
    """

    # TODO list:
    #   - implement functions
    #   - test test

    def __init__(self, file, remove_exhausted_ballots=False):
        """
        Reads ballot format file into TODO

        Parameters
        ----------
        file : string
            - Path to the file, which should be in ballot format
        remove_exhausted_ballots : boolean, optional
            - Whether to remove exhausted ballots from the count or count them
            as ``no confidence''. Default of False does the latter
        """
        self.ballots = pd.read_csv(file, header=None, index_col=False)
        self.candidates = set()
        for col in self.ballots:
            self.candidates.update(self.ballots[col].unique())
        self.candidates.remove(np.nan)
        self.ballots = self.ballots.to_numpy()
        self.remove_exhausted_ballots = remove_exhausted_ballots

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
        steps : TODO (see above)
            - TODO
        winner_file : string
            - File to write the winner to
        steps_file : string
            - File to write the steps to
        """
        raise NotImplementedError()

    def run(self):
        """
        Runs the election

        Algorthmic details:
            - If multiple candidates are tied for last, recursivly check the next
            layer of preferences.  If complete tie, error.

        Returns
        -------
        winner : string
            - Winner of the election
        steps : np.array #TODO: figure out what data type!
            - Array (matrix?) of election results from each step of the IRV process
        """
        tallies = {}
        for name in self.candidates:
            tallies[name] = 0
        steps = [tallies] # should this be empty?

        rund = 1
        while len(tallies) > 1:
            tallies = self.one_round(tallies, rund)
            steps.append(tallies)
            rund += 1

        # if remove_exhausted_ballots, we have a winner regardless of exhausted ballots
        winner = list(tallies.keys())[0]
        if not self.remove_exhausted_ballots and tallies[winner]/(self.ballots.shape[0]) < 0.5:
            print(f"No confidence vote! Winner, {winner}, recieved only {tallies[winner]} votes out of {self.ballots.shape[0]} ballots")
            winner = "No Confidence"

        return winner, steps

    def one_round(self, tallies, rund):
        """
        Helper to run one round of IRV

        This algorthim differs from the standard "remove and make 2nd place 1st place" algo, but does not have to modify ballots or shift rows.
        It also provides an easy of seeing setps and intermediate tallies, but perhaps at the expense of being slightly more complex.

        Parameters
        ----------
        tallies : dictornary
            - Dictornary, with candidates as keys, representing how many votes
            a candidate currently has
        rund : int
            - round number

        Returns
        -------
        new_tallies : dictornary
            - Updated tallies with new vote counts, and lowest candidate removed
        """

        active_candidates = set(tallies.keys()) # set for ``permutation independence''
        tally_changes = {}
        for name in active_candidates:
            tally_changes[name] = 0

        # count rund column iff candidates in all previous rows have been eliminated
        # (and rund hasn't been either!)
        for i in range(self.ballots.shape[0]):
            prev_choices = self.ballots[i,0:rund]
            name = str(self.ballots[i,rund])
            if name in active_candidates and (not any(x in active_candidates for x in prev_choices)):
                tally_changes[str(self.ballots[i,rund])] += 1

        new_tallies = copy.deepcopy(tallies) # to avoid issues with steps?
        for name in active_candidates:
            new_tallies[name] = tallies[name] + tally_changes[name]

        # need second for-loop due to unclear set order; this is usually helpful but not here
        min_names = []
        for name in active_candidates:
            if len(min_names) == 0 or new_tallies[name] < new_tallies[min_names[0]]:
                min_names = [name]
            elif new_tallies[name] == new_tallies[min_names[0]]:
                min_names.append(name)

        if len(min_names) == 1:
            new_tallies.remove(min_names[0])
        else:
            loser = self.break_ties(min_names)
            new_tallies.remove(loser)

        return new_tallies

    def break_ties(self, tied_candidates):
        """
        Helper to break ties between candidates, returning the loser
        Does so by comparing number of 1st choice votes, then 2nd, etc
        If still tied (highly improbable), error

        Parameters
        ----------
        tied_candidates : list
            - List of the candidates tied

        Returns
        -------
        loser : string
            - The losing candidate in the tie break
        """
        raise NotImplementedError()

# Ballot format refrence:
#     - CSV with each line a ballot, ranking candidates from left to right
#     -Example:
#         A,B,C
#         C,B
