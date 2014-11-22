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
    return [[roll_die(num, sides) for i in xrange(num)] for i in xrange(rerolls)]


def strategy_keep_sixes(outcome):
    """An example strategy that keeps all dices that land on six."""
    return [d for d in outcome if d == 6]


def strategy_keep_unique(outcome):
    return list(set(outcome))


def strategy_keep_unique(outcome):
    return list(set(outcome))


def strategy_keep_some_unique(outcome, num=5):
    s = set(outcome)
    while len(s) > num:
        elem = s.pop()
    return list(s)


def reroll_dice_with_choice(keep_strategy=strategy_keep_sixes, rerolls=3, num=2, sides=6):
    """Perform multiple rerolls, but with the choice to keep some dice the same
    and reroll all the others."""
    outcome = roll_dice(num, sides)
    for i in xrange(rerolls):
        to_keep = keep_strategy(outcome)
        new_outcome = []
        for d in to_keep:
            if d in outcome:
                new_outcome.append(d)
                outcome.remove(d)
            else:
                assert False, "Keep_strategy() result is corrupt: %s for %s" % \
                              (to_keep, outcome)
        new_outcome.extend(roll_dice(num - len(new_outcome), sides))
        outcome = new_outcome
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


def count_sixes(listy):
    return listy.count(6)


def count_unique(listy):
    return len(set(listy))


def run_multiple_times_and_print_stats(func, N=100):
    outcomes = run_many_times(func, times=N)
    hist = count_outcomes(outcomes)
    odds = hist_counts_to_probabilities(hist)
    for k, v in odds.iteritems():
        print "%s: %.2f %%" % (k, v)


def run_strat_and_print_process(keep_strategy):
    def keep_strategy_and_print(outcome):
        to_keep = keep_strategy(outcome)
        print "%s -> %s" % (outcome, to_keep)
        return to_keep

    def roll_and_print():
         final_outcome = reroll_dice_with_choice(
                keep_strategy=keep_strategy_and_print,
                rerolls=3, num=6, sides=6)
         print final_outcome
         return count_sixes(final_outcome)

    #run_multiple_times_and_print_stats(roll, N=10000)
    print roll_and_print()


def parse_args():
    parser = argparse.ArgumentParser(
        description='Simulating various dice throw situations.')
    parser.add_argument('--stats', type=int, nargs='?', const=1000,  # action="store_true"
                        help='Performs multiple throws and outputs cumulative results.', )
    parser.add_argument('-s', '--sides', type=int, default=6,
                        help='Specify the number of sides each dice has.')
    parser.add_argument('-n', '--num', type=int, default=2,
                        help='Specify the number of dice to throw.',)
    args = parser.parse_args()
    return args


def main():
    settings = parse_args()

    def roll_sixes():
        return count_sixes(
            reroll_dice_with_choice(
                keep_strategy=strategy_keep_sixes,
                rerolls=3, num=settings.num, sides=settings.sides))
        # return count_sixes(roll_dice(num=6, sides=settings.sides))

    def roll_unique():
        return count_unique(
            # roll_dice(num=6, sides=6))
            reroll_dice_with_choice(
                keep_strategy=strategy_keep_unique,
                rerolls=3, num=settings.num, sides=6))
            # reroll_dice_with_choice(
            #   keep_strategy=strategy_keep_some_unique,
            #   rerolls=3, num=settings.num, sides=settings.sides))

    if settings.stats is not None:
        run_multiple_times_and_print_stats(roll_unique, N=10000)
    else:
        run_strat_and_print_process(strategy_keep_sixes)
        run_strat_and_print_process(strategy_keep_unique)


if __name__ == "__main__":
    main()
