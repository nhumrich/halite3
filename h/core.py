#!/usr/bin/env python3

import random
import logging
from copy import copy
import itertools
import argparse
# import numpy as np

import hlt
# constants = hlt.constants
from hlt import constants
from hlt.positionals import Direction, Position

##### CONSTANTS
# RETURN_AMOUNT = 900
parser = argparse.ArgumentParser(description='')
parser.add_argument('--return_amount', action="store", type=int)
parser.add_argument('--look_amount', action="store", type=int)
parser.add_argument('--so_look_amount', action='store', type=int)
parser.add_argument('--ship_do_ratio', action='store', type=int)
parser.add_argument('--do_distance', action='store', type=int)
parser.add_argument('--do_turn_factor', action='store', type=float)
parser.add_argument('--do_halite_factor', action='store', type=float)
parser.add_argument('--distance_factor', action='store', type=float)
parser.add_argument('--stay_factor', action='store', type=float)
parser.add_argument('--enemy_factor', action='store', type=float)
parser.add_argument('--build_factor', action='store', type=int)
parser.add_argument('--build_halite_limit', action='store', type=float)
parser.add_argument('--name', action='store', type=str)
args = parser.parse_args()

######

game = hlt.Game()
size = game.game_map.width
player_num = len(game.players)

const_dict = {
    2: {
        32: {
        'return_amount': 930,
        'look_amount': 225,
        'so_look_amount': 183,
        'ship_do_ratio': 29,
        'do_distance': 28,
        'do_turn_factor': 0.2,
        'do_halite_factor': 0.8,
        'distance_factor': 2.4,
        'stay_factor': 4.1,
        'enemy_factor': 1.0,
        'build_factor': 1633,
        'build_halite_limit': 0.4
        },
        40: {
            'return_amount': 847,
            'look_amount': 222,
            'so_look_amount': 170,
            'ship_do_ratio': 18,
            'do_distance': 13,
            'do_turn_factor': 0.9,
            'do_halite_factor': 0.7,
            'distance_factor': 3.1,
            'stay_factor': 2.1,
            'enemy_factor': 1.0,
            'build_factor': 3429,
            'build_halite_limit': 0.2
        },
        48: {
            'return_amount': 843,
            'look_amount': 226,
            'so_look_amount': 226,
            'ship_do_ratio': 5,
            'do_distance': 23,
            'do_turn_factor': 0.6,
            'do_halite_factor': 0.7,
            'distance_factor': 3.0,
            'stay_factor': 2.3,
            'enemy_factor': 1.0,
            'build_factor': 1210,
            'build_halite_limit': 0.5
        },
        56: {
            'return_amount': 843,
            'look_amount': 245,
            'so_look_amount': 167,
            'ship_do_ratio': 27,
            'do_distance': 25,
            'do_turn_factor': 0.7,
            'do_halite_factor': 0.2,
            'distance_factor': 1.8,
            'stay_factor': 3.7,
            'enemy_factor': 1.0,
            'build_factor': 2180,
            'build_halite_limit': 0.3
        },
        64: {
            'return_amount': 843,
            'look_amount': 184,
            'so_look_amount': 42,
            'ship_do_ratio': 15,
            'do_distance': 16,
            'do_turn_factor': 0.6,
            'do_halite_factor': 0.1,
            'distance_factor': 0.8,
            'stay_factor': 3.9,
            'enemy_factor': 1.0,
            'build_factor': 1168,
            'build_halite_limit': 0.6
        },},
    4: {
        32: {
            'return_amount': 930,
            'look_amount': 299,
            'so_look_amount': 66,
            'ship_do_ratio': 26,
            'do_distance': 9,
            'do_turn_factor': 0.4,
            'do_halite_factor': 0.9,
            'distance_factor': 1.1,
            'stay_factor': 4.4,
            'enemy_factor': 1.0,
            'build_factor': 1512,
            'build_halite_limit': 0.3

        },
        40: {
            'return_amount': 930,
            'look_amount': 222,
            'so_look_amount': 170,
            'ship_do_ratio': 18,
            'do_distance': 13,
            'do_turn_factor': 0.9,
            'do_halite_factor': 0.7,
            'distance_factor': 3.1,
            'stay_factor': 2.1,
            'enemy_factor': 1.0,
            'build_factor': 3429,
            'build_halite_limit': 0.2
        },
        48: {
            'return_amount': 843,
            'look_amount': 226,
            'so_look_amount': 226,
            'ship_do_ratio': 5,
            'do_distance': 23,
            'do_turn_factor': 0.6,
            'do_halite_factor': 0.7,
            'distance_factor': 3.0,
            'stay_factor': 2.3,
            'enemy_factor': 1.0,
            'build_factor': 1210,
            'build_halite_limit': 0.5
        },
        56: {
            'return_amount': 843,
            'look_amount': 245,
            'so_look_amount': 167,
            'ship_do_ratio': 27,
            'do_distance': 25,
            'do_turn_factor': 0.7,
            'do_halite_factor': 0.2,
            'distance_factor': 1.8,
            'stay_factor': 3.7,
            'enemy_factor': 1.0,
            'build_factor': 2180,
            'build_halite_limit': 0.3
        },
        64: {
            'return_amount': 843,
            'look_amount': 184,
            'so_look_amount': 42,
            'ship_do_ratio': 15,
            'do_distance': 16,
            'do_turn_factor': 0.6,
            'do_halite_factor': 0.1,
            'distance_factor': 0.8,
            'stay_factor': 3.9,
            'enemy_factor': 1.0,
            'build_factor': 1168,
            'build_halite_limit': 0.6
        },
    }
}


