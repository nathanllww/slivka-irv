import csv
import collections
import os
import logging
import pandas as pd
import numpy as np
from numpy.random import default_rng
import datetime
from . import LOGGING_FOLDER


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
    #   - exception handling in write functions?

    def __init__(self, file: str,
                 remove_exhausted_ballots: bool = False,
                 permute: bool = False,
                 log_to_stderr: bool = False,
                 save_log: bool = False):
        """
        Initialize an election, reading ballots into numpy array, creating
        list of candidates and setting parameters

        Parameters
        ----------
        file : string
            - Path to the file, which should be in ballot format
        remove_exhausted_ballots : boolean, optional
            - Whether to remove exhausted ballots from the count or count them
            as ``no confidence''. Default of False does the latter
        log_to_stderr : boolean, optional
            - Whether to print certain progress info.  Default False
        permute : boolean, optional
            - Whether to randomly permute the order of ballots before processing.
            Potentially useful in testing.  Default False
        save_log : boolean, option
            - Whether to save logs to a timestamped file.
            Logs folder can be set by environment variable `LOGGING_FOLDER`.
            Default False
        """

        # first determine longest ballot (num_col), so that pandas can read properly
        # unfortunately doesn't seem to be a way around this

        self._populate_ballots_and_candidates(file, permute=permute)
        self.remove_exhausted_ballots: bool = remove_exhausted_ballots
        self.log_to_stderr: bool = log_to_stderr
        self.input_file: str = file
        self._setup_logger_handler(save_log, log_to_stderr)

    def _populate_ballots_and_candidates(self, file: str, permute: bool = False) -> None:
        """
        Helper function for `__init__`

        Populates `self.ballots` and `self.candidates` from `file`

        Parameters
        ----------
        file : string
            - Path to the file, which should be in ballot format
        permute : boolean, optional
            - Whether to randomly permute the order of ballots before processing.
            Potentially useful in testing.  Default False
        """
        num_col = 0
        with open(file, 'r') as csvfile:
            lines = csv.reader(csvfile)
            for row in lines:
                if num_col < len(row):
                    num_col = len(row)

        self.ballots = pd.read_csv(file, header=None, names=range(num_col), index_col=False, dtype='str', comment='#')
        self.candidates: set = set()

        for col in self.ballots:
            self.candidates.update(self.ballots[col].unique())
        if np.nan in self.candidates:
            self.candidates.remove(np.nan)

        self.ballots: np.ndarray = self.ballots.to_numpy()
        if permute:
            default_rng().shuffle(self.ballots)

    def _setup_logger_handler(self, save_log: bool, log_to_stderr: bool) -> None:
        """
        Helper function for `__init__`

        Initializes logger, and adds handlers for logger.

        Parameters
        ----------
        save_log : bool
            If True, saves logs to a file, by adding a FileHandler to the logger
            Default False
        log_to_stderr : bool
            If True, prints logs to stderr, by adding a StreamHandler to the logger
        """
        self._logger = logging.getLogger(str(self.__class__))
        self._logger.setLevel(logging.INFO)
        if log_to_stderr:
            self._logger.addHandler(logging.StreamHandler())
        if save_log:
            os.makedirs(LOGGING_FOLDER, exist_ok=True)
            input_basename = os.path.basename(self.input_file).split('.')[0]
            timestamp_str = str(datetime.datetime.now())
            self._logger.addHandler(
                logging.FileHandler(
                    os.path.join(
                        LOGGING_FOLDER,
                        f"{input_basename}-{timestamp_str}-log.txt")
                )
            )

    def write_results(self, winner: str, steps: list[dict], output_file: str) -> None:
        """
        Writes winner and steps to winner_file and steps_file

        Parameters
        ----------
        winner : string
            - Winner of the election
        steps : list[dict]
            - Array of dictornaries storing candidate tallies at each stage
        output_file : string
            - File to write the details to
        """

        winner_line = f'= WINNER: {winner} ='
        lines = ['=' * len(winner_line) + '\n']
        lines.append(winner_line + '\n')
        lines.append('=' * len(winner_line) + '\n')

        lines.append(f"There were {self.ballots.shape[0]} total ballots cast\n")
        if winner != "No Confidence":
            percent_votes = round(100*steps[-1][winner]/self.ballots.shape[0], 2)
            lines.append(f"In the final round, {winner} received {steps[-1][winner]} votes, or {percent_votes}%\n")
        lines.append('\n\n')
        lines.append('==========\n')
        lines.append('= ROUNDS =\n')
        lines.append('==========\n')
        # TODO: sort steps, do nothing, or keep order consistent?
        for i in range(len(steps)):
            lines.append(f'Round {i+1}: {steps[i]}\n')

        with open(output_file, 'w') as f:
            f.writelines(lines)

    def run(self) -> tuple[str, list[dict]]:
        """
        Runs the election

        Algorithmic notes:
            - See break_ties for details on how it attempts to break ties
            - If, in any round, a candidate has a tally exceeding half the total
            ballots cast, that candidate is deemed the winner and the function returns
            - If not remove_exhausted_ballots, exhausted ballots are treated as
            votes of no confidence

        Returns
        -------
        winner : string
            - Winner of the election. In the event of a no confidence result, this is
            "No Confidence"
        steps : list[dict]
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
            if rem_len == 0:  # we only have nothing removed if majority
                return tallies.most_common(1)[0][0], steps

        # if remove_exhausted_ballots, we have a winner regardless of exhausted ballots
        winner = list(tallies.keys())[0]
        if not self.remove_exhausted_ballots and tallies[winner]/(self.ballots.shape[0]) <= 0.5:
            self._logger.info(
                f"""
                No confidence vote! Winner: {winner} received {tallies[winner]} votes
                out of {self.ballots.shape[0]} ballots
                """
            )
            winner = "No Confidence"

        return winner, steps

    def one_round(self, tallies: collections.Counter, rund: int = -1) -> tuple[dict, dict]:
        """
        Helper to run one round of IRV
        Algo is essentially "remove and make 2nd place 1st" but without modifying ballots

        Parameters
        ----------
        tallies : collections.Counter
            - Counter, with candidates as keys, representing how many votes
            a candidate currently has
        rund : int, optional
            - For logging: round number, starting at zero like python arrays
            Default -1

        Returns
        -------
        new_tallies : dict
            - Updated tallies with new vote counts, and lowest candidate removed
        removed : dict
            - Dictionary with removed candidate and their tally count at this stage
        """

        active_candidates = set(tallies.keys())  # set for ``permutation independence''
        new_tallies = collections.Counter()
        for name in active_candidates:
            new_tallies[name] = 0

        # for each ballot, count first choice that has not been eliminated
        # this might have been more elegant by changing self.ballots so the first
        # column is always such a choice, but I prefer not having to change ballots
        # as this opens up to very subtle errors
        for i in range(self.ballots.shape[0]):
            tocount = 0
            while not self.is_exhausted(i, tocount) and not (self.ballots[i, tocount] in active_candidates):
                tocount += 1
            if not self.is_exhausted(i, tocount):
                new_tallies[self.ballots[i, tocount]] += 1

            # # is this method of escaping from the loop good or bad practice?
            # try:
            #     while not (self.ballots[i, tocount] in active_candidates):
            #         # check if nan if is float rather than string
            #         if type(self.ballots[i, tocount]) == float or tocount == self.ballots.shape[1]-1:
            #             raise Exception("exhausted ballot")
            #         tocount += 1
            #     new_tallies[self.ballots[i, tocount]] += 1
            # except Exception as e:
            #     # don't ignore real errors
            #     if str(e) != "exhausted ballot":
            #         raise e

        self._logger.info(f"Round {rund}: New tallies are {new_tallies}")

        # determine all min tallies, of which there could be many
        sort_tallies = new_tallies.most_common()[::-1]
        min_names = []
        i = 0
        while i < len(sort_tallies) and sort_tallies[0][1] == sort_tallies[i][1]:
            min_names.append(sort_tallies[i][0])
            i += 1

        new_tallies, removed = self.remove_candidates(new_tallies, min_names, sort_tallies)
        return new_tallies, removed

    def is_exhausted(self, ballot: int, ranking: int) -> bool:
        if ranking > self.ballots.shape[1]-1 or type(self.ballots[ballot, ranking]) == float:
            return True
        return False

    def remove_candidates(self, new_tallies: collections.Counter, min_names: list[str], sort_tallies:
                          list[tuple[int, str]]) -> tuple[collections.Counter, set]:
        """
        Remove losing candiate from new_tallies and returns set of names of removed candidate
        (or empty set if a candiate has already won)

        Modifies new_tallies, returns the name(s) of loser
        """

        removed = {}
        # don't bother removing if one candidate already has a majority
        if sort_tallies[-1][1] <= self.ballots.shape[0] / 2:
            if len(min_names) == 1:
                loser = min_names[0]
                removed = {loser: new_tallies.pop(loser)}
            else:
                losers = self.break_ties(min_names, new_tallies)
                for name in losers:
                    removed[name] = new_tallies.pop(name)

        return new_tallies, removed

    def break_ties(self, tied_candidates: list[str], tallies: collections.Counter) -> list[str]:
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

        self._logger.info(f"Breaking ties between {tied_candidates}!")

        # determine min non-tied tally
        sort_tallies = tallies.most_common()[::-1]
        tied_val = sort_tallies[0][1]
        tied_sum = 0  # to double check computation of tied vals (mainly for debugging)

        i = 0
        while i < len(sort_tallies) and sort_tallies[0][1] == sort_tallies[i][1]:
            tied_sum += sort_tallies[i][1]
            i += 1

        min_nt = -1
        if i < len(sort_tallies):
            min_nt = sort_tallies[i][1]

        # check at the beginning as well
        if self.can_remove_all(tied_candidates, min_nt, tied_val):
            return tied_candidates

        for place in range(self.ballots.shape[1]):
            min_names = []
            min_val = -1
            for name in tied_candidates:
                place_votes = len(self.ballots[self.ballots[:, place] == name, place])
                if min_val == -1 or place_votes < min_val:
                    min_names = [name]
                    min_val = place_votes
                elif place_votes == min_val:
                    min_names.append(name)

            tied_candidates = min_names
            if self.can_remove_all(min_names, min_nt, tied_val):
                return min_names

        raise ValueError(f"Unbreakable tie between {tied_candidates}, new election needed")

    def can_remove_all(self, tied_candidates: list[str], min_non_tied: int, tied_val: int):
        """
        Determine if all of tied_candidates can be removed
        (i.e. their sum is less than min_non_tied)

        Also logs removal to reduce code duplication
        """

        if len(tied_candidates)*tied_val < min_non_tied:
            sum_tally = len(tied_candidates)*tied_val
            self._logger.info(
                f"Removed all of {tied_candidates}, as their sum tally ({sum_tally}) is less than the"
                f" min non-tied ({min_non_tied})"
            )
            return True
        # can also always remove all if there's only one
        elif len(tied_candidates) == 1:
            return True
        else:
            return False
