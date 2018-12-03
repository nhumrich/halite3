
import subprocess
import random
import math
import json
import boto
from typing import List


bots_seen = set()

MUTATE_RATE = 0.1


class Constant:
    def __init__(self, name, min, max, *, val=None):
        self.name = name
        self.min = min
        self.max = max

        if val is None:
            if isinstance(self.min, int):
                self.val = random.randint(self.min, self.max)
            elif isinstance(self.min, float):
                self.val = round(random.uniform(self.min, self.max), 1)
            else:
                self.val = 0
        else:
            self.val = val

    def mutate(self):
        range_ = self.max - self.min
        if isinstance(self.min, int):
            adaption = math.ceil(range_ * MUTATE_RATE)
            newval = random.randint(
                max(self.val - adaption, self.min),
                min(self.val + adaption, self.max))
        elif isinstance(self.min, float):
            adaption = min(round(range_ * 0.1, 1), MUTATE_RATE)
            newval = round(random.uniform(
                max(self.val - adaption, self.min),
                min(self.val + adaption, self.max)), 1)
        else:
            raise NotImplementedError

        return Constant(self.name, self.min, self.max, val=newval)

    def __eq__(self, other):
        return self.val == other.val

    def __hash__(self):
        return hash(self.val)


class Bot:
    def __init__(self, name, constants=None):
        self.name = name
        if constants is not None:
            self.constants = constants
            return

        self.constants = []

        def get_constant(name, a, b):
            constant = Constant(name, a, b)
            self.constants.append(constant)
            return constant

        # get_constant('return_amount', 500, 1000)
        get_constant('look_amount', 10, 300)
        get_constant('so_look_amount', 2, 200)
        get_constant('ship_do_ratio', 5, 30)
        get_constant('do_distance', 1, 50)
        get_constant('do_turn_factor', 0.1, 1.0)
        get_constant('do_halite_factor', 0.1, 0.9)
        get_constant('distance_factor', 0.1, 5.0)
        get_constant('stay_factor', 0.1, 16.0)
        # get_constant('enemy_factor', 0.0, 3.0)
        get_constant('build_factor', 800, 4000)
        get_constant('build_halite_limit', 0.1, 0.9)

    def mutate(self, name=None):
        newconstants = [c.mutate() for c in self.constants]

        if name is None:
            name = self.name

        return Bot(name, constants=newconstants)

    def get_string(self):
        s = f'--name {self.name} '
        for c in self.constants:
            s += f'--{c.name} {c.val} '
        return s

    def __str__(self):
        return self.get_string()

    def __eq__(self, other):
        return self.constants == other.constants

    def __hash__(self):
        sh = ''
        for c in self.constants:
            sh += str(hash(c))

        return hash(sh)


def do_round(bots: List[Bot]):

    run_string = ['./halite', '--replay-directory', 'replays/', '--width', '32', '--height', '32', '--results-as-json']
    command = 'python3 run.py '


    for b in bots:
        print(b)
        bot_line = command
        run_string.append(command + b.get_string())

    scores = {'0': 0, '1': 0, '2': 0, '3': 0}
    for _ in range(2):
        # we run 4 games total for each pairing, 2 at a single time
        processes = []
        for __ in range(2):
            # we can play two games at once
            processes.append(subprocess.Popen(run_string, stdout=subprocess.PIPE, stderr=subprocess.PIPE))

        for p in processes:
            outs, errs = p.communicate()
            results = outs.decode()
            j = json.loads(results)
            # print(j['stats'])
            map = {}
            rank = []
            for k, v in j['stats'].items():
                map[k] = v['score']

            print(sorted(map.items(), key=lambda d: d[1], reverse=True))
            rank = sorted(map, key=lambda d: map[d], reverse=True)
            # print(rank)
            for points, i in enumerate(reversed(rank)):
                scores[i] = scores[i] + points

    print(scores)
    final = sorted(scores, key=lambda d: scores[d], reverse=True)
    print('Winner:', final[0])
    return final[0], final[1]


def mutate(seed, name):
    while True:
        bot = seed.mutate(name)
        if bot not in bots_seen:
            return bot


def run_gym():
    # start with random bots
    seed_bot = Bot('0', constants=seed())
    bot1 = mutate(seed_bot, '1')
    while True:
        bot1 = mutate(seed_bot, '1')
        bot2 = mutate(seed_bot, '2')
        bot3 = mutate(Bot('a'), '3')

        bots = [seed_bot, bot1, bot2, bot3]

        winner, second = do_round(bots)

        # winner gets to mutate
        winning_bot, *losers = [b for b in bots if b.name == winner]
        bot1, *others = [b for b in bots if b.name == second]
        winning_bot.name = '0'

        bot1.name = '1'

        seed_bot = winning_bot

        for b in losers:
            bots_seen.add(b)


def seed():
    constants = []
    # constants.append(Constant('return_amount', 500, 1000, val=850))
    constants.append(Constant('look_amount', 100, 300, val=200))
    constants.append(Constant('so_look_amount', 2, 200, val=50))
    constants.append(Constant('ship_do_ratio', 5, 30, val=15))
    constants.append(Constant('do_distance', 1, 50, val=15))
    constants.append(Constant('do_turn_factor', 0.1, 1.0, val=0.4))
    constants.append(Constant('do_halite_factor', 0.1, 0.9, val=0.5))
    constants.append(Constant('distance_factor', 0.1, 5.0, val=1.0))
    constants.append(Constant('stay_factor', 0.1, 16.0, val=1.0))
    # constants.append(Constant('enemy_factor', 0.0, 3.0, val=1.0))
    constants.append(Constant('build_factor', 800, 4000, val=1500))
    constants.append(Constant('build_halite_limit', 0.1, 0.9, val=0.5))
    return constants


if __name__ == '__main__':
    run_gym()
