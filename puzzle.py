# puzzle.py
# classes for the tiles, transformations and the puzzle board

import random
import cv2
import numpy as np


# a single piece of the picture
class Tile:
    def __init__(self, image, home):
        self.image = image
        self.home = home      # where the tile should be
        self.rotation = 0     # how many 90 degree turns
        self.flipped = False

    def rotate(self, turns=1):
        self.rotation = (self.rotation + turns) % 4

    def flip(self):
        self.rotation = (-self.rotation) % 4
        self.flipped = not self.flipped

    def is_upright(self):
        return self.rotation == 0 and self.flipped == False

    def get_image(self):
        img = self.image
        if self.flipped:
            img = cv2.flip(img, 1)
        for i in range(self.rotation):
            img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        return img


# parent class for the scramble moves
class Transformation:
    def __init__(self, pos):
        self.pos = pos

    def apply(self, board):
        pass


class Swap(Transformation):
    def __init__(self, pos, other):
        super().__init__(pos)
        self.other = other

    def apply(self, board):
        board.swap(self.pos, self.other)


class Rotate(Transformation):
    def apply(self, board):
        board.tiles[self.pos].rotate(random.choice([1, 2, 3]))


class Flip(Transformation):
    def apply(self, board):
        tile = board.tiles[self.pos]
        if random.choice([True, False]):
            tile.flip()          # horizontal
        else:
            tile.flip()          # vertical = horizontal flip + 180
            tile.rotate(2)


class Board:
    def __init__(self, image, grid):
        self.original = image
        self.grid = grid
        self.size = image.shape[0] // grid
        self.tiles = []
        self.moves = 0
        self.hints = 3
        self.hint = None
        self.selected = None
        self.done = False

        for r in range(grid):
            for c in range(grid):
                piece = image[r*self.size:(r+1)*self.size, c*self.size:(c+1)*self.size]
                self.tiles.append(Tile(piece, r*grid + c))

    def scramble(self):
        counts = {3: 6, 4: 12, 5: 20}
        n = counts[self.grid]
        spots = random.sample(range(self.grid*self.grid), self.grid*self.grid)
        moves = [Swap(spots.pop(), spots.pop()), Rotate(spots.pop()), Flip(spots.pop())]
        while len(moves) < n:
            if len(spots) > n - len(moves) and random.randint(1, 3) == 1:
                moves.append(Swap(spots.pop(), spots.pop()))
            elif random.randint(1, 2) == 1:
                moves.append(Rotate(spots.pop()))
            else:
                moves.append(Flip(spots.pop()))
        for m in moves:
            m.apply(self)

    def swap(self, a, b):
        self.tiles[a], self.tiles[b] = self.tiles[b], self.tiles[a]

    def correct(self, pos):
        return self.tiles[pos].home == pos and self.tiles[pos].is_upright()

    def wrong_tiles(self):
        return [i for i in range(len(self.tiles)) if not self.correct(i)]

    def after_move(self):
        self.moves += 1
        self.hint = None
        if len(self.wrong_tiles()) == 0:
            self.done = True

    def solve(self):
        self.tiles.sort(key=lambda t: t.home)
        for t in self.tiles:
            t.rotation = 0
            t.flipped = False
        self.moves = 0
        self.hint = None
        self.selected = None
        self.done = True

    def get_image(self):
        rows = []
        for r in range(self.grid):
            rows.append(np.hstack([t.get_image() for t in self.tiles[r*self.grid:(r+1)*self.grid]]))
        return np.vstack(rows)