def get_constant(name, a, b):
    result = getattr(args, name) or const_dict[player_num][size].get(name)
    # if result is None:
    #     if isinstance(a, int):
    #         result = random.randint(a, b)
    #     elif isinstance(a, float):
    #         result = round(random.uniform(a, b), 1)
    #     else:
    #         return 0
    return result


# RETURN_AMOUNT = get_constant('return_amount', 500, 1000)
RETURN_AMOUNT = 930
LOOK_AMOUNT = get_constant('look_amount', 10, 1000)
SO_LOOK_AMOUNT = get_constant('so_look_amount', 2, 1000)
SHIP_DO_RATIO = get_constant('ship_do_ratio', 5, 30)
DO_DISTANCE = get_constant('do_distance', 1, 50)
DO_TURN_FACTOR = get_constant('do_turn_factor', 0.1, 1.0)
DO_HALITE_FACTOR = get_constant('do_halite_factor', 0.1, 0.9)
DISTANCE_FACTOR = get_constant('distance_factor', 0.1, 5.0)
STAY_FACTOR = get_constant('stay_factor', 0.1, 5.0)
# ENEMY_FACTOR = get_constant('enemy_factor', 0.0, 3.0)
ENEMY_FACTOR = 1
BUILD_FACTOR = get_constant('build_factor', 800, 4000)
BUILD_HALITE_LIMIT = get_constant('build_halite_limit', 0.1, 0.9)


for k, v in copy(locals()).items():
    if k.isupper():
        logging.info(f'{k}:{v}')

if args.name:
    NAME = args.name
else:
    NAME = f'{RETURN_AMOUNT}:{SHIP_DO_RATIO}:{DO_DISTANCE}:{BUILD_FACTOR}'


# if not NEW_SPAWN:
#     import pydevd
#     pydevd.settrace('localhost', port=8989, stdoutToServer=True, stderrToServer=True)

# logging.info(f'spawn type: {NEW_SPAWN}')https://www.brow.sh/

astar_cache = {}

spent_so_far = 0
# np.set_printoptions(threshold=np.nan)

first_seen = {}


def myhash(self):
    return hash((self.x, self.y))


Position.__hash__ = myhash


class PP:
    def __init__(self, priority, position):
        self.priority = priority
        self.position = position

    def __lt__(self, other):
        return self.priority < other.priority


def move(target, source, ship, positions_used, command_queue, collide=False, shortest=False):
    # logging.info(f'moving to {target} from {source}')

    def doit(d):
        po = game.game_map.normalize(ship.position.directional_offset(d))
        # logging.info(f'testing {d}')
        if (collide and po in dropoffs) or po not in positions_used:
            # logging.info(f'ship {ship.id} on {source} next move on {po}')
            positions_used.add(po)
            command_queue.append(ship.move(d))
            # logging.info(command_queue)
            return True
        return False

    all_possible = {(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)}
    moves = game.game_map.get_unsafe_moves(source, target)
    if target == source:
        # stay where we are
        if doit((0, 0)):
            return

    # find cheapest path
    # if shortest:
    #     moves = sorted(moves, key=lambda x: astar(source.directional_offset(x), target),
    #                reverse=not shortest)

    if len(moves) >= 2:
        # sort by cost
        moves = sorted(moves,
                       key=lambda x: game.game_map[
                           ship.position.directional_offset(x)].halite_amount,
                       reverse=not shortest)

    for d in moves:
        if doit(d):
            return
        all_possible.remove(d)

    # if (0, 0) in all_possible:
    #     # try staying put first
    #     if doit((0, 0)):
    #         return
    #
    #     all_possible.remove((0, 0))

    while all_possible:
        d = random.sample(all_possible, 1)[0]
        # d = all_possible.pop()
        if doit(d):
            return
        all_possible.remove(d)

    # welp, we crash
    # logging.info(f'{ship.id} crash')


