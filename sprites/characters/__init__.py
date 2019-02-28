import math
from math import cos, sin

from sprites import X, Y


class Character:
    def __init__(self, vertex, color):
        self._vertex = vertex
        self._color = color
        self._polygon = []
        self._heading = 0

    def draw(self, surface):
        pass

    def move(self, new_x, new_y, heading=0):
        # Save location
        self._vertex[X] = new_x
        self._vertex[Y] = new_y
        self._heading = heading

    def _rotate_point(self, pt):
        theta = math.radians(self._heading)  # Convert angle to radians
        cosang, sinang = cos(theta), sin(theta)
        x, y = pt[X], pt[Y]
        tx, ty = x - self._vertex[X], y - self._vertex[Y]
        new_x = (tx * cosang + ty * sinang) + self._vertex[X]
        new_y = (-tx * sinang + ty * cosang) + self._vertex[Y]
        return [int(new_x), int(new_y)]

    def _rotate_polygon(self):
        """ Rotate polygon the given angle about its vertex. """
        theta = math.radians(self._heading)  # Convert angle to radians
        cosang, sinang = cos(theta), sin(theta)

        new_points = []
        for p in self._polygon:
            x, y = p[X], p[Y]
            tx, ty = x - self._vertex[X], y - self._vertex[Y]
            new_x = (tx * cosang + ty * sinang) + self._vertex[X]
            new_y = (-tx * sinang + ty * cosang) + self._vertex[Y]
            new_points.append([new_x, new_y])

        # Save off new poly
        self._polygon = new_points
