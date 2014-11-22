#!/usr/bin/env python
from random import randint
from collections import OrderedDict
from copy import copy
import argparse


def roll_die(sides=6):
    """Throw one die and return it's result."""
    return randint(1, sides)


def roll_dice(num=2, sides=6):
    """Throw multiple dice and return their results."""
    return [roll_die(sides) for i in xrange(num)]


def reroll_dice(rerolls=3, num=2, sides=6):
    return [roll_dice(num, sides) for i in xrange(rerolls)]


def keep_sixes(outcome):
    """An example strategy that keeps all dices that land on six."""
    return [d for d in outcome if d == 6]


def keep_none(outcome):
    return []


def keep_unique(outcome):
    return list(set(outcome))


def keep_some_unique(outcome, num=5):
    s = set(outcome)
    while len(s) > num:
        elem = s.pop()
    return list(s)


def count_sixes(listy):
    return listy.count(6)


def count_unique(listy):
    return len(set(listy))


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
        if type(value) == list:
            value = tuple(sorted(value))
        if value in count_dict:
            count_dict[value] += 1
        else:
            count_dict[value] = 0
    ordered_count_dict = OrderedDict(sorted(count_dict.items()))
    return ordered_count_dict


def hist_counts_to_probabilities(hist):
    """Convert a histogram of event counts into probabilities."""
    total = 0
    for k, v in hist.iteritems():
        total += hist[k]
    for k, v in hist.iteritems():
        hist[k] = 100 * (v / float(total))
    return hist


def run_multiple_times_and_print_stats(func, N=100):
    outcomes = run_many_times(func, times=N)
    hist = count_outcomes(outcomes)
    odds = hist_counts_to_probabilities(hist)
    for k, v in odds.iteritems():
        print "%s: %.2f %%" % (k, v)


def parse_args():
    keep_options = {
        "none": keep_none,
        "sixes": keep_sixes,
        "unique": keep_unique
    }

    reduce_options = {
        "none": lambda x: x,
        "count_sixes": count_sixes,
        "count_unique": count_unique
    }

    parser = argparse.ArgumentParser(
        description="Simulating various dice throw situations.")
    parser.add_argument("-n", dest="num", type=int, default=1,
                        help="Specify the number of dice to throw.")
    parser.add_argument("-s", dest="sides", type=int, default=6,
                        help="Specify the number of sides each dice has.")
    parser.add_argument("-ss", dest="multi_sides", nargs="*",
                        help="[TODO] Specify the number of sides for each dice.")
    parser.add_argument("-r", dest="reroll", type=int, default=1,
                        help="Perform multiple rerolls (stats only count last roll).")
    parser.add_argument("--keep", default="none", choices=keep_options.keys(),
                        help="Choose a keeping strategy when performing rerolls.")
    parser.add_argument("--stats", nargs="?", const="none", choices=reduce_options.keys(),
                        help="Performs multiple throws and outputs cumulative results. " + \
                        "Provide a parameter to choose an approach for reducing a dice throw to a single value of interest.", )
    parser.add_argument("-N", type=int, default=1000, metavar="simulations",
                        help="Set the number of simulations to run for statistical results.", )
    args = parser.parse_args()
    print args
    args.keep = keep_options[args.keep]
    if args.stats is not None:
        args.stats = reduce_options[args.stats]

    if args.multi_sides is not None:
        if len(args.multi_sides) != args.num:
            raise Exception("'-ss' parameter has to specify the same number of values as there are dice.")
        for value in args.multi_sides:
            if not value.isdigit():
                raise Exception("'-ss' parameter has to consist of only integer numbers.")

    return args


def main():
    settings = parse_args()

    if settings.stats is not None:
        def perform_roll():
            return settings.stats(
                reroll_dice_with_choice_last_only(
                    keep_strategy=settings.keep,
                    rerolls=settings.reroll,
                    num=settings.num,
                    sides=settings.sides))
        run_multiple_times_and_print_stats(perform_roll, N=settings.N)
    else:
        results = reroll_dice_with_choice(
                    keep_strategy=settings.keep,
                    rerolls=settings.reroll,
                    num=settings.num,
                    sides=settings.sides)
        for result in results:
            print result


if __name__ == "__main__":
    main()
