#!/usr/bin/env python3

import random
import logging
import itertools
from copy import copy
import math
from scipy import constants
from queue import PriorityQueue

import hlt
from hlt import constants
from hlt.positionals import Direction, Position

# This game object contains the initial game state.
game = hlt.Game()


class PP:
    def __init__(self, priority, position):
        self.priority = priority
        self.position = position

    def __lt__(self, other):
        return self.priority < other.priority


def move(target, source, ship, positions_used, command_queue, collide=Position(-5, -5), shortest=False):
    # logging.info(f'moving to {target} from {source}')

    def doit(d):
        po = game.game_map.normalize(ship.position.directional_offset(d))
        # logging.info(f'testing {d}')
        if collide == po or po not in positions_used:  # and ((not game.game_map[po].is_occupied) or game.game_map[po].ship.owner!=game.my_id or po == ship.position):
            logging.info(f'ship {ship.id} on {source} next move on {po}')
            positions_used.append(po)
            command_queue.append(ship.move(d))
            logging.info(command_queue)
            return True
        return False

    all_possible = {(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)}
    moves = game.game_map.get_unsafe_moves(source, target)
    if target == source:
        # stay where we are
        if doit((0, 0)):
            return(0, 0)

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
        #d = random.sample(all_possible, 1)[0]
        d = all_possible.pop()
        if doit(d):
            return
        # all_possible.remove(d)

    # welp, we crash
    logging.info(f'{ship.id} crash')


game.ready("NicksBot")
logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))

num_players = len(game.players)
logging.info(f'{num_players} player mode.')

syp = game.players[game.my_id].shipyard.position
logging.info(syp)


def run():
    while True:
        game.update_frame()
        # You extract player metadata and the updated map metadata here for convenience.
        me = game.me
        game_map = game.game_map

        # highs = PriorityQueue()
        # spots = PriorityQueue()
        # for x, y in itertools.product(range(game_map.width), range(game_map.height)):
        #     highs.put(
        #         PP(
        #             (constants.MAX_HALITE - game_map[Position(x, y)].halite_amount * .25) +
        #                 (game_map.calculate_distance(Position(x,y),(0, 0) syp)) * 2,
        #             Position(x, y)))

        positions_used = []
        command_queue = []
        ship_queue = me.get_ships()

        # top10 = [highs.get().position for _ in range(10)]
        # logging.info(top10)

        # sort ships by proximity to shipyard
        ship_queue = sorted(ship_queue, key=lambda s: game_map.calculate_distance(s.position, syp),
                            reverse=True)

        for ship in ship_queue:
            ship.staying = False
            ship.returning = False
            if (constants.MAX_TURNS - game.turn_number) < 4 and ship.position == syp:
                # ignore ship completely so that it can die
                ship.staying = True
            # can it move?
            elif (game_map[ship.position].halite_amount * 0.1) > ship.halite_amount:
                # can't move, stay put
                logging.info(f'ship {ship.id} staying with {ship.halite_amount} avaliable')
                move(ship.position, ship.position, ship, positions_used, command_queue)
                ship.staying = True

            elif ((ship.halite_amount > 850) or
                  (game_map.calculate_distance(ship.position, syp) + 4 >=
                   (constants.MAX_TURNS - game.turn_number))):
                ship.returning = True

        for ship in ship_queue:
            if ship.staying:
                continue
            if (not ship.returning and
                    game_map[ship.position].halite_amount > constants.MAX_HALITE // 15):
                # collect while we are here
                move(ship.position, ship.position, ship, positions_used, command_queue)
                ship.staying = True

        for ship in ship_queue:
            if ship.returning:
                # move to drop-off
                logging.info('move to dropoff')
                if constants.MAX_TURNS - game.turn_number <= 4:
                    move(syp, ship.position, ship, positions_used, command_queue, collide=syp,
                         shortest=True)
                else:
                    move(syp, ship.position, ship, positions_used, command_queue, shortest=True)

        for ship in ship_queue:
            if ship.returning or ship.staying:
                continue

            ps = PriorityQueue()
            for x, y in itertools.product(range(game_map.width), range(game_map.height)):
                pass
                # todo: eventually, calculate the one with the "cheapest" path, not shortest.
                ps.put(PP(game_map.calculate_distance(ship.position, p), p))

            p = ps.get().position
            if (ship.halite_amount > 200 and (
                    game_map.calculate_distance(ship.position, syp) < game_map.calculate_distance(
                ship.position, p))):
                # move to drop-off
                move(syp, ship.position, ship, positions_used, command_queue, shortest=True)
            else:
                move(p, ship.position, ship, positions_used, command_queue)

        # If the game is in the first 200 turns and you have enough halite, spawn a ship.
        # Don't spawn a ship if you currently have a ship at port, though - the ships will collide.
        if game.turn_number <= (
                constants.MAX_TURNS // 2.8) and me.halite_amount > constants.SHIP_COST and not game_map[
            me.shipyard].is_occupied and syp not in positions_used:
            command_queue.append(me.shipyard.spawn())

            # Send your moves back to the game environment, ending this turn.
        game.end_turn(command_queue)


if __name__ == '__main__':
    run()

