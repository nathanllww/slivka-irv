# Slivka Instant Runoff Voting

This repo contains the logic for Instant Runoff Voting on Wildcat Connection, designed for Slivka Executive Committee Elections, but distributed with the MIT license so any organization may use it.

[Instant Runoff Voting Wikipedia](https://en.wikipedia.org/wiki/Instant-runoff_voting)

[Why](https://www.fairvote.org/rcv#rcvbenefits)
[Instant](https://www.cgpgrey.com/blog/the-alternative-vote-explained.html)
[Runoff](https://www2.isye.gatech.edu/~jjb/papers/stv.pdf)
[Voting?](https://ncase.me/ballot/)

## Installation

Coming soon: non-technical instructions.

Create python >=3.9 environment with the environment manager of your choice. For conda:
```shell
$ conda create -n slivka-irv python=3.9
$ conda activate slivka-irv
```
All the following steps, and running the program, should be done in your newly created environment.
This package is not yet on PyPi. For now, the package should be cloned from Github, then installed.
```shell
$ git clone https://github.com/nathanllww/slivka-irv.git
$ pip install -e slivka-irv
```
Ensure the package is installed correctly.
```shell
$ irv
usage: irv [-h] [--args.save ARGS.SAVE] [--args.load ARGS.LOAD] [--args.debug ARGS.DEBUG]
           [--remove_exhausted_ballots] [--permute] [--log_to_stderr] [--save_log]
           [--ballots_output] [--elections_output ELECTIONS_OUTPUT]
           wc_file
irv: error: the following arguments are required: wc_file
```

## Usage Instructions

### Create an election on Wildcat Connection.
See [here](docs/making_wc_election.md) for detailed instructions on making an election in Wildcat Connection.  Some brief points to rememeber are included below:
+ Each ranking should be a different question.
+ It does not matter if multiple questions or ballots are used.
+ No two questions should be named the same.
+ Export Wildcat Connection CSV.
<!-- + **TODO(Leo): Wildcat connection instructions** -->

### Run on Exported CSV

Let's say our exported CSV has the filepath `wc.csv`. To run IRV on `wc.csv`, enter a shell within your created environment and run:
```shell
$ irv wc.csv
```
This will print the Winner and IRV Rounds for each question.
It will also save the winner and rounds into the folder path `--elections_output`, which defaults to `./elections`.

For more information on the flags, run:
```shell
$ irv -h
```

## Algorithmic Details
This project uses the standard IRV algorithm: for each ballot, give a vote to the highest ranked non-eliminated candidate, and then remove the candidate with the lowest votes.
In addition, if any at any step one candidate has over half the vote, that candidate is automatically declared the winner.

### Ties
In the event that several candidates are tied for last, the algorithm attempts to break the tie as follows:
+ If the sum of votes of the tied candidates in less than the number of votes received by _any_ non-tied candidate, remove all the tied candidates
+ For each tied candidate, the algorithm counts how many people ranked the candidate first, how many ranked them second, etc.  If one tied candidate has less than first choices than the others, they are removed.
In the event of another tie in the number of first choices, the algorithms proceeds to second choice counts, and so on.

Sometimes, both of these methods fail to break tie, in which case the algorithm will report an ''unbreakable tie''

### Exhausted Ballots
By default, exhausted ballots (i.e. ballots on which every ranked candidate has been eliminated) are counted of votes of ''no confidence,'' since a ballot can only be exhausted if a voter does not rank every candidate.
In other words, to win a candidate must receive a tally of at least half of all ballots cast, rather than simply being the only candidate remaining after all others have been eliminated.
To declare the last remaining candidate the winner (or equivalently to remove exhausted ballots), run `irv` with the `--remove_exhausted_ballots` flag.

## Future Steps
- Javascript/PHP bindings
- Additional Ranked Choice Voting algorithms