def closest_dropoff(position):
    min_so_far = 5000
    closest_so_far = None
    for do in dropoffs:
        distance = game.game_map.calculate_distance(position, do)
        if distance < min_so_far:
            min_so_far = distance
            closest_so_far = do
    return closest_so_far


def get_halite_amount():
    hal = 0
    for x, y in itertools.product(range(game.game_map.width), range(game.game_map.height)):
        hal += game.game_map[Position(x, y)].halite_amount
    return hal



num_players = len(game.players)
logging.info(f'{num_players} player mode.')

syp = game.players[game.my_id].shipyard.position

dropoffs = [syp]
collection_per_turn = []

logging.info(syp)
returning = set()

starting_halite_amount = get_halite_amount()

# distance_array = np.array([[abs(i) + abs(j) + 1 for i in range(-20, 21)] for j in range(-20, 21)])
# distance_2 = np.square(distance_array)

game.ready(NAME)
logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))


def run():
    global spent_so_far
    destinations = {}
    ships_des = {}

    while True:
        game.update_frame()
        # You extract player metadata and the updated map metadata here for convenience.
        me = game.me
        game_map = game.game_map

        turns_left = constants.MAX_TURNS - game.turn_number
        halite_left = get_halite_amount()
        halite_percent = halite_left / starting_halite_amount
        # astar_cache.clear()
        highs = []
        # spots = PriorityQueue()
        for x, y in itertools.product(range(game_map.width), range(game_map.height)):
            highs.append(Position(x, y))

        enemy_locations = {ship.position for i in game.players for ship in game.players[i].get_ships() if game.players[i].id != game.my_id}

        highs = sorted(highs, key=lambda p: game_map[p].halite_amount, reverse=True)[:LOOK_AMOUNT]
        do_spots = highs[:SO_LOOK_AMOUNT]
        positions_used = set()
        command_queue = []

        ship_queue = me.get_ships()
        for do in me.get_dropoffs():
            pos = do.position
            if pos not in dropoffs:
                dropoffs.append(pos)

        # top10 = [highs.get().position for _ in range(10)]
        # logging.info(top10)

        # sort ships by proximity to shipyard
        ship_queue = sorted(ship_queue, key=lambda s: game_map.calculate_distance(s.position, syp),
                            reverse=True)
        # ship_queue = sorted(ship_queue, key=lambda s: s.id,
        #                     reverse=True)

        dropoff = False
        for ship in ship_queue:

            # is ship in inspired state?
            num_of_enemies = 0
            for x, y in itertools.product(range(-4, 5), range(-4, 5)):
                pos = ship.position.directional_offset((x,y))
                if pos in enemy_locations:
                    num_of_enemies += 1
                if num_of_enemies >= 2:
                    ship.inspired = True
                    break
            else:
                ship.inspired = False

            ship.collect_amount = game_map[ship.position].halite_amount * .25
            if ship.inspired:
                ship.collect_amount += ship.collect_amount * 2  # inspiration bonus

            if ship.id not in first_seen:
                first_seen[ship.id] = game.turn_number
            ship.staying = False
            ship.returning = False
            if ship.position in destinations:
                s = destinations[ship.position]
                del ships_des[s]
                del destinations[ship.position]
            if (constants.MAX_TURNS - game.turn_number) < 6 and ship.position in dropoffs:
                # ignore ship completely so that it can die
                ship.staying = True
            # should we build a drop-off?
            elif (len(ship_queue) >= SHIP_DO_RATIO * len(dropoffs) and
                  ship.position in do_spots and
                  game_map.calculate_distance(ship.position, closest_dropoff(ship.position)) >
                  DO_DISTANCE and
                  me.halite_amount > constants.DROPOFF_COST -
                  game_map[ship.position].halite_amount + ship.halite_amount and
                  game.turn_number < constants.MAX_TURNS * DO_TURN_FACTOR and
                  halite_percent > DO_HALITE_FACTOR and
                  # len(dropoffs) < 4 and
                  not dropoff):
                dropoff = True
                spent_so_far += constants.DROPOFF_COST - game_map[ship.position].halite_amount
                command_queue.append(ship.make_dropoff())
                ship.staying = True
                positions_used.add(ship.position)
                d = ships_des.pop(ship.id, None)
                destinations.pop(d, None)
            # can it move?
            elif (game_map[ship.position].halite_amount * (1 / constants.MOVE_COST_RATIO)) > ship.halite_amount:
                # can't move, stay put
                # logging.info(f'ship {ship.id} staying with {ship.halite_amount} avaliable')
                move(ship.position, ship.position, ship, positions_used, command_queue)
                ship.staying = True
            elif ((ship.halite_amount > RETURN_AMOUNT) or
                  (game_map.calculate_distance(ship.position,
                                               closest_dropoff(ship.position)) + 6 >=
                   (constants.MAX_TURNS - game.turn_number))):
                returning.add(ship.id)
                ship.returning = True
            elif (ship.halite_amount + ship.collect_amount > 1000):
                # its not worth staying on the square, just go home
                ship.returning = True
                returning.add(ship.id)

        # mark enemy ships if we don't control more than half the ships on the board

        if len(ship_queue) < len(enemy_locations):
            for pos in enemy_locations:
                for d in Direction.get_all_cardinals():
                    location = game_map.normalize(pos.directional_offset(d))
                    if game_map.calculate_distance(location,
                                                   closest_dropoff(pos)) > 1:
                        positions_used.add(location)

        logging.info(enemy_locations)

        for ship in ship_queue:
            if ship.position in dropoffs:
                returning.discard(ship.id)
                ship.returning = False
            elif ship.id in returning and not ship.staying:
                # move to drop-off
                # logging.info('move to dropoff')
                ship.returning = True
                if constants.MAX_TURNS - game.turn_number <= 10:
                    collide = True
                else:
                    collide = False

                d = ships_des.pop(ship.id, None)
                destinations.pop(d, None)

                move(closest_dropoff(ship.position), ship.position, ship, positions_used,
                     command_queue, collide=collide, shortest=True)

        for ship in ship_queue:
            if ship.returning or ship.staying:
                continue
            elif (ship.halite_amount + ship.collect_amount >
                  RETURN_AMOUNT):
                # will staying make me cross over the line?
                ship.staying = True
                move(ship.position, ship.position, ship, positions_used, command_queue)

            else:
                logging.info(f'd {destinations}')
                highest_so_far = ship.collect_amount * STAY_FACTOR
                best = ship.position
                if ship.id in ships_des:
                    p = ships_des[ship.id]  # where I was going
                    w = game_map[p].halite_amount / (
                            game_map.calculate_distance(ship.position, p) * DISTANCE_FACTOR + 1)
                    if p in enemy_locations:
                        w *= ENEMY_FACTOR
                    if w > highest_so_far:
                        best = p
                else:
                    for p in highs:
                        # p = game_map.normalize(p)
                        if p in destinations:
                            continue
                        hal = game_map[p].halite_amount

                        if p in dropoffs:
                            hal = ship.halite_amount

                        weighted = hal / (game_map.calculate_distance(ship.position, p)
                                          * DISTANCE_FACTOR + 1)
                        if weighted > highest_so_far:
                            best = p
                        if p in destinations and destinations[p] != ship.id:
                            # logging.info(f'nope on {p} for ship {ship.id}')
                            continue

                p = best
                logging.info(f'Ship {ship.id} moving to position {p}')

                if ship.id in ships_des:
                    if ships_des[ship.id] != p:
                        if ships_des[ship.id] in destinations:
                            del destinations[ships_des[ship.id]]
                        else:
                            logging.info(
                                f'Mismatch. Expected {ships_des[ship.id]} in {destinations}')
                ships_des[ship.id] = p
                destinations[p] = ship.id
                if p in dropoffs:
                    shortest = True
                else:
                    shortest = False
                move(p, ship.position, ship, positions_used, command_queue, shortest=shortest)
                ''''''

        halite_collected = me.halite_amount + spent_so_far - 5000
        ship_turns = 0
        for id, turn in first_seen.items():
            ship_turns += game.turn_number - turn

        collection_per_turn.append(halite_collected)

        if game.turn_number < 20:
            avg_per_ship_per_turn = 2000
        else:
            # halite_diff = collection_per_turn[game.turn_number - 1] - \
            #               collection_per_turn[game.turn_number - 21]
            avg_per_ship_per_turn = halite_collected / ship_turns

        logging.info(f'turn {game.turn_number} has avg {avg_per_ship_per_turn}')

        # if (avg_per_ship_per_turn * turns_left >= 1400 and
        if ((avg_per_ship_per_turn * turns_left >= BUILD_FACTOR) and
                me.halite_amount >= constants.SHIP_COST and
                not dropoff and
                halite_percent > BUILD_HALITE_LIMIT and
                syp not in positions_used):
            spent_so_far += constants.SHIP_COST
            positions_used.add(syp)
            command_queue.append(me.shipyard.spawn())
            # Send your moves back to the game environment, ending this turn.
        logging.info(command_queue)
        game.end_turn(command_queue)


if __name__ == '__main__':
    run()
