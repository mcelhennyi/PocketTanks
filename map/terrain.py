import bisect
import math
from math import atan2

import pygame

from sprites import X, Y
import random


MAX_TERRAIN = 200
MIN_TERRAIN = 0
LINE_WIDTH = 2


class OutOfMapException(Exception):
    pass


class Terrain:
    def __init__(self, dimension, color):

        # Game details
        self._dimension = dimension

        # Terrain Generation
        self._terrain = []
        self._color = color
        self._terrain_polygon = []

        # Generate terrain
        self.generate_terrain()

    def height_at_point(self, pt):
        return self._terrain[pt]

    def grade_at_point(self, pt, width=4):
        # TODO: Do smart things with small tall peaks, use some physics maybe??

        # dist either side
        dist = int(width/2.0)

        # Get the x value for point left and right of middle point
        less_x = pt - dist if pt - dist >= 0 else 0
        high_x = pt + dist if pt + dist < self._dimension[X] else self._dimension[X] - 1

        # Get the y value for point left and right of middle point
        h_less = self._terrain[less_x]
        h_high = self._terrain[high_x]

        # Calculate and return slope - What a bitch
        slope = - (360 + ((atan2((h_less - h_high), (less_x - high_x)) * 180.0 / math.pi) - 180))
        return slope

    def generate_terrain(self):
        # previous_height = random.randint(self._dimension[Y] - MAX_TERRAIN, self._dimension[Y] - 1)
        # for x in range(0, self._dimension[X]):
        #     self._terrain.append(self._random_height(previous_height))  # Generate and save current height
        #     previous_height = self._terrain[x]  # Save off for previous in next iteration

        points = self._midpoint_displacement(start=[0, self._dimension[Y] - MAX_TERRAIN],
                                             end=[self._dimension[X]+1, self._dimension[Y] - MAX_TERRAIN],
                                             roughness=0.9,
                                             vertical_displacement=self._dimension[Y] - MAX_TERRAIN,
                                             num_of_iterations=13)

        for point in points:
            self._terrain.append(point[1] if point[1] < self._dimension[Y] else self._dimension[Y] - 1)

        # Generate the polygon for this terrain list
        self._terrain_polygon.append([0, self._dimension[Y]])  # Bottom left corner of the screen
        for x, y in enumerate(self._terrain):
            self._terrain_polygon.append([x, y])  # points along the terrain
        self._terrain_polygon.append([self._dimension[X], self._dimension[Y]])  # Bottom Right
        self._terrain_polygon.append([0, self._dimension[Y]])  # Bottom left corner of the screen again to close polygon

    def intersects_terrain(self, location, buffer_x=0, buffer_y=0):
        # TODO Add a buffer to calculation to make it easier
        if location[X] > self._dimension[X]:
            # thing is out of the map
            # print(location)
            raise OutOfMapException("Projectile out of map to the right.")
        elif location[X] < 0:
            # thing is out side of the map
            # print(location)
            # print(self._dimension)
            raise OutOfMapException("Projectile out of map to the left.")

        # print(location)

        # We made it here, the thing is still in the map
        if self._terrain[location[X]] <= location[Y]:
            print("INTERSECT WITH GROUND: " + str(self._terrain[location[X]]) + " " + str(location[Y]))
            # Terrain is over or equal to height of projectile at this X location, we intersect
            return True
        else:
            # Otherwise we do not intersect
            return False

    def draw(self, surface):
        pygame.draw.polygon(
            surface,
            self._color,
            self._terrain_polygon,
            LINE_WIDTH
        )

    # def _random_height(self, previous_height):
    #     greater = random.randint(0, 100) > 50  # Generate a yes no
    #
    #     if greater:
    #         return random.randint(self._dimension[Y] - MAX_TERRAIN, previous_height)
    #     else:
    #         return random.randint(previous_height, self._dimension[Y] - 1)

    # Iterative midpoint vertical displacement
    def _midpoint_displacement(self, start, end, roughness, vertical_displacement=None,
                               num_of_iterations=16):
        """
        Given a straight line segment specified by a starting point and an endpoint
        in the form of [starting_point_x, starting_point_y] and [endpoint_x, endpoint_y],
        a roughness value > 0, an initial vertical displacement and a number of
        iterations > 0 applies the  midpoint algorithm to the specified segment and
        returns the obtained list of points in the form
        points = [[x_0, y_0],[x_1, y_1],...,[x_n, y_n]]

        From:
        https://bitesofcode.wordpress.com/2016/12/23/landscape-generation-using-midpoint-displacement/

        """
        # Final number of points = (2^iterations)+1
        if vertical_displacement is None:
            # if no initial displacement is specified set displacement to:
            #  (y_start+y_end)/2
            vertical_displacement = (start[1] + end[1]) / 2
        # Data structure that stores the points is a list of lists where
        # each sublist represents a point and holds its x and y coordinates:
        # points=[[x_0, y_0],[x_1, y_1],...,[x_n, y_n]]
        #              |          |              |
        #           point 0    point 1        point n
        # The points list is always kept sorted from smallest to biggest x-value
        points = [start, end]
        iteration = 1
        while iteration <= num_of_iterations:
            # Since the list of points will be dynamically updated with the new computed
            # points after each midpoint displacement it is necessary to create a copy
            # of the state at the beginning of the iteration so we can iterate over
            # the original sequence.
            # Tuple type is used for security reasons since they are immutable in Python.
            points_tup = tuple(points)
            for i in range(len(points_tup) - 1):
                # Calculate x and y midpoint coordinates:
                # [(x_i+x_(i+1))/2, (y_i+y_(i+1))/2]
                midpoint = list(map(lambda x: (points_tup[i][x] + points_tup[i + 1][x]) / 2,
                                    [0, 1]))
                # Displace midpoint y-coordinate
                midpoint[1] += random.choice([-vertical_displacement,
                                              vertical_displacement])
                # Insert the displaced midpoint in the current list of points
                bisect.insort(points, midpoint)
                # bisect allows to insert an element in a list so that its order
                # is preserved.
                # By default the maintained order is from smallest to biggest list first
                # element which is what we want.
            # Reduce displacement range
            vertical_displacement *= 2 ** (-roughness)
            # update number of iterations
            iteration += 1

        return points
