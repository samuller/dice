Dice
====

[![PyPI Version](https://img.shields.io/pypi/v/dice-sim)](https://pypi.org/project/dice-sim/)

A small script for running simulations with dice throws, including situations
where you get multiple rerolls and can decide which dice to keep or reroll.

Terminology
-----------

* Keep strategy:
  a strategy used to decide which dice to keep between rerolls
* Reduction function:
  a function for reducing a dice throw result to a single value of interest

Usage
-----

    usage: dice [-h] [-n NUM] [-s SIDES] [-ss [SIDES [SIDES ...]]] [-r REROLL]
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

Examples
--------

    dice
    [6]

    dice -n 2
    [6, 5]

    dice -n 2 --stats sum
    Total sum of dice values in a throw:
    2: 2.50 %
    3: 4.50 %
    4: 7.70 %
    5: 11.20 %
    6: 14.70 %
    7: 19.20 %
    8: 13.40 %
    9: 9.80 %
    10: 8.40 %
    11: 5.60 %
    12: 3.00 %

    dice -n 2 --stats count 1 6
    Number of dice with the value [1, 6]:
    0: 44.80 %
    1: 43.60 %
    2: 11.60 %

    dice -n 6 -r 3
    [6, 5, 3, 2, 4, 3]
    [5, 2, 3, 4, 6, 4]
    [2, 5, 4, 2, 6, 6]

    dice -n 6 -r 3 --keep value 3
    [6, 5, 3, 2, 4, 3]
    [3, 3, 5, 2, 3, 4]
    [3, 3, 3, 6, 4, 2]

    dice -n 6 -r 3 --keep value 3 --stats count 3
    Number of dice with the value [3]:
    0: 4.50 %
    1: 16.30 %
    2: 26.70 %
    3: 31.20 %
    4: 15.70 %
    5: 5.10 %
    6: 0.50 %

Installation
------------

    sudo pip install dice-sim

Development
-----------

    python setup.py bdist_wheel --universal

And run `./dice.py` directly instead of the global `dice` script.
