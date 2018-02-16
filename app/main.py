import bottle
import os
import random
import heapq
import copy

@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')


@bottle.post('/start')
def start():
    data = bottle.request.json
    game_id = data['game_id']

    head_url = 'https://img0.etsystatic.com/103/0/11964913/il_340x270.892126004_kfiw.jpg'

    return {
        'color': '#002800',
        'taunt': 'I am Groot!',
        'head_url': head_url,
        'name': 'Groot',
        'head_type' : 'shades',
        'tail_type' : 'round-bum'
    }


@bottle.post('/move')
def move():
    data = bottle.request.json

    move = get_move(data)

    # #Emergency move if move is None
    # if (move is None):
    #     print("MOVE IS NONE!!!!!!!!!")
    #     map = make_map(data, True)
    #     groot = get_groot(data)
    #     head = groot["body"]["data"][0]

    #     x = head["x"]
    #     y = head["y"]

    #     #Try and find safe move
    #     if y != 0 and map[y-1][x] == 0:
    #         if y != 1 and map[y-2][x] == 0:
    #             move = 'up'

    #     if y != (data["height"]-1) and map[y+1][x] == 0:
    #         if y != (data["height"]-2) and map[y+2][x] == 0:
    #             move = 'down'

    #     if x != 0 and map[y][x-1] == 0:
    #         if x != 1 and map[y][x-2] == 0:
    #             move = 'left'

    #     if x != (data["width"]-1) and map[y][x+1] == 0:
    #         if x != (data["width"]-2) and map[y][x+2] == 0:
    #             move = 'right'

    #     #Just find a move
    #     if (move == None):
    #         if y != 0 and map[y-1][x] == 0:
    #             move = 'up'

    #         if y != (data["height"]-1) and map[y+1][x] == 0:
    #             move = 'down'

    #         if x != 0 and map[y][x-1] == 0:
    #             move = 'left'

    #         if x != (data["width"]-1) and map[y][x+1] == 0:
    #             move = 'right'

    taunt = 'I am Gro'
    for x in range(data['turn'] % 8):
        taunt += 'o'
    taunt += 'ot!'
    return {
        'move': move
    }


def get_move(data):
    groot = get_groot(data)
    moves = get_possible_moves_from_flood(data)

    #Here would be a good place to use conditionals for our move behaviour

    if groot["health"] < 60:
        return hungry(data, moves)
    else:
        return default(data, moves)


def get_groot(data):
    return data["you"]


def get_possible_moves_from_flood(data):
    map = make_flood_map(data)
    possible_moves = []
    groot = get_groot(data)
    head = groot["body"]["data"][0]

    x = head["x"]
    y = head["y"]

    if y != 0 and map[y - 1][x] == 0:
        possible_moves.append({"direction": "up", "count": 0})

    if y != (data["height"] - 1) and map[y + 1][x] == 0:
        possible_moves.append({"direction": "down", "count": 0})

    if x != 0 and map[y][x - 1] == 0:
        possible_moves.append({"direction": "left", "count": 0})

    if x != (data["width"] - 1) and map[y][x + 1] == 0:
        possible_moves.append({"direction": "right", "count": 0})

    # Run flood fill on all possible moves
    for move in possible_moves:
        move_coords = get_move_coordinates(head, move["direction"])
        temp_map = copy.deepcopy(map)
        filled = []
        flood_fill(temp_map, move_coords["x"], move_coords["y"], filled)
        move["count"] = len(filled)

    grootLength = len(groot["body"]["data"])
    final_moves = []
    for move in possible_moves:
        dangerousLength = grootLength * 1.5
        if (move["count"] > dangerousLength):
            final_moves.append(move["direction"])

    # If all moves are smaller than our body, return the biggest one
    if len(final_moves) is 0 and len(possible_moves) > 0:
        sorted_possible_moves = sorted(possible_moves, key=lambda move: move["count"], reverse=True)
        final_moves.append(sorted_possible_moves[0]["direction"])

    return final_moves


def flood_fill(map, x, y, filled):
    if map[y][x] == 0:
        # Mark as visited
        map[y][x] = 1
        filled.append({'x': x, 'y': y})

        # Check surrounding spots:
        if x > 0:
            flood_fill(map, x - 1, y, filled)
        if x < len(map[y]) - 1:
            flood_fill(map, x + 1, y, filled)
        if y > 0:
            flood_fill(map, x, y - 1, filled)
        if y < len(map) - 1:
            flood_fill(map, x, y + 1, filled)


def get_move_coordinates(head, move):
    x = head["x"]
    y = head["y"]

    if move == 'left':
        return {'x': x - 1, 'y': y}
    if move == 'right':
        return {'x': x + 1, 'y': y}
    if move == 'up':
        return {'x': x, 'y': y - 1}
    if move == 'down':
        return {'x': x, 'y': y + 1}

    print("Invalid move passed in to get_move_coordinates")


