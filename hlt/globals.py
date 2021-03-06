import math

import logging


game = None
dropoffs = []
endgame = False

claimed_moves = {}

from hlt.positionals import Direction


def closest_dropoff(position, enemy=False):
    min_so_far = 5000
    closest_so_far = None
    dos = dropoffs
    if enemy:
        dos = []
        for player_id in game.players:
            dos.append(game.players[player_id].shipyard.position)
            for drop in game.players[player_id].get_dropoffs():
                dos.append(drop.position)

    for do in dos:
        distance = game.game_map.calculate_distance(position, do)
        if distance < min_so_far:
            min_so_far = distance
            closest_so_far = do
    return closest_so_far


def move(target, source, ship, positions_used, enemy_locations,
         command_queue, collide=False, shortest=False, la=13):

    for i in range(1, 15):
        if game.turn_number + i not in claimed_moves:
            claimed_moves[game.turn_number + i] = {}

    collide = collide or endgame
    num, amount, direcs = calculate_real_distance(
        target, source, positions_used, enemy_locations,
        ship.halite_amount, ship, collide=collide, la=la)

    # logging.info(direcs)
    direc, *rest = direcs
    po = game.game_map.normalize(ship.position.directional_offset(direc))
    # logging.info(f'Moving {ship.id} at {ship.position} to {po}')
    positions_used.add(po)
    prev_po = po
    # logging.info(len(direcs))
    for i, d in enumerate(direcs[:1]):
        new_po = game.game_map.normalize(prev_po.directional_offset(direcs[0]))
        claimed_moves[game.turn_number + i + 1][new_po] = ship.id
        prev_po = new_po
    command_queue.append(ship.move(direc))


def calculate_real_distance(target, source, positions,
                            enemy_locations, amount, ship,
                            collide=False, turn=0, la=13):
    # if turn == 1:
    source = game.game_map.normalize(source)
    if turn == la:
        return 1, amount, [(0, 0)]

    if turn == 1:
        # logging.info(f'zz: {target}, {source}, {positions}, {amount}, {turn}')
        if collide and source in dropoffs:
            pass
        elif source in positions:
            return 100, -5, [(0, 0)]
        elif source in enemy_locations and amount > 100:
            enemy_ship = enemy_locations[source]
            if enemy_ship.halite_amount > 600:
                # ignore this ship
                pass
            else:
                return 30, -1, [(0, 0)]
        elif amount > 600:
            for d in Direction.get_all_cardinals():
                if game.game_map.normalize(source.directional_offset(d)) in enemy_locations:
                    return 30, -1, [(0, 0)]

    if turn in (2, 3, 4):
        ship_id = claimed_moves[game.turn_number + 1].get(source)
        if ship_id and ship_id != ship.id:
            return 50, -2, [(0,0)]

    if target == source and turn != 0:
        if turn == 0:
            logging.info('hit')
        return 1, amount, [(0, 0)]

    stay_moves = 0
    cost_of_move = game.game_map[source].halite_amount * 0.1
    if amount - int(cost_of_move) < 0:
        # must stay
        stay_moves += 1
        collected = math.ceil(game.game_map[source].halite_amount * 0.25)
        spot_new = game.game_map[source].halite_amount - collected
        amount = min(amount + collected, 1000) - int(spot_new * 0.1)
        stayed = True

    else:
        amount = amount - int(cost_of_move)
        stayed = False

    def calc_move(d, cur_best):
        new_pos = source.directional_offset(d)
        num_moves, new_amount, direcs = calculate_real_distance(
            target, new_pos, positions, enemy_locations, amount, ship, collide=collide, turn=turn+1, la=la)

        if turn == 0 and ship.id == 14:
            logging.info(f'{num_moves} : {new_amount} : {direcs}')
        if d == (0,0):
            collected = math.ceil(game.game_map[new_pos].halite_amount * 0.25)
            new_amount = min(new_amount + collected, 1000)
        # logging.info(f'target {target} to source {source}: {}')
        # if num_moves >= 80:
        #     return cur_best

        # if (num_moves < cur_best[0] or
        #         (num_moves == cur_best[0] and amount > cur_best[1])):
        if (new_amount > cur_best[1]) or (new_amount == cur_best[1] and num_moves < cur_best[0]):
            return num_moves, new_amount, [d] + direcs

        return cur_best

    # stay, up, right, left, down - bottom left
    # all_possible = {(0, 0),  (0, 1), (1, 0), (-1, 0), (0, -1)}
    # stay, left, right, down, up - upper right
    # all_possible = {(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)}
    # stay, right, left, up, down - bottom left
    # all_possible = {(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)}
    # stay, down, right, left, up - upper right
    # all_possible = {(0, 0), (0, -1), (1, 0), (-1, 0), (0, 1)}
    # stay, up, left, right, down - bottom left
    # all_possible = {(0, 0), (0, 1), (-1, 0), (0, 1), (0, -1)}
    # stay, up, left, down, right - bottom left
    all_possible = {(0, 1), (-1, 0), (0, -1), (1, 0), (0, 0), }
    # stay, down, left, up, right - bottom right
    # all_possible = {(0, 0), (0, -1), (-1, 0), (0, 1), (1, 0)}
    # all_possible = {(0,0), (0, -1), (1, 0), (-1, 0), (0, 1)}
    # if game.turn_number < 20:
    #     for dop in all_possible:
    #         logging.info(dop)
    ideal = set()
    medio = set()
    fallback = set()

    moves = game.game_map.get_unsafe_moves(source, target)
    if target == source:
        assert len(moves) == 0
        ideal.add((0, 0))
        all_possible.discard((0, 0))
        fallback = all_possible
    elif len(moves) == 1:
        # try move first
        direction = moves[0]
        ideal.add(direction)
        all_possible.discard(direction)


        reverse = (direction[0] * -1, direction[1] * -1)
        fallback.add(reverse)
        all_possible.discard(reverse)

        medio = all_possible

    elif len(moves) in (2, 3):
        for m in moves:
            ideal.add(m)
            all_possible.discard(m)

        medio.add((0, 0))
        all_possible.discard((0, 0))

        fallback = all_possible

    else:
        logging.info("How did this happen?")

    cur_best = 100, -10, source
    for d in ideal:
        cur_best = calc_move(d, cur_best)

    if cur_best[0] > 25:
        logging.info('medio')
        for d in medio:
            cur_best = calc_move(d, cur_best)

    if cur_best[0] > 25:
        logging.info('fallback')
        for d in fallback:
            cur_best = calc_move(d, cur_best)

    if cur_best[0] >= 100:
        return 100, -10, [(0,0)]

    # now calc out own move
    num_moves, new_amount, direcs = cur_best
    if stayed:
        direcs = [(0,0)] + direcs

    num_moves += 1 + stay_moves

    if turn == 0:
        logging.info(f'{ship.id}, {num_moves}, {new_amount}, {direcs}')
    return num_moves, new_amount, direcs
