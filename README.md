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

### Create an election on wildcat connection. 
+ Each ranking should be a different question.
+ It does not matter if multiple questions or ballots are used.
+ No two questions should be named the same.
+ Export Wildcat Connection CSV.
+ **TODO(Leo): Wildcat connection instructions**

### Run on Exported CSV

Let's say our exported CSV has the filepath `wc.csv`. To run IRV on `wc.csv`, enter into your terminal: 
```shell
$ irv wc.csv
```
This will print the Winner and IRV Rounds for each question.
It will also save the winner and rounds into the folder path `--elections_output`, which defaults to `./elections`.

For more information on the flags, run:
```shell
$ irv -h
```

## Future Steps
- Javascript/PHP bindings
- Additional Ranked Choice Voting algorithms
