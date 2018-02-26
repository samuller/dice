#!/usr/bin/env python
"""A command-line tool for simulating various dice throw situations.

Copyright (C) 2014  Simon Muller

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
"""
import sys
import argparse
import random
from collections import OrderedDict
from copy import copy
__author__ = "Simon Muller"
__copyright__ = "Copyright 2014, Simon Muller"


def roll_die(sides=6):
    """Throw one die and return it's result."""
    return random.randint(1, sides)


def roll_dice(num=2, sides=6):
    """Throw multiple dice and return their results."""
    if type(sides) == int:
        return [roll_die(sides) for i in range(num)]
    elif type(sides) == list:
        assert len(sides) == num
        return [roll_die(s) for s in sides]


def reroll_dice(rerolls=3, num=2, sides=6):
    """Performs multiple dice rolls and and returns their results."""
    return [roll_dice(num, sides) for i in range(rerolls)]


def keep_value(outcome, values_of_interest):
    """A keep strategy that keeps all dices that land on the given values."""
    return [d for d in outcome if d in values_of_interest]


def keep_none(outcome, values_of_interest=None):
    """A keep strategy that never keeps any dice."""
    return []


def keep_unique(outcome, values_of_interest=None):
    """A keep strategy that throws away duplicates."""
    return list(set(outcome))


def keep_duplicates(outcome, values_of_interest=None):
    """A keep strategy that keeps only duplicates."""
    return [d for d in outcome if outcome.count(d) > 1]


def keep_some_unique(outcome, num=5):
    """A keep strategy that throws away duplicates, but never keeps more than 'num' dice."""
    s = set(outcome)
    while len(s) > num:
        elem = s.pop()
    return list(s)


def order_dice(outcome, values_of_interest):
    """A reduction function for a set of dice values where order doesn't matter."""
    if len(values_of_interest) == 0:
        return tuple(sorted(outcome))

    for value in copy(outcome):
        # Completely ignore dice that don't have values of interest
        if value not in values_of_interest:
            outcome.remove(value)
    return tuple(sorted(outcome))


def count_unique(outcome, values_of_interest):
    """A reduction function for counting how many values are unique."""
    return len(set(outcome))


def sum_values(outcome, values_of_interest):
    """A reduction function for summing the values in a result."""
    if len(values_of_interest) == 0:
        return sum(outcome)
    # Only sum dice with values of interest
    total = 0
    for value in values_of_interest:
        total += outcome.count(value) * value
    return total


def count_values(outcome, values_of_interest):
    """A reduction function for counting the number of given values on a result."""
    count = 0
    for value in values_of_interest:
        count += outcome.count(value)
    return count


def dice_throw(outcome, values_of_interest):
    """A reduction function that keeps the precise result of the dice throws (including order)."""
    return tuple(outcome)


def reroll_dice_with_choice(keep_strategy=keep_none, rerolls=3, num=2, sides=6):
    """Perform multiple rerolls, but with the choice to keep some dice the same
    and reroll all the others. Return all rolls."""
    outcomes = []
    outcomes.append(roll_dice(num, sides))
    for i in range(rerolls - 1):
        prev_outcome = copy(outcomes[-1])
        to_keep = keep_strategy(prev_outcome)
        new_outcome = []
        for d in to_keep:
            if d in prev_outcome:
                new_outcome.append(d)
                prev_outcome.remove(d)
            else:
                assert False, "Keep_strategy() result is corrupt: %s for %s" % \
                              (to_keep, outcome)
        new_outcome.extend(roll_dice(num - len(new_outcome), sides))
        outcomes.append(new_outcome)
    return outcomes


def reroll_dice_with_choice_last_only(keep_strategy=keep_none, rerolls=3, num=2, sides=6):
    """Perform multiple rerolls with choice, but only return the final result."""
    outcomes = reroll_dice_with_choice(keep_strategy, rerolls, num, sides)
    outcome = outcomes[-1]
    return outcome


def reduce_many_dice_rolls(action=sum, times=100, num=2, sides=6):
    """Roll multiple dice many times and each time perform some action
    on the dice to calculate a single value. Return results as a generator."""
    return (action(roll_dice(num, sides)) for i in range(times))


def run_many_times(func, times=100):
    """Create a generator that returns the result of running the given function
    multiple times."""
    return (func() for i in range(times))


def count_outcomes(values):
    """Count the number of identical outcomes and return histogram."""
    count_dict = {}
    for value in values:
        # The outcome values have to be hashable to be inserted into dict
        # Outcomes containing lists should therefore be converted to tuples
        if value in count_dict:
            count_dict[value] += 1
        else:
            count_dict[value] = 1
    return count_dict


def count_total_events(hist):
    """Sum the number of values in a histogram (which are values in a dictionary)."""
    total = 0
    # Count total number of events
    for key in hist:
        total += hist[key]
    return total


def hist_counts_to_probabilities(hist):
    """Convert a histogram of event counts into probabilities."""
    total = count_total_events(hist)
    # Divide number of events by total to get probabilities
    for k, v in hist.iteritems():
        hist[k] = (v / float(total))
    return hist


def run_multiple_times_and_print_stats(func, N=100, use_percentages=False):
    """Run a function N times and print out a histogram of the results."""
    outcomes = run_many_times(func, times=N)
    hist = count_outcomes(outcomes)

    if use_percentages:
        odds = hist_counts_to_probabilities(hist)
        # Use an ordered dict so that we can print with sorted keys
        odds = OrderedDict(sorted(odds.items()))
        for k, v in odds.iteritems():
            # Print probabilities as percentages
            print("%s: %.2f %%" % (k, 100*v))
    else:
        total = count_total_events(hist)
        # Use an ordered dict so that we can print with sorted keys
        hist = OrderedDict(sorted(hist.items()))
        for k, v in hist.iteritems():
            print("%s: %d out of %d" % (k, v, total))


REDUCE_ARG_OPTIONS = {
    "sum": (sum_values, "total sum of dice values in a throw"),
    "order": (order_dice, "ordered dice values"),
    "count": (count_values, "number of dice with the value %s"),
    "unique": (count_unique, "number of unique dice in a throw"),
    "values": (dice_throw, "dice values"),
}


def parse_arg_reduce_function(args):
    """Parse command-line arguments for the reduce function."""

    if len(args) == 0:
        args = ["sum"]

    if args[0] in REDUCE_ARG_OPTIONS:
        func = REDUCE_ARG_OPTIONS[args[0]][0]
        details = REDUCE_ARG_OPTIONS[args[0]][1]
    else:
        raise Exception("'--stats' parameter has to specify a valid reduction function, " +
                        " not '%s'. Valid options are: %s" % (args[0], REDUCE_ARG_OPTIONS.keys()))
    reduce_args = []
    for arg in args[1:]:
        reduce_args.append(int(arg))

    return func, reduce_args, (details % reduce_args)


KEEP_ARG_OPTIONS = {
    "none": keep_none,
    "value": keep_value,
    "unique": keep_unique,
    "duplicate": keep_duplicates,
}


def parse_arg_keep_function(args):
    """Parse command-line arguments for the keep strategy."""

    if args is None or len(args) == 0:
        args = ["none"]

    if args[0] in KEEP_ARG_OPTIONS:
        func = KEEP_ARG_OPTIONS[args[0]]
    else:
        raise Exception("'--keep' parameter has to specify a valid keep strategy, " +
                        " not '%s'. Valid options are: %s" % (args[0], KEEP_ARG_OPTIONS.keys()))

    keep_args = []
    for arg in args[1:]:
        keep_args.append(int(arg))

    return func, keep_args


def parse_args():
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        description="Simulate various dice throw situations.", add_help=False)
    parser.add_argument("-h", "--help", action="help", help="Show this help message and exit.")
    parser.add_argument("-n", dest="num", type=int, default=1,
                        help="Specify the number of dice to throw.")
    parser.add_argument("-s", dest="sides", type=int, default=6,
                        help="Specify the number of sides all dice have.")
    parser.add_argument("-ss", dest="multi_sides", type=int, nargs="*", metavar="SIDES",
                        help="Specify the number of sides for each individual die.")
    parser.add_argument("-r", dest="reroll", type=int, default=1,
                        help="Perform multiple rerolls (stats only count last roll).")
    parser.add_argument("--keep", nargs="*", metavar="STRATEGY",
                        help="Choose a keeping strategy when performing rerolls. Options are: %s." %
                             (KEEP_ARG_OPTIONS.keys(),))
    parser.add_argument("--stats", nargs="*", metavar="REDUCE",
                        help="Performs multiple throws and outputs cumulative results. " +
                        "Provide a parameter to choose an approach for reducing a " +
                        "dice throw to a single value of interest. Options are: %s." %
                        (REDUCE_ARG_OPTIONS.keys(),))
    parser.add_argument("-N", type=int, default=1000, metavar="SIMULATIONS",
                        help="Set the number of simulations to run for statistical results.", )
    parser.add_argument("--counts", default=False, action="store_true",
                        help="Print actual event counts instead of percentages in the statistical results.", )
    parser.add_argument("--seed", type=int,
                        # "Set the seed value used for randomizing results."
                        help=argparse.SUPPRESS)
    args = parser.parse_args()

    if args.multi_sides is not None:
        if len(args.multi_sides) != args.num:
            raise Exception("'-ss' parameter has to specify the same number of values as there are dice.")
        args.sides = args.multi_sides

    args.keep = parse_arg_keep_function(args.keep)

    if args.stats is not None:
        args.stats = parse_arg_reduce_function(args.stats)

    if args.seed is not None:
        random.seed(args.seed)

    return args


def main():
    settings = parse_args()

    def keep_strategy(outcome):
        return settings.keep[0](
            outcome,
            settings.keep[1] if len(settings.keep) > 1 else None
        )

    def reduce_func(outcome):
        return settings.stats[0](
            outcome,
            settings.stats[1] if len(settings.stats) > 1 else None
        )

    if settings.stats is not None:
        # Perform multiple simulations and output statistical results
        def perform_roll():
            return reduce_func(
                reroll_dice_with_choice_last_only(
                    keep_strategy=keep_strategy,
                    rerolls=settings.reroll,
                    num=settings.num,
                    sides=settings.sides),
            )
        print("%s:" % settings.stats[2].capitalize())
        run_multiple_times_and_print_stats(perform_roll,
                                           N=settings.N,
                                           use_percentages=not settings.counts)
    else:
        # Perform a single simulation and output results
        results = reroll_dice_with_choice(
            keep_strategy=keep_strategy,
            rerolls=settings.reroll,
            num=settings.num,
            sides=settings.sides)
        for result in results:
            print("%s" % (result))


if __name__ == "__main__":
    main()
