#!/usr/bin/env python3

import random
import logging
import itertools
import argparse
import math
import numpy as np
import scipy as sp
import scipy.signal
from queue import PriorityQueue

import hlt
from hlt import constants
from hlt.positionals import Direction, Position

##### CONSTANTS
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


# This game object contains the initial game state.
game = hlt.Game()

logging.info(f'spawn type: {NEW_SPAWN}')
spent_so_far = 0

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

distance_array = np.array([[abs(i) + abs(j) + 1 for i in range(-20, 21)] for j in range(-20, 21)])
distance_2 = np.square(distance_array)

np.set_printoptions(threshold=np.nan)
npmap = np.array([[game.game_map[Position(x,y)].halite_amount for x in  range(game.game_map.height)] for y in range(game.game_map.width)])
# normed = npmap - np.min(npmap, axis=0)
# normed /= np.ptp(normed, axis=0)

normed = npmap / np.sqrt((np.sum(npmap ** 2)))
convolved = scipy.signal.fftconvolve(npmap, [[1,1,1,1,1],[1,1,1,1,1],[1,1,2,1,1],[1,1,1,1,1],[1,1,1,1,1]])
logging.info(npmap)
logging.info(normed)
logging.info(convolved)
x, y = np.where(convolved == convolved.max())
x, y = x[0], y[0]
logging.info(f'{x}, {y}')
logging.info(game.game_map[Position(x, y)].halite_amount)


game.ready(NAME)
logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))


