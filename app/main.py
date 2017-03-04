import bottle
import os
import random


@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')


@bottle.post('/start')
def start():
    data = bottle.request.json
    game_id = data['game_id']
    board_width = data['width']
    board_height = data['height']

    head_url = 'https://img0.etsystatic.com/103/0/11964913/il_340x270.892126004_kfiw.jpg'

    # TODO: Do things with data

    return {
        'color': '#00FF00',
        'taunt': 'I am Groot!',
        'head_url': head_url,
        'name': 'Groot'
    }


@bottle.post('/move')
def move():
    data = bottle.request.json

    # TODO: Do things with data
    directions = ['up', 'down', 'left', 'right']


    move = get_move(data)

    return {
        'move': move,
        'taunt': 'I am Groot!'
    }


def get_move(data):
    groot = get_groot(data)
    return default(data)
    # if groot["health"] < 25:
    #     return hungry(data)
    # else:
    #     return default(data)

def get_groot(data):
    for snake in data["snakes"]:
        if snake["id"] == data["you"]:
            return snake


def default(data):
    groot = get_groot(data)

    map = make_map(data)

    return "down"




# def evaluate(coord, map):
#     value = 0

#     if coord[1] == 0:
#         north = 100
#     else:
#         north = map[coord[1]-1][coord[0]]

#     if coord[1] == (len(map)-1):
#         south = 100
#     else:
#         south = heatMap[coord[1]+1][coord[0]]

#     if coord[0] == (len(heatMap[0])-1):
#         east = 100
#     else:
#         east = heatMap[coord[1]][coord[0]+1]

#     if coord[0] == 0:
#         west = 100
#     else:
#         west = heatMap[coord[1]][coord[0]-1]

#     values = [north, south, east, west]

#     minimum = min(values)

#     if north == minimum:
#         return [coord[0],coord[1]-1]

#     if south == minimum:
#         return [coord[0],coord[1]+1]

#     if east == minimum:
#         return [coord[0]+1,coord[1]]

#     if west == minimum:
#         return [coord[0]-1,coord[1]]

# def hungry(data):

#     groot = get_groot(data)
#     map = make_map(data)

#     if not len(data["food"]):
#         return default(data)

#     food = food_eval(map, data["food"], shia["coords"][0])

#     if not len(food):
#         return default(data)

#     return get_move(shia["coords"][0], food, data)



def make_map(data):
    wall_coords = []
    map = []

    for y in range(data["height"]):
        row = []
        for j in range(data["width"]):
            row.append(0)
        map.append(row)


    for snake in data["snakes"]:
        if snake["id"] == data["you"]:
            for body in snake["coords"][1:]:
                wall_coords.append(body)
        else:
            for body in snake["coords"]:
                wall_coords.append(body)
    print(map)

    return heatMap





# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()
if __name__ == '__main__':
    bottle.run(application, host=os.getenv('IP', '0.0.0.0'), port=os.getenv('PORT', '8080'))