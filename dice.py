#!/usr/bin/env python
import sys
if sys.version_info.major != 2:
    raise Exception("Only Python version 2 supported, not %s." %
                    ".".join(map(str, sys.version_info[0:3])))
from random import randint
from collections import OrderedDict
from copy import copy
import argparse


def roll_die(sides=6):
    """Throw one die and return it's result."""
    return randint(1, sides)


def roll_dice(num=2, sides=6):
    """Throw multiple dice and return their results."""
    if type(sides) == int:
        return [roll_die(sides) for i in xrange(num)]
    elif type(sides) == list:
        assert len(sides) == num
        return [roll_die(s) for s in sides]


def reroll_dice(rerolls=3, num=2, sides=6):
    """Performs multiple dice rolls and and returns their results."""
    return [roll_dice(num, sides) for i in xrange(rerolls)]


def keep_sixes(outcome):
    """A keep strategy that keeps all dices that land on six."""
    return [d for d in outcome if d == 6]


def keep_none(outcome):
    """A keep strategy that never keeps any dice."""
    return []


def keep_unique(outcome):
    """A keep strategy that throws away duplicates."""
    return list(set(outcome))


def keep_some_unique(outcome, num=5):
    """A keep strategy that throws away duplicates, but never keeps more than 'num' dice."""
    s = set(outcome)
    while len(s) > num:
        elem = s.pop()
    return list(s)


def order_dice(outcome, values_of_interest):
    """A reduction function for a set of dice values where order doesn't matter."""
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


def reroll_dice_with_choice(keep_strategy=keep_sixes, rerolls=3, num=2, sides=6):
    """Perform multiple rerolls, but with the choice to keep some dice the same
    and reroll all the others. Return all rolls."""
    outcomes = []
    outcomes.append(roll_dice(num, sides))
    for i in xrange(rerolls - 1):
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


def reroll_dice_with_choice_last_only(keep_strategy=keep_sixes, rerolls=3, num=2, sides=6):
    """Perform multiple rerolls with choice, but only return the final result."""
    outcomes = reroll_dice_with_choice(keep_strategy, rerolls, num, sides)
    outcome = outcomes[-1]
    return outcome


def reduce_many_dice_rolls(action=sum, times=100, num=2, sides=6):
    """Roll multiple dice many times and each time perform some action
    on the dice to calculate a single value. Return results as a generator."""
    return (action(roll_dice(num, sides)) for i in xrange(times))


def run_many_times(func, times=100):
    """Create a generator that returns the result of running the given function
    multiple times."""
    return (func() for i in xrange(times))


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
            print "%s: %.2f %%" % (k, 100*v)
    else:
        total = count_total_events(hist)
        # Use an ordered dict so that we can print with sorted keys
        hist = OrderedDict(sorted(hist.items()))
        for k, v in hist.iteritems():
            print "%s: %d out of %d" % (k, v, total)


def parse_arg_reduce_function(args):
    reduce_options = {
        "sum": sum_values,
        "order": order_dice,
        "count": count_values,
        "unique": count_unique,
        # "combination": order_dice,
    }
    if args == []:
        args = ["sum"]

    if args[0] in reduce_options:
        func = reduce_options[args[0]]
    else:
        raise Exception("'--stats' parameter has to specify a valid reduction function, " +
                        " not '%s'. Valid options are: %s" % (args[0], reduce_options.keys()))
    reduce_args = []
    for arg in args[1:]:
        reduce_args.append(int(arg))

    return func, reduce_args


def parse_args():
    keep_options = {
        "none": keep_none,
        "sixes": keep_sixes,
        "unique": keep_unique,
    }

    parser = argparse.ArgumentParser(
        description="Simulating various dice throw situations.")
    parser.add_argument("-n", dest="num", type=int, default=1,
                        help="Specify the number of dice to throw.")
    parser.add_argument("-s", dest="sides", type=int, default=6,
                        help="Specify the number of sides all dice have.")
    parser.add_argument("-ss", dest="multi_sides", type=int, nargs="*", metavar="SIDES",
                        help="Specify the number of sides for each individual die.")
    parser.add_argument("-r", dest="reroll", type=int, default=1,
                        help="Perform multiple rerolls (stats only count last roll).")
    parser.add_argument("--keep", default="none", choices=keep_options.keys(),
                        help="Choose a keeping strategy when performing rerolls.")
    parser.add_argument("--stats", nargs="*",
                        help="Performs multiple throws and outputs cumulative results. " +
                        "Provide a parameter to choose an approach for reducing a dice throw to a single value of interest.", )
    parser.add_argument("-N", type=int, default=1000, metavar="simulations",
                        help="Set the number of simulations to run for statistical results.", )
    parser.add_argument("--counts", default=False, action="store_true",
                        help="Print actual event counts instead of percentages in the statistical results.", )
    args = parser.parse_args()
    print args
    args.keep = keep_options[args.keep]

    if args.stats is not None:
        args.stats = parse_arg_reduce_function(args.stats)

    if args.multi_sides is not None:
        if len(args.multi_sides) != args.num:
            raise Exception("'-ss' parameter has to specify the same number of values as there are dice.")
        args.sides = args.multi_sides

    return args


def main():
    settings = parse_args()

    if settings.stats is not None:
        # Perform multiple simulations and output statistical results
        def perform_roll():
            return settings.stats[0](
                reroll_dice_with_choice_last_only(
                    keep_strategy=settings.keep,
                    rerolls=settings.reroll,
                    num=settings.num,
                    sides=settings.sides),
                settings.stats[1] if len(settings.stats) == 2 else None)
        run_multiple_times_and_print_stats(perform_roll,
                                           N=settings.N,
                                           use_percentages=not settings.counts)
    else:
        # Perform a single simulation and output results
        results = reroll_dice_with_choice(
            keep_strategy=settings.keep,
            rerolls=settings.reroll,
            num=settings.num,
            sides=settings.sides)
        for result in results:
            print result


if __name__ == "__main__":
    main()