def make_flood_map(data):
    wall_coords = []
    map = []

    for y in range(data["height"]):
        row = []
        for j in range(data["width"]):
            row.append(0)
        map.append(row)


    for snake in data["snakes"]["data"]:
        # Cut off end of tail, since this will move on the next turn
        for body in snake["body"]["data"][:-1]:
            wall_coords.append(body)

    for wall in wall_coords:
        map[wall["y"]][wall["x"]] = 1

    return map


def default(data, flood_fill_moves):
    map = make_map(data, False)
    groot = get_groot(data)
    head = groot["body"]["data"][0]

    x = head["x"]
    y = head["y"]

    #dangersLeft = 0
    #dangersRight = 0
    #dangersUp = 0
    #dangersDown = 0

    dangersLeft = False
    dangersRight = False
    dangersUp = False
    dangersDown = False

    if (len(groot["body"]["data"]) > 1):
        firstBody = groot["body"]["data"][1]
        xfirstBody = firstBody["x"]
        yfirstBody = firstBody["y"]
        
        
        if (y - 1 == yfirstBody) or (y == 0) :
            #Do not move up
            #dangersUp = 100
            dangersUp = True

        if (y + 1 == yfirstBody) or (y == data["height"] - 1):
            #Do not move down
            #dangersDown = 100
            dangersDown = True

        if (x - 1 == xfirstBody) or (x == 0):
            #Do not move left
            #dangersLeft = 100
            dangersLeft = True

        if (x + 1 == xfirstBody) or (x == data["width"] - 1):
            #Do not move right
            #dangersRight = 100
            dangersRight = True

    xtemp = x
    ytemp = y

    #upList = [dangersUp, 'up']
    #downList = [dangersDown, 'down']
    #leftList = [dangersLeft, 'left']
    #rightList = [dangersRight, 'right']

    #values = [upList, downList, leftList, rightList]

    #sorted_by_first = sorted(values, key=lambda value: value[0])

    #for option in sorted_by_first:
    if dangersUp == False:
            #if y == 0:
                #continue

            # ytemp = y - 1
            # if (map[ytemp][x] >= 2):
            #     continue
        return 'up'

    if dangersDown == False:
            #if y == data["height"] - 1:
                #continue

            # ytemp = y + 1
            # if (map[ytemp][x] >= 2):
            #     continue
        return 'down'

    if dangersLeft == False:
            #if x == 0:
                #continue

            # xtemp = x - 1
            # if (map[y][xtemp] >= 2):
            #     continue
        return 'left'

    if dangersRight == False:
            #if x == data["width"] - 1:
                #continue

            # xtemp = x + 1
            # if (map[y][xtemp] >= 2):
            #     continue
        return 'right'


    #print("IF WE GET HERE, THIS IS BADDDD")
    #return None


def hungry(data, flood_fill_moves):
    groot = get_groot(data)
    map = make_map(data, True)
    if not len(data["food"]["data"]):
        return default(data, flood_fill_moves)

    food = food_eval(map, data["food"]["data"], groot["body"]["data"][0])
    if not len(food):
        return default(data, flood_fill_moves)

    move = get_astar_move(groot["body"]["data"][0], food[1], data)

    if move in flood_fill_moves:
        return move
    else:
        return default(data, flood_fill_moves)

def food_eval(map, data_food, our_head):
        food_distance = []
        for food in data_food:
            food_distance.append(get_distance(our_head, food))
        sorted(food_distance)
        return food_distance[0]


def get_distance(our_head, food_coords):
    x_distance = abs(our_head["x"] - food_coords["x"])
    y_distance = abs(our_head["y"] - food_coords["y"])
    return [ x_distance + y_distance , food_coords]


def make_map(data, excludeFood):
    wall_coords = []
    map = []

    for y in range(data["height"]):
        row = []
        for j in range(data["width"]):
            row.append(0)
        map.append(row)


    for snake in data["snakes"]["data"]:
        head_counter = 0
        if snake["id"] == data["you"]["id"]:
            for body in snake["body"]["data"][1:]:
                wall_coords.append(body)
        else:
            for body in snake["body"]["data"]:
                if (head_counter == 0):
                    wall_coords.append(body)
                    wall_coords.append(body)
                    wall_coords.append(body)
                wall_coords.append(body)


    for wall in wall_coords:
        x = wall["x"]
        y = wall["y"]

        map[y][x] = 1
    
    if (not excludeFood):
        for food in data["food"]["data"]:
            wall_coords.append(food)

    for wall in wall_coords:
        x = wall["x"]
        y = wall["y"]

        map[y][x] += 1

    # Make edge scary
    for y in range(data["height"]):
        for x in range(data["width"]):
            if x == 0 or x == (data["width"]-1):
                map[y][x] += 0.5
            if y == 0 or y == (data["height"]-1):
                map[y][x] += 0.5

    return map


