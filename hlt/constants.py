"""
The constants representing the game variation being played.
They come from game engine and changing them has no effect.
They are strictly informational.
"""

import argparse


SHIP_COST = DROPOFF_COST = MAX_HALITE = MAX_TURNS = None
EXTRACT_RATIO = MOVE_COST_RATIO = None
INSPIRATION_ENABLED = INSPIRATION_RADIUS = INSPIRATION_SHIP_COUNT = None
INSPIRED_EXTRACT_RATIO = INSPIRED_BONUS_MULTIPLIER = INSPIRED_MOVE_COST_RATIO = None
RETURN_AMOUNT = LOOK_AMOUNT = SO_LOOK_AMOUNT = None
SHIP_DO_RATIO = DO_DISTANCE = DO_TURN_FACTOR = None
DO_HALITE_FACTOR = DISTANCE_FACTOR = STAY_FACTOR = None
ENEMY_FACTOR = BUILD_FACTOR = BUILD_HALITE_LIMIT = None
NAME = None

const_dict = {
    2: {
        32: {
            'return_amount': 950,
            'look_amount': 225,
            'so_look_amount': 40,
            'ship_do_ratio': 10,
            'do_distance': 14,
            'do_turn_factor': 0.4,
            'do_halite_factor': 0.5,
            'distance_factor': 1.6,
            'stay_factor': 3.5,
            'enemy_factor': 1.0,
            'build_factor': 1633,
            'build_halite_limit': 0.5
        },
        40: {
            'return_amount': 950,
            'look_amount': 300,
            'so_look_amount': 100,
            'ship_do_ratio': 10,
            'do_distance': 16,
            'do_turn_factor': 0.7,
            'do_halite_factor': 0.6,
            'distance_factor': 1.5,
            'stay_factor': 3.7,
            'enemy_factor': 1.0,
            'build_factor': 2000,
            'build_halite_limit': 0.3
        },
        48: {
            'return_amount': 950,
            'look_amount': 300,
            'so_look_amount': 100,
            'ship_do_ratio': 10,
            'do_distance': 16,
            'do_turn_factor': 0.7,
            'do_halite_factor': 0.6,
            'distance_factor': 1.5,
            'stay_factor': 3.7,
            'enemy_factor': 1.0,
            'build_factor': 2000,
            'build_halite_limit': 0.3
        },
        56: {
            'return_amount': 950,
            'look_amount': 300,
            'so_look_amount': 100,
            'ship_do_ratio': 10,
            'do_distance': 16,
            'do_turn_factor': 0.7,
            'do_halite_factor': 0.6,
            'distance_factor': 1.5,
            'stay_factor': 3.7,
            'enemy_factor': 1.0,
            'build_factor': 2000,
            'build_halite_limit': 0.3
        },
        64: {
            'return_amount': 950,
            'look_amount': 300,
            'so_look_amount': 100,
            'ship_do_ratio': 10,
            'do_distance': 16,
            'do_turn_factor': 0.7,
            'do_halite_factor': 0.6,
            'distance_factor': 1.5,
            'stay_factor': 3.7,
            'enemy_factor': 1.0,
            'build_factor': 2000,
            'build_halite_limit': 0.3
        },
    },
    4: {
        32: {
            'return_amount': 870,
            'look_amount': 200,
            'so_look_amount': 50,
            'ship_do_ratio': 26,
            'do_distance': 15,
            'do_turn_factor': 0.4,
            'do_halite_factor': 0.5,
            'distance_factor': 1.0,
            'stay_factor': 4.0,
            'enemy_factor': 1.0,
            'build_factor': 1612,
            'build_halite_limit': 0.4

        },
        40: {
            'return_amount': 930,
            'look_amount': 300,
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
            'return_amount': 930,
            'look_amount': 300,
            'so_look_amount': 170,
            'ship_do_ratio': 18,
            'do_distance': 13,
            'do_turn_factor': 0.9,
            'do_halite_factor': 0.7,
            'distance_factor': 3.1,
            'stay_factor': 2.1,
            'enemy_factor': 1.0,
            'build_factor': 2600,
            'build_halite_limit': 0.2
        },
        56: {
            'return_amount': 930,
            'look_amount': 300,
            'so_look_amount': 170,
            'ship_do_ratio': 18,
            'do_distance': 13,
            'do_turn_factor': 0.9,
            'do_halite_factor': 0.7,
            'distance_factor': 3.1,
            'stay_factor': 2.1,
            'enemy_factor': 1.0,
            'build_factor': 2400,
            'build_halite_limit': 0.2
        },
        64: {
            'return_amount': 930,
            'look_amount': 300,
            'so_look_amount': 150,
            'ship_do_ratio': 10,
            'do_distance': 16,
            'do_turn_factor': 0.7,
            'do_halite_factor': 0.6,
            'distance_factor': 1.4,
            'stay_factor': 3.6,
            'enemy_factor': 1.0,
            'build_factor': 2000,
            'build_halite_limit': 0.3
        },
    }
}


