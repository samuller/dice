Intro
-----

A small script for running simulations with dice throws, including situations
where you get multiple rerolls and can decide which dice to keep or reroll.

Usage
-----

    usage: dice.py [-h] [-n NUM] [-s SIDES] [-ss [SIDES [SIDES ...]]] [-r REROLL]
                   [--keep [STRATEGY [STRATEGY ...]]]
                   [--stats [REDUCE [REDUCE ...]]] [-N SIMULATIONS] [--counts]

    Simulate various dice throw situations.

    optional arguments:
      -h, --help            Show this help message and exit.
      -n NUM                Specify the number of dice to throw.
      -s SIDES              Specify the number of sides all dice have.
      -ss [SIDES [SIDES ...]]
                            Specify the number of sides for each individual die.
      -r REROLL             Perform multiple rerolls (stats only count last roll).
      --keep [STRATEGY [STRATEGY ...]]
                            Choose a keeping strategy when performing rerolls.
                            Options are: ['none', 'unique', 'duplicate', 'value'].
      --stats [REDUCE [REDUCE ...]]
                            Performs multiple throws and outputs cumulative
                            results. Provide a parameter to choose an approach for
                            reducing a dice throw to a single value of interest.
                            Options are: ['count', 'sum', 'unique', 'values',
                            'order'].
      -N SIMULATIONS        Set the number of simulations to run for statistical
                            results.
      --counts              Print actual event counts instead of percentages in
                            the statistical results.

Terminology
-----------
* Keep strategy: 
  a strategy used to decide which dice to keep between rerolls
* Reduction function: 
  a function for reducing a dice throw result to a single value of interest
