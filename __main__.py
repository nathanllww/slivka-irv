import os
import argbind
import logging
from io import StringIO
from wildcat_connection import WildcatConnectionCSV as wc
from irv import IRVElection

IRVElection = argbind.bind(IRVElection, without_prefix=True)

_logger = logging.getLogger(__name__)


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
        save = argbind.bind(ballot.save_to_files, without_prefix=True)
        save()

    for name, ballot_str in ballot.question_formatted_ballots.items():
        election = IRVElection(StringIO(ballot_str), name=name)
        winner, steps = election.run()
        print(election.result_string(winner, steps))
        if elections_output:
            election.write_results(winner, steps, os.path.join(elections_output, f"{name}.txt"))

if __name__ == "__main__":
    args = argbind.parse_args()
    with argbind.scope(args):
        run()
