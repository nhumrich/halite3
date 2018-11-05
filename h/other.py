#!/usr/bin/env python3

import random
import logging
import itertools
from copy import copy
import math
from scipy.constants import G
from queue import PriorityQueue

import hlt
from hlt import constants
from hlt.positionals import Direction, Position

# This game object contains the initial game state.
game = hlt.Game()


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


game.ready("OtherBot")
logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))

num_players = len(game.players)
logging.info(f'{num_players} player mode.')

syp = game.players[game.my_id].shipyard.position

dropoffs = [syp]
collection_per_turn = []

logging.info(syp)
returning = set()


def run():
    global spent_so_far
    while True:
        game.update_frame()
        # You extract player metadata and the updated map metadata here for convenience.
        me = game.me
        game_map = game.game_map

        turns_left = constants.MAX_TURNS - game.turn_number

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
        ship_queue = sorted(ship_queue, key=lambda s: game_map.calculate_distance(s.position, syp),
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
            elif (len(ship_queue) > 15 * len(dropoffs) and
                  game_map.calculate_distance(ship.position, closest_dropoff(ship.position)) > 15 and
                  me.halite_amount > constants.DROPOFF_COST -
                  game_map[ship.position].halite_amount + ship.halite_amount and
                  game.turn_number < constants.MAX_TURNS / 1.7 and
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
            elif ((ship.halite_amount > 900) or
                  (game_map.calculate_distance(ship.position, closest_dropoff(ship.position)) + 4 >=
                   (constants.MAX_TURNS - game.turn_number))):
                returning.add(ship.id)
                ship.returning = True
            elif (ship.halite_amount + (game_map[ship.position].halite_amount * 0.25) > 1000):
                # its not worth staying on the square, just go home
                ship.returning = True
                returning.add(ship.id)

        # mark enemy ships only if 4 players
        if num_players == 4:
            for i in game.players:
                if i == game.my_id:
                    continue
                player = game.players[i]
                for ship in player.get_ships():
                    for d in Direction.get_all_cardinals() + [(0, 0)]:
                        location = game_map.normalize(ship.position.directional_offset(d))
                        if game_map.calculate_distance(location,
                                                       closest_dropoff(ship.position)) <= 4:
                            pass
                        # elif (ship.halite_amount > 950 and
                        #         len(game.players[ship.owner].get_ships()) < len(ship_queue)):
                        # its fine to collide with a high halite ship and steal its halite
                        # pass
                        else:
                            positions_used.add(location)
        # for ship in ship_queue:
        #     if ship.staying:
        #         continue
        #     if (not ship.returning and
        #             game_map[ship.position].halite_amount > constants.MAX_HALITE // 14):
        #         # collect while we are here
        #         move(ship.position, ship.position, ship, positions_used, command_queue)
        #         ship.staying = True

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
            elif (ship.halite_amount + (game_map[ship.position].halite_amount * 0.25) > 900):
                # will staying make me cross over the line?
                ship.staying = True
                move(ship.position, ship.position, ship, positions_used, command_queue)
            else:
                ps = PriorityQueue()
                for x, y in itertools.product(range(ship.position.x-20, ship.position.x+20),
                                              range(ship.position.y-20, ship.position.y+20)):
                    p = game_map.normalize(Position(x, y))
                    if p in destinations:
                        continue
                    cell = game_map[p]
                    hal = cell.halite_amount
                    # if p == ship.position:
                    #     continue
                    if p in dropoffs:
                        # Gravity for the dropoff is equivalent to halite in ship
                        hal = ship.halite_amount
                    # if cell.ship and cell.ship.owner != me.id:
                    #         hal -= 200
                    ps.put(PP(
                        - (0.07 * hal /
                            (game_map.calculate_distance(ship.position, p) + 1) ** 2), p))
                        # - (hal /
                        #    (game_map.calculate_distance(ship.position, p) + 1)), p))

                p = ps.get().position
                if p in dropoffs:
                    # move to drop-off
                    shortest = True
                else:
                    shortest = False
                destinations.add(p)
                move(p, ship.position, ship, positions_used, command_queue, shortest=shortest)

        # Don't spawn a ship if you currently have a ship at port, though - the ships will collide.

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

        logging.info(f'turn {game.turn_number} has acg {avg_per_ship_per_turn}')

        if (6 * turns_left > 1400 and
                # if (turns_left > 175 and
                # if (avg_per_ship_per_turn * turns_left >= 1400 and
                me.halite_amount >= constants.SHIP_COST and
                not game_map[me.shipyard].is_occupied and
                not dropoff and
                syp not in positions_used):
            spent_so_far += constants.SHIP_COST
            command_queue.append(me.shipyard.spawn())

            # Send your moves back to the game environment, ending this turn.
        game.end_turn(command_queue)


if __name__ == '__main__':
    run()