def get_astar_move(start, goal, data):
    start = (start["x"], start["y"])
    goal = (goal["x"], goal["y"])
    wall_coords     = []
    start           = tuple(start)
    goal            = tuple(goal)

    for snake in data["snakes"]["data"]:
        if snake["id"] == data["you"]["id"]:
            for body in snake["body"]["data"][1:]:
                wall_coords.append((body["x"], body["y"]))
        else:
            for body in snake["body"]["data"]:
                wall_coords.append((body["x"], body["y"]))

    a = AStar()

    a.init_grid(data["height"],data["width"],wall_coords,start,goal)

    solution = a.solve()

    if solution:
        return convert_direction(start, solution[1])

    return None


def convert_direction(start, coord):

    if start[0] > coord[0]:
        return "left"
    elif start[0] < coord[0]:
        return "right"

    if start[1] > coord[1]:
        return "up"

    return "down"


'''
Thanks to Laurent Luce for supplying A*
https://github.com/laurentluce/python-algorithms/
'''

class Cell(object):
    def __init__(self, x, y, reachable):
        """Initialize new cell.
        @param reachable is cell reachable? not a wall?
        @param x cell x coordinate
        @param y cell y coordinate
        @param g cost to move from the starting cell to this cell.
        @param h estimation of the cost to move from this cell
                 to the ending cell.
        @param f f = g + h
        """
        self.reachable = reachable
        self.x = x
        self.y = y
        self.parent = None
        self.g = 0
        self.h = 0
        self.f = 0


class AStar(object):
    def __init__(self):
        # open list
        self.opened = []
        heapq.heapify(self.opened)
        # visited cells list
        self.closed = set()
        # grid cells
        self.cells = []
        self.grid_height = None
        self.grid_width = None

    def init_grid(self, width, height, walls, start, end):
        """Prepare grid cells, walls.
        @param width grid's width.
        @param height grid's height.
        @param walls list of wall x,y tuples.
        @param start grid starting point x,y tuple.
        @param end grid ending point x,y tuple.
        """
        self.grid_height = height
        self.grid_width = width
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                if (x, y) in walls:
                    reachable = False
                else:
                    reachable = True
                self.cells.append(Cell(x, y, reachable))
        self.start = self.get_cell(*start)
        self.end = self.get_cell(*end)

    def get_heuristic(self, cell):
        """Compute the heuristic value H for a cell.
        Distance between this cell and the ending cell multiply by 10.
        @returns heuristic value H
        """
        return 10 * (abs(cell.x - self.end.x) + abs(cell.y - self.end.y))

    def get_cell(self, x, y):
        """Returns a cell from the cells list.
        @param x cell x coordinate
        @param y cell y coordinate
        @returns cell
        """
        return self.cells[x * self.grid_height + y]

    def get_adjacent_cells(self, cell):
        """Returns adjacent cells to a cell.
        Clockwise starting from the one on the right.
        @param cell get adjacent cells for this cell
        @returns adjacent cells list.
        """
        cells = []
        if cell.x < self.grid_width-1:
            cells.append(self.get_cell(cell.x+1, cell.y))
        if cell.y > 0:
            cells.append(self.get_cell(cell.x, cell.y-1))
        if cell.x > 0:
            cells.append(self.get_cell(cell.x-1, cell.y))
        if cell.y < self.grid_height-1:
            cells.append(self.get_cell(cell.x, cell.y+1))
        return cells

    def get_path(self):
        cell = self.end
        path = [(cell.x, cell.y)]
        while cell.parent is not self.start:
            cell = cell.parent
            path.append((cell.x, cell.y))

        path.append((self.start.x, self.start.y))
        path.reverse()
        return path

    def update_cell(self, adj, cell):
        """Update adjacent cell.
        @param adj adjacent cell to current cell
        @param cell current cell being processed
        """
        adj.g = cell.g + 10
        adj.h = self.get_heuristic(adj)
        adj.parent = cell
        adj.f = adj.h + adj.g

    def solve(self):
        """Solve maze, find path to ending cell.
        @returns path or None if not found.
        """
        # add starting cell to open heap queue
        heapq.heappush(self.opened, (self.start.f, self.start))
        while len(self.opened):
            # pop cell from heap queue
            f, cell = heapq.heappop(self.opened)
            # add cell to closed list so we don't process it twice
            self.closed.add(cell)
            # if ending cell, return found path
            if cell is self.end:
                return self.get_path()
            # get adjacent cells for cell
            adj_cells = self.get_adjacent_cells(cell)
            for adj_cell in adj_cells:
                if adj_cell.reachable and adj_cell not in self.closed:
                    if (adj_cell.f, adj_cell) in self.opened:
                        # if adj cell in open list, check if current path is
                        # better than the one previously found
                        # for this adj cell.
                        if adj_cell.g > cell.g + 10:
                            self.update_cell(adj_cell, cell)
                    else:
                        self.update_cell(adj_cell, cell)
                        # add adj cell to open list
                        heapq.heappush(self.opened, (adj_cell.f, adj_cell))


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()
if __name__ == '__main__':
    bottle.run(application, host=os.getenv('IP', '0.0.0.0'), port=os.getenv('PORT', '8000'))