def run():
    global spent_so_far
    while True:
        game.update_frame()
        # You extract player metadata and the updated map metadata here for convenience.
        me = game.me
        game_map = game.game_map

        turns_left = constants.MAX_TURNS - game.turn_number
        halite_left = get_halite_amount()
        halite_percent = halite_left / starting_halite_amount

        # highs = PriorityQueue()
        # spots = PriorityQueue()
        # for x, y in itertools.product(range(game_map.width), range(game_map.height)):
        #     highs.put(
        #         PP(
        #             (constants.MAX_HALITE - game_map[Position(x, y)].halite_amount * .25) +
        #                 (game_map.calculate_distance(Position(x,y),(0, 0) syp)) * 2,
        #             Position(x, y)))

        positions_used = set()
        destinations = set()
        command_queue = []

        ship_queue = me.get_ships()
        for do in me.get_dropoffs():
            pos = do.position
            if pos not in dropoffs:
                dropoffs.append(pos)

        # top10 = [highs.get().position for _ in range(10)]
        # logging.info(top10)

        # sort ships by proximity to shipyard
        # ship_queue = sorted(ship_queue, key=lambda s: game_map.calculate_distance(s.position, syp),
        #                     reverse=True)
        ship_queue = sorted(ship_queue, key=lambda s: s.id,
                            reverse=True)

        dropoff = False
        for ship in ship_queue:
            if ship.id not in first_seen:
                first_seen[ship.id] = game.turn_number
            ship.staying = False
            ship.returning = False
            if ship.position in destinations:
                destinations.remove(ship.position)
            if (constants.MAX_TURNS - game.turn_number) < 4 and ship.position in dropoffs:
                # ignore ship completely so that it can die
                ship.staying = True
            # should we build a drop-off?
            elif (len(ship_queue) > 12 * len(dropoffs) and
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
            elif ((ship.halite_amount > 850) or
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
            elif ((ship.halite_amount + (game_map[ship.position].halite_amount * 0.25) > 850)): #or
                # game_map[ship.position].halite_amount > constants.MAX_HALITE / 14):
                # will staying make me cross over the line?
                ship.staying = True
                move(ship.position, ship.position, ship, positions_used, command_queue)


            # ships_left = [ship for ship in ship_queue if not ship.staying and not ship.returning]
            # if ships_left:
            #     ps = PriorityQueue()
            #     """a = np.array([(x,y) for x,y in itertools.product(range(ship.position.x-25, ship.position.x+25),
            #                                    range(ship.position.y-25, ship.position.y+25))])
            #
            #     """
            #     for x, y in itertools.product(range(game_map.height), range(game_map.width)):
            #         p = Position(x, y)
            #         if p in dropoffs:distance_array = np.array([[abs(i) + abs(j) for i in range(-20, 21)] for j in range(-20, 21)])
            #             continue
            #
            #         # result = abs(p - closest_dropoff(p))
            #         # a = min(result.x, game_map.width - result.x)
            #         # b = min(result.y, game_map.height - result.y)
            #         # priority = (game_map[p].halite_amount /
            #         #             (math.sqrt(a ** 2 + b ** 2) / 2))
            #         priority = (game_map[p].halite_amount /
            #                     (game_map.calculate_distance(p, closest_dropoff(p)) / 3))
            #         ps.put(PP(- priority, p))
            #
            #     while True:
            #         if ps.empty():
            #             break
            #         # logging.info(f'ships left: {ships_left}')
            #         pp = ps.get()
            #         best_so_far = 10000
            #         current_best = 0
            #         # find closest ship
            #         for ship in ships_left:
            #             distance = game_map.calculate_distance(ship.position, pp.position)
            #             rate = - game_map[ship.position].halite_amount * 1.4
            #             if distance <= best_so_far:
            #                 if rate > pp.priority:
            #                     best_so_far = distance
            #                     current_best = ship
            #         ship = current_best
            #         if ship:
            #             move(pp.position, ship.position, ship, positions_used, command_queue,
            #                  shortest=False)
            #             ships_left.remove(ship)
            #
            #     # logging.info(f'ships left: {ships_left}')
            #     for ship in ships_left:
            #         # logging.info(f'ship left {ship}')
            #         move(ship.position, ship.position, ship, positions_used, command_queue)

            else:
                halite_grid = [[0] * 41] * 41
                for x, y in itertools.product(range(ship.position.x-20, ship.position.x+21),
                                              range(ship.position.y-20, ship.position.y+21)):
                    p = game_map.normalize(Position(x, y))
                    if p in destinations:
                        continue
                    cell = game_map[p]
                    hal = cell.halite_amount
                    best_so_far = 0
                    # if p == ship.position:
                    #     continue
                    # if p in dropoffs:
                    # Gravity for the dropoff is equivalent to halite in ship
                    # hal = ship.halite_amount
                    # if cell.ship and cell.ship.owner != me.id:
                    #         hal -= 200
                    # p_val = (0.07 * hal /
                    #         (game_map.calculate_distance(ship.position, p) + 1) ** 2)
                    halite_grid[x - ship.position.x - 20][y - ship.position.y - 20] = hal
                    # p_val = (hal /
                    #          (game_map.calculate_distance(ship.position, p) + 1))
                    # if p_val > best_so_far:
                    #     best_so_far = p_val
                    #     current_best = p

                hal_ar = np.array(halite_grid)
                grav = hal_ar / distance_2
                # grav = grav / distance_array

                u = Direction.North, grav[:21,:]
                d = Direction.South, grav[20:,:]
                l = Direction.West, grav[:,:21]
                r = Direction.East, grav[:,20:]


                moves = [(Direction.Still, game_map[ship.position].halite_amount)]
                for dir, g in (u,d,l,r):
                    n = np.linalg.norm(g)
                    moves.append((dir, n))

                moves = sorted(moves, key=lambda x: x[1], reverse=True)
                logging.info(f'moves {moves}')
                for d, _ in moves:
                    p = ship.position.directional_offset(d)
                    if p not in positions_used:
                        if p in dropoffs:
                            # move to drop-off
                            shortest = True
                        else:
                            shortest = False
                        move(p, ship.position, ship, positions_used, command_queue, shortest=shortest)
                        break
                else:
                    move(ship.position, ship.position, ship, positions_used, command_queue)

                # logging.info(halite_grid)

                # p = ps.get().position
                # p = current_best

                # destinations.add(p)
                # move(p, ship.position, ship, positions_used, command_queue, shortest=shortest)
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
            avg_per_ship_per_turn = halite_collected / ship_turns / 1.2

        logging.info(f'turn {game.turn_number} has avg {avg_per_ship_per_turn}')

        # if (turns_left > 175 and        # Don't spawn a ship if you currently have a ship at port, though - the ships will collide.
        # if (avg_per_ship_per_turn * turns_left >= 1400 and
        if (
                ((6 * turns_left > 1400 and not NEW_SPAWN) or
                 (avg_per_ship_per_turn * turns_left >= 1800 and NEW_SPAWN)) and
                me.halite_amount >= constants.SHIP_COST and
                not dropoff and
                halite_percent > 0.5 and
                syp not in positions_used):
            spent_so_far += constants.SHIP_COST
            command_queue.append(me.shipyard.spawn())

            # Send your moves back to the game environment, ending this turn.
        logging.info(command_queue)
        game.end_turn(command_queue)


if __name__ == '__main__':
    run()

