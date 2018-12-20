from collections import defaultdict

import subprocess
import random
import math
import json
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

        get_constant('return_amount', 400, 1100)
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

    def __repr__(self):
        s = f'name:{self.name}'
        for c in self.constants:
            s += f' {c.name}:{c.val}'
        return s

    def __eq__(self, other):
        return self.constants == other.constants

    def __hash__(self):
        sh = ''
        for c in self.constants:
            sh += str(hash(c))

        return hash(sh)


def do_round(bots: List[Bot]):
    run_string = ['./halite', '--replay-directory', 'replays/', '--width', '40', '--height', '40',
                  '--results-as-json']

    scores = defaultdict(lambda: 0)
    for i in range(len(bots)):
        processes = []
        # we run 4 games total for each pairing, 2 at a single time
        a = bots[i]
        b = bots[i-1]
        for __ in range(3):
            # each bot plays its opponent three times
            bot_strings = []

            for n in [a, b]:
                bot_strings.append('python run.py ' + n.get_string())

            processes.append((a, b, subprocess.Popen(run_string + bot_strings,
                                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)))

        for a, b, p in processes:
            outs, errs = p.communicate()
            results = outs.decode()

            # print(f'{a} vs {b}')
            try:
                response = json.loads(results)
            except json.JSONDecodeError:
                print('error decoding:', results)
                continue

            map = {}
            for k, v in response['stats'].items():
                map[k] = v['score']

            # print(sorted(map.items(), key=lambda d: d[1], reverse=True))
            rank = sorted(map, key=lambda d: map[d], reverse=True)
            # print(rank)
            name_map = {'0': a, '1': b}
            for points, i in enumerate(reversed(rank)):
                scores[name_map[i]] += points

    print(scores)
    final = sorted(scores, key=lambda d: scores[d], reverse=True)
    # print('Winner:', final[0])
    print(final)
    return final


def mutate(seed, name):
    while True:
        bot = seed.mutate(name)
        if bot not in bots_seen:
            return bot


def run_gym():
    # start with random bots
    bots = [Bot(str(i)) for i in range(60)]
    # seed_bot = Bot('0', constants=seed())
    # seed_bot2 = Bot('1', constants=seed())
    while True:
        winners = do_round(bots)[:15]
        for i in range(5):
            mutations = []
            for b in winners:
                for j in range(4):
                    mutations.append(mutate(b, b.name + '-' + str(j)))

            bots = winners + mutations
            while len(winners) > 4:
                random.shuffle(bots)

                winners = do_round(bots)[:(len(bots)//2)]
                bots = winners

        while len(winners) > 1:
            index = (len(winners)//2)
            winners = do_round(winners)[:index]
        print(f'Round Winner: {winners[0]}')
        bots = [mutate(winners[0], winners[0].name + f'-m{i}') for i in range(59)] + winners


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
