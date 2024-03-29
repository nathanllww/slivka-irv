import os
import argbind
import logging
from wildcat_connection import WildcatConnectionCSV
from . import IRVElection

"""
WTF is going on here?

In the case that the website breaks, you can use the command line tool specified here to run the election.

WTF is argbind?

`argbind` turns functions into CLI interfaces without verbose argparsing.
Prem Seetharaman (previously a postdoc at NU) maintains argbind and if you find issues with it, contact him and tell him
that Andreas sent you: https://github.com/pseeth/argbind
"""
IRVElection.__init__.__doc__ = IRVElection.__doc__  # this makes -h docs work.
IRVElection = argbind.bind(IRVElection, without_prefix=True)  # This actually connects the function to CLI.

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
    elections_output: str = "./elections",
    verbose: bool = False
) -> list[tuple[str, str, list[dict]]]:
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
        Folder for saving elections output. Default: "./elections"
    verbose : bool, optional
        Whether to print extra information. Default: False

    Returns
    -------
    results : list[tuple[str, str, list[dict]]]
        Returns list of elections tuples, containing election name, winner, and steps
        in that order.

    """
    ballot = WildcatConnectionCSV(wc_file)
    if ballots_output:
        if verbose:
            print(f"Saving ballots. Ballot folder: {ballot.get_ballot_folder()}")
        ballot.save_to_files(include_spoilt_ballots=True)

    if elections_output and verbose:
        print(f"Election results saved in {elections_output}")

    results = []
    for name, ballots in ballot.question_formatted_ballots.items():
        election = IRVElection(ballots, name)
        winner, steps = election.run()
        if verbose:
            print(question_title_format(name))
            print(election.results_string(winner, steps))
        results.append((name, winner, steps))
        if elections_output:
            os.makedirs(elections_output, exist_ok=True)
            election.write_results(winner, steps, os.path.join(elections_output, f"{name}.txt"))
    return results


def main_func():
    args = argbind.parse_args()
    with argbind.scope(args):
        run(verbose=True)


if __name__ == "__main__":
    main_func()