def load_constants(constants):
    """
    Load constants from JSON given by the game engine.
    """
    global SHIP_COST, DROPOFF_COST, MAX_HALITE, MAX_TURNS
    global EXTRACT_RATIO, MOVE_COST_RATIO
    global INSPIRATION_ENABLED, INSPIRATION_RADIUS, INSPIRATION_SHIP_COUNT
    global INSPIRED_EXTRACT_RATIO, INSPIRED_BONUS_MULTIPLIER, INSPIRED_MOVE_COST_RATIO

    """The cost to build a single ship."""
    SHIP_COST = constants['NEW_ENTITY_ENERGY_COST']

    """The cost to build a dropoff."""
    DROPOFF_COST = constants['DROPOFF_COST']

    """The maximum amount of halite a ship can carry."""
    MAX_HALITE = constants['MAX_ENERGY']

    """
    The maximum number of turns a game can last. This reflects the fact
    that smaller maps play for fewer turns.
    """
    MAX_TURNS = constants['MAX_TURNS']

    """1/EXTRACT_RATIO halite (truncated) is collected from a square per turn."""
    EXTRACT_RATIO = constants['EXTRACT_RATIO']

    """1/MOVE_COST_RATIO halite (truncated) is needed to move off a cell."""
    MOVE_COST_RATIO = constants['MOVE_COST_RATIO']

    """Whether inspiration is enabled."""
    INSPIRATION_ENABLED = constants['INSPIRATION_ENABLED']

    """
    A ship is inspired if at least INSPIRATION_SHIP_COUNT opponent
    ships are within this Manhattan distance.
    """
    INSPIRATION_RADIUS = constants['INSPIRATION_RADIUS']

    """
    A ship is inspired if at least this many opponent ships are within
    INSPIRATION_RADIUS distance.
    """
    INSPIRATION_SHIP_COUNT = constants['INSPIRATION_SHIP_COUNT']

    """An inspired ship mines 1/X halite from a cell per turn instead."""
    INSPIRED_EXTRACT_RATIO = constants['INSPIRED_EXTRACT_RATIO']

    """An inspired ship that removes Y halite from a cell collects X*Y additional halite."""
    INSPIRED_BONUS_MULTIPLIER = constants['INSPIRED_BONUS_MULTIPLIER']

    """An inspired ship instead spends 1/X% halite to move."""
    INSPIRED_MOVE_COST_RATIO = constants['INSPIRED_MOVE_COST_RATIO']


def parse_constants(player_num, size):
    global RETURN_AMOUNT, LOOK_AMOUNT, SO_LOOK_AMOUNT
    global SHIP_DO_RATIO, DO_DISTANCE, DO_TURN_FACTOR
    global DO_HALITE_FACTOR, DISTANCE_FACTOR, STAY_FACTOR
    global ENEMY_FACTOR, BUILD_FACTOR, BUILD_HALITE_LIMIT
    global NAME

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

    def get_constant(name, a, b):
        result = getattr(args, name) or const_dict[player_num][size].get(name)
        return result

    RETURN_AMOUNT = get_constant('return_amount', 500, 1000)
    # RETURN_AMOUNT = 950
    LOOK_AMOUNT = get_constant('look_amount', 10, 1000)
    # LOOK_AMOUNT = 300
    SO_LOOK_AMOUNT = get_constant('so_look_amount', 2, 1000)
    # SO_LOOK_AMOUNT = 100
    SHIP_DO_RATIO = get_constant('ship_do_ratio', 5, 30)
    # SHIP_DO_RATIO = 10
    DO_DISTANCE = get_constant('do_distance', 1, 50)
    # DO_DISTANCE = 16
    DO_TURN_FACTOR = get_constant('do_turn_factor', 0.1, 1.0)
    # DO_TURN_FACTOR = 0.7
    DO_HALITE_FACTOR = get_constant('do_halite_factor', 0.1, 0.9)
    # DO_HALITE_FACTOR = 0.6
    DISTANCE_FACTOR = get_constant('distance_factor', 0.1, 5.0)
    # DISTANCE_FACTOR = 1.5
    STAY_FACTOR = get_constant('stay_factor', 0.1, 5.0)
    # STAY_FACTOR = 3.7
    ENEMY_FACTOR = get_constant('enemy_factor', 0.0, 3.0)
    # ENEMY_FACTOR = 1
    BUILD_FACTOR = get_constant('build_factor', 800, 4000)
    # BUILD_FACTOR = 2000
    BUILD_HALITE_LIMIT = get_constant('build_halite_limit', 0.1, 0.9)
    # BUILD_HALITE_LIMIT = 0.3

    if args.name:
        NAME = args.name
    else:
        NAME = f'{RETURN_AMOUNT}:{SHIP_DO_RATIO}:{DO_DISTANCE}:{BUILD_FACTOR}'
