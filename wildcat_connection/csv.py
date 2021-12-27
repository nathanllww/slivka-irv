import os
import datetime
import pandas as pd
from .constants import SUBMISSION_ID_COLNAME, QUESTION_RANK_SEPARATOR
from . import BALLOT_FOLDER
from .utils import isnan, wc_update_catcher


class WildcatConnectionCSV:
    """
    Class for converting a Wildcat Connection exported ballot CSV into
    the ballot format for the `irv` module.

    Attributes
    ----------
    csv_filepath: str
        Filepath to Wildcat Connection CSV
    question_num_candidates: dict[str, int]
        Maps question name to number of candidates.
    question_formatted_ballots: dict[str, str]
        Maps question name to formatted ballot string.
        See `IRVElection` for information about the ballot format
    question_spoilt_ballots: dict[str, list[str]]
        Maps question name to list of SubmissionIDs with spoilt ballots.

    Parameters
    ----------
    csv_filepath : str
        Filepath to Wildcat Connection exported CSV.
    """
    @wc_update_catcher
    def __init__(self, csv_filepath: str):
        self.csv_filepath = csv_filepath
        self.__df: pd.DataFrame = self._get_dataframe()
        self.question_num_candidates: dict[str, int] = self._get_question_num_candidates()
        formatted_ballots, spoilt_ballots = self._get_ballot_formatted_strings()
        self.question_formatted_ballots: dict[str, str] = formatted_ballots
        self.question_spoilt_ballots: dict[str, list[str]] = spoilt_ballots

    def _get_dataframe(self) -> pd.DataFrame:
        df = pd.read_csv(self.csv_filepath, header=[1], dtype=str)
        df[SUBMISSION_ID_COLNAME] = df[SUBMISSION_ID_COLNAME].astype(int)
        df = df.set_index(SUBMISSION_ID_COLNAME)
        return df

    @staticmethod
    def _valid_rank_set(rank_set: set[int]) -> bool:
        """
        Checks if `rank_set` is a set of all numbers from 1 to `len(rank_set)`
        """
        return rank_set == set(range(1, len(rank_set) + 1))

    def _get_question_num_candidates(self) -> dict[str, int]:
        """
        Helper function for __init__

        Generates questions from DataFrame, and number of rankings for each question.
        Raises ValueError if duplicate columns exist.

        `self.__df` should already be populated.

        Returns
        -------
        question_num_candidates : dict[str, int]
            Dictionary mapping question name to number of candidates.
        """
        question_ranks = [col.split(QUESTION_RANK_SEPARATOR) for col in self.__df.columns
                          if col != SUBMISSION_ID_COLNAME]
        tracked = {}
        for question, rank in question_ranks:
            try:
                rank = int(rank)
            except ValueError:
                raise ValueError(f"Duplicate Question: {question}")
            tracked_ranks = tracked.setdefault(question, set())
            if rank in tracked_ranks:
                raise ValueError(f"Duplicate Question: {question}")
            tracked_ranks.add(rank)
        for question, rank_set in tracked.items():
            if not self._valid_rank_set(rank_set):
                raise ValueError(
                    f"""
                    Question {question} does not contain rank choices from 1 to {len(rank_set)}
                    It contains: {rank_set}
                    """
                )
        return {question: len(rank_set) for question, rank_set in tracked.items()}

    def _get_one_ballot_format(self, question: str, num_candidates: int) -> tuple[str, list[str]]:
        """
        Helper function to `_get_ballot_formatted_strings`

        Parameters
        ----------
        question : str
            Question name
        num_candidates : int
            Number of candidates
        Returns
        -------
        ballot_string : str
            Formatted ballot string
        spoiled_ballots : list[str]
            List of Submission IDs of spoiled ballots
        """
        def _is_spoiled(row: list[str]) -> bool:
            for i in range(1, len(row)):
                if isnan(row[i-1]) and not isnan(row[i]):
                    return True
            return False

        columns = [f"{question}{QUESTION_RANK_SEPARATOR}{rank}"
                   for rank in range(1, num_candidates + 1)]
        valid_rows = []
        spoiled_ballots = []
        for submission_id, row in self.__df[columns].iterrows():
            row = row.tolist()
            if _is_spoiled(row):
                spoiled_ballots.append(submission_id)
            else:
                valid_rows.append(",".join([item for item in row if not isnan(item)]))

        ballot_string = "\n".join(valid_rows)
        return ballot_string, spoiled_ballots

    def _get_ballot_formatted_strings(self) -> tuple[dict[str, str], dict[str, list[str]]]:
        """
        For each question, get the ballot formatted string and the submission ids of spoilt ballots.

        `self.__df` and `self.question_num_candidates` should already be populated.

        Returns
        -------
        question_formatted_ballots : dict[str, str]
            Contains the formatted ballot string for each question.
        question_spoilt_ballots : dict[str, list[str]]
            Contains the Submission IDs of the spoilt ballots for each question.

        """
        question_formatted_ballots, question_spoilt_ballots = {}, {}
        for question, num_candidates in self.question_num_candidates.items():
            ballot_string, spoiled_ballots = self._get_one_ballot_format(question, num_candidates)
            question_formatted_ballots[question] = ballot_string
            question_spoilt_ballots[question] = spoiled_ballots

        return question_formatted_ballots, question_spoilt_ballots

    def get_ballot_folder(self) -> str:
        """
        Gets folder where ballots will be saved. Uses BALLOT_FOLDER constant.

        Returns
        -------
        ballot_folder : str
        """
        csv_basename = os.path.basename(self.csv_filepath).split('.')[0]
        timestamp_str = str(datetime.datetime.now())
        return os.path.join(BALLOT_FOLDER, f"{csv_basename}-{timestamp_str}")

    def save_to_files(self, include_spoilt_ballots: bool = False) -> None:
        """
        Saves ballots to folder.

        Each question is saved to a different file in the following format.

        - ballot_folder
            - question 1.csv
            - question 1_spoilt.txt
            - question 2.csv
            - question 2_spoilt.txt

        Parameters
        ----------
        include_spoilt_ballots: bool, optional
            Whether to make another file for spoilt ballots.
            Default: False
        """
        folder = self.get_ballot_folder()
        os.makedirs(folder)
        for question, ballot_str in self.question_formatted_ballots:
            with open(os.path.join(folder, f"{question}.csv")) as file:
                file.write(ballot_str)
            if include_spoilt_ballots:
                with open(os.path.join(folder, f"{question}_spoilt.txt")):
                    file.writelines(self.question_spoilt_ballots[question])
