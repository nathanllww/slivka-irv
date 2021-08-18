# Script to run irv test
# Each input file is expected to end with
#   winner,[name of winner]
# This script will then check if results match, and print those that don't
# If a test failes, will also print steps
#
# Syntax
# ======
#   python test_irv.py [OPTIONS] FILE ...
#
# OPTIONS
# =======
#   --verbose
#       print certain additional progress info
#
#   --remove_exhausted_ballots, --reb
#       Do NOT require 50% of total ballots cast to win;
#       the candidate remaining at the end of the IRV always wins.
#       Default behavior (without this flag) is to treat exhuasted ballots as
#       votes of no confidence.
#
#   --no_fail_exit, --nfe
#       Do not exit on a failed test, and instead continue through the other tests
#
# FILE FORMAT
# ===========
#   This scripts excepts the normal ``ballot format'' (see irv.py), but also requires
#   the last row be a "winner ballot" in order to check the IRV script.
#   This "winner ballot" should have the  following format:
#       winner,[name of winner]
#   For example, if candidate A should win, then the last line of the input file should be
#       winner,A
#   To test for a tie or no confidence result, use winner name "tie" or "No Confidence"; i.e.
#       winner,tie
#

import sys
import irv

# FUNCTIONS
# =========

def fail(message, steps):
    pred(f"Fail: ")
    print(message)
    print("Steps:")
    print(f"{steps}")

    if exit_on_fail:
        sys.exit(2)
    else:
        global failed
        failed = True

def pred(skk): print("\033[91m{}\033[00m".format(skk), end="")
def pgreen(skk): print("\033[92m{}\033[00m".format(skk), end="")

# SCRIPT
# ======

# First, process arguments
verbose = False
remove_exhausted_ballots = False
exit_on_fail = True

sys.argv.pop(0) # remove the "run_irv.py" arg
nargs = len(sys.argv)

special_args = 0
while special_args < nargs and sys.argv[special_args][:2] == '--':
    special_args += 1

if nargs < 1 or special_args == nargs:
    pred("Error: ")
    print("At least one input file is required; see test_irv.py for running info")
    sys.exit(1)

for i in range(special_args):
    if sys.argv[i] == '--verbose':
        verbose = True
    elif sys.argv[i] == '--no_fail_exit' or sys.argv[i] == '--nfe':
        exit_on_fail = False
    elif sys.argv[i] == '--remove_exhausted_ballots' or sys.argv[i] == '--reb':
        remove_exhausted_ballots = True
    else:
        pred("Error: ")
        print(f"Unsupport argument {sys.argv[i]}")
        sys.exit(1)

files = sys.argv[special_args:]

# Now that arguments are loaded, start running files
if verbose:
    print(f"Starting to run elections on files {files}")

failed = False
for f in files:
    if verbose:
        print(f"\nRunning on {f}...")

    irv_elec = irv.IRVElection(f, verbose=verbose, remove_exhausted_ballots=remove_exhausted_ballots)
    if irv_elec.ballots[-1,0] != 'winner':
        pred("Error: ")
        print(f"{f} lacks winner ballot, last row is {irv_elec.ballots[-1,:]}")
        print("See test_irv.py for details of excepted format")
        sys.exit(1)

    real_winner = irv_elec.ballots[-1,1]
    irv_elec.ballots = irv_elec.ballots[:-1,:]
    irv_elec.candidates.remove('winner')
    if real_winner == 'tie' or real_winner == 'No Confidence':
        irv_elec.candidates.remove(real_winner)
    try:
        if real_winner == 'tie':
            erred = False
            try:
                winner, steps = irv_elec.run()
            except ValueError as e:
                pgreen("Success: ")
                print(f"{f} (ValueError with {str(e)})")
                erred = True
            if not erred:
                fail(f"{f} should tie, but IRV returns {winner}", steps)
        else:
            winner, steps = irv_elec.run()
            if winner != real_winner:
                fail(f"{f} has real winner {real_winner}, but IRV returns {winner}", steps)
            else:
                pgreen(f"Success: ")
                print(f"{f}")
    except ValueError as e: # all other errors, don't catch for stacktrace and ``unskipability''
        fail(f"ValueError with {str(e)}", None)

if failed:
    sys.exit(2)


