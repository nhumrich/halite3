game = None
dropoffs = []


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
