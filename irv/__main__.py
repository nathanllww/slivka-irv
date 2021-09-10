import os
import argbind
import logging
from io import StringIO
from wildcat_connection import WildcatConnectionCSV
from . import IRVElection

IRVElection = argbind.bind(IRVElection.irv_election, without_prefix=True)

_logger = logging.getLogger(__name__)


def question_title_format(question: str) -> str:
    return f"""
{"#" * (len(question) + 4)}
# {question} #
{"#" * (len(question) + 4)}
    """


@argbind.bind(positional=True, without_prefix=True)
def run(
    wc_file: str,
    ballots_output: bool = False,
    elections_output: str = "./elections"
) -> None:
    """
    End-to-end IRV calculation from Wildcat Connection CSV.

    Prints winners and writes results to disk.

    Parameters
    ----------
    wc_file : str
        CSV file generated from exported election on Wildcat Connection
    ballots_output : bool, optional
        Whether to save preprocessed ballot. Default: False
    elections_output : str, optional
        Folder for saving elections output. Default; "./elections"
    """
    ballot = WildcatConnectionCSV(wc_file)
    if ballots_output:
        print(f"Saving ballots. Ballot folder: {ballot.get_ballot_folder()}")
        ballot.save_to_files(include_spoilt_ballots=True)

    if elections_output:
        print(f"Election results saved in {elections_output}")

    for name, ballot_str in ballot.question_formatted_ballots.items():
        election = IRVElection(StringIO(ballot_str), name)
        winner, steps = election.run()
        print(question_title_format(name))
        print(election.results_string(winner, steps))
        if elections_output:
            os.makedirs(elections_output, exist_ok=True)
            election.write_results(winner, steps, os.path.join(elections_output, f"{name}.txt"))


def main_func():
    args = argbind.parse_args()
    with argbind.scope(args):
        run()


if __name__ == "__main__":
    main_func()
