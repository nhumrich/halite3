#!/usr/bin/env python3

import random
import logging
import itertools
import argparse
import numpy as np

import hlt
from hlt import constants
from hlt.positionals import Direction, Position

##### CONSTANTS
RETURN_AMOUNT = 850
parser = argparse.ArgumentParser(description='')
parser.add_argument('-s', action="store_true", default=False)
# parser.add_argument('-b', action="store", dest="b")
# parser.add_argument('-c', action="store", dest="c", type=int)
ns = parser.parse_args()

NEW_SPAWN = ns.s
NAME = 'NicksBot'
if NEW_SPAWN:
    NAME = 'Alternate'
######

# if not NEW_SPAWN:
#     import pydevd
#     pydevd.settrace('localhost', port=8989, stdoutToServer=True, stderrToServer=True)

# logging.info(f'spawn type: {NEW_SPAWN}')

game = hlt.Game()

logging.info(f'spawn type: {NEW_SPAWN}')
spent_so_far = 0
np.set_printoptions(threshold=np.nan)

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

    if len(moves) == 2:
        # sort by cost
        a = ship.position.directional_offset(moves[0])
        b = ship.position.directional_offset(moves[1])
        costa = game.game_map[a].halite_amount
        costb = game.game_map[b].halite_amount

        if costa > costb and shortest:
            moves[0], moves[1] = moves[1], moves[0]
        if costa < costb and not shortest:
            moves[0], moves[1] = moves[1], moves[0]

    for d in moves:
        if doit(d):
            return
        all_possible.remove(d)

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

        highs = []
        # spots = PriorityQueue()
        for x, y in itertools.product(range(game_map.width), range(game_map.height)):
            highs.append(Position(x, y))

        highs = sorted(highs, key=lambda p: game_map[p].halite_amount, reverse=True)[:150]
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
            if ship.id not in first_seen:
                first_seen[ship.id] = game.turn_number
            ship.staying = False
            ship.returning = False
            if ship.position in destinations:
                del destinations[ship.position]
            if (constants.MAX_TURNS - game.turn_number) < 4 and ship.position in dropoffs:
                # ignore ship completely so that it can die
                ship.staying = True
            # should we build a drop-off?
            elif (len(ship_queue) >= 10 * len(dropoffs) and
                  ship.position in highs and
                  game_map.calculate_distance(ship.position, closest_dropoff(ship.position)) > 15 and
                  me.halite_amount > constants.DROPOFF_COST -
                  game_map[ship.position].halite_amount + ship.halite_amount and
                  game.turn_number < constants.MAX_TURNS * 0.75 and
                  halite_percent > 0.4 and
                  # len(dropoffs) < 4 and
                  not dropoff):
                dropoff = True
                spent_so_far += constants.DROPOFF_COST - game_map[ship.position].halite_amount
                command_queue.append(ship.make_dropoff())
                ship.staying = True
                positions_used.add(ship.position)
            # can it move?
            elif (game_map[ship.position].halite_amount * 0.1) > ship.halite_amount:
                # can't move, stay put
                # logging.info(f'ship {ship.id} staying with {ship.halite_amount} avaliable')
                move(ship.position, ship.position, ship, positions_used, command_queue)
                ship.staying = True
            elif ((ship.halite_amount > RETURN_AMOUNT) or
                  (game_map.calculate_distance(ship.position, closest_dropoff(ship.position)) + 4 >=
                   (constants.MAX_TURNS - game.turn_number))):
                returning.add(ship.id)
                ship.returning = True
            elif (ship.halite_amount + (game_map[ship.position].halite_amount * 0.25) > 1000):
                # its not worth staying on the square, just go home
                ship.returning = True
                returning.add(ship.id)

        # mark enemy ships if we don't control more than half the ships on the board
        total_num_of_ships = 0
        for i in game.players:
            total_num_of_ships += len(game.players[i].get_ships())

        if len(ship_queue) < total_num_of_ships:
            for i in game.players:
                if i == game.my_id:
                    continue
                player = game.players[i]
                for ship in player.get_ships():
                    for d in Direction.get_all_cardinals() + [(0, 0)]:
                        location = game_map.normalize(ship.position.directional_offset(d))
                        if game_map.calculate_distance(location,
                                                       closest_dropoff(ship.position)) <= 1:
                            pass
                        # elif (ship.halite_amount > 950 and
                        #         len(game.players[ship.owner].get_ships()) < len(ship_queue)):
                        # its fine to collide with a high halite ship and steal its halite
                        # pass
                        else:
                            positions_used.add(location)

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

                move(closest_dropoff(ship.position), ship.position, ship, positions_used,
                     command_queue, collide=collide, shortest=True)

        for ship in ship_queue:
            if ship.returning or ship.staying:
                continue
            elif (ship.halite_amount + (game_map[ship.position].halite_amount * 0.25) >
                  RETURN_AMOUNT):
                # will staying make me cross over the line?
                ship.staying = True
                move(ship.position, ship.position, ship, positions_used, command_queue)

            else:
                logging.info(f'd {destinations}')

                highest_so_far = game_map[ship.position].halite_amount
                best = ship.position
                for p in highs:
                    # p = game_map.normalize(p)
                    if p in destinations:
                        continue
                    hal = game_map[p].halite_amount

                    if p in dropoffs:
                        hal = ship.halite_amount

                    weighted = hal / (game_map.calculate_distance(ship.position, p) + 1)
                    if weighted > highest_so_far:
                        best = p
                    if p in destinations and destinations[p] != ship.id:
                        # logging.info(f'nope on {p} for ship {ship.id}')
                        continue

                p = best
                logging.info(f'Ship {ship.id} moving to position {p}')

                if ship.id in ships_des:
                    if ships_des[ship.id] !=p:
                        if ships_des[ship.id] in destinations:
                            del destinations[ships_des[ship.id]]
                        else:
                            logging.info(f'Mismatch. Expected {ships_des[ship.id]} in {destinations}')
                ships_des[ship.id] = p
                destinations[p] = ship.id
                # if p in dropoffs:
                #     p.
                move(p, ship.position, ship, positions_used, command_queue, shortest=False)
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
            avg_per_ship_per_turn = halite_collected / ship_turns / 1.1

        logging.info(f'turn {game.turn_number} has avg {avg_per_ship_per_turn}')

        # if (avg_per_ship_per_turn * turns_left >= 1400 and
        if (
                ((turns_left > 150 and not NEW_SPAWN) or
                 (avg_per_ship_per_turn * turns_left >= 1800 and NEW_SPAWN)) and
                me.halite_amount >= constants.SHIP_COST and
                not dropoff and
                halite_percent > 0.4 and
                syp not in positions_used):
            spent_so_far += constants.SHIP_COST
            command_queue.append(me.shipyard.spawn())

            # Send your moves back to the game environment, ending this turn.
        logging.info(command_queue)
        game.end_turn(command_queue)


if __name__ == '__main__':
    run()

