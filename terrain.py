from sprites import X, Y
import random


MAX_TERRAIN = 50
MIN_TERRAIN = 0


class OutOfMapException(Exception):
    pass


class Terrain:
    def __init__(self, dimension):

        # Game details
        self._dimension = dimension

        # Terrain Generation
        self._terrain = []

    def generate_terrain(self):
        previous_height = random.randint(MIN_TERRAIN, MAX_TERRAIN)
        for x in range(0, self._dimension[X]):
            self._terrain.append(self._random_height(previous_height))  # Generate and save current height
            previous_height = self._terrain[x]  # Save off for previous in next iteration

    def intersects_terrain(self, location, buffer_x=0, buffer_y=0):
        # TODO Add a buffer to calculation to make it easier
        if location[X] > self._dimension[X]:
            # thing is out of the map
            raise OutOfMapException("Projectile out of map to the right.")
        elif location[X] < self._dimension[X]:
            # thing is out side of the map
            raise OutOfMapException("Projectile out of map to the left.")

        # We made it here, the thing is still in the map
        if self._terrain[location[X]] >= location[Y]:
            # Terrain is over or equal to height of projectile at this X location, we intersect
            return True
        else:
            # Otherwise we do not intersect
            return False

    def _random_height(self, previous_height):
        greater = random.randint(0, 100) > 50  # Generate a yes no

        if greater:
            return random.randint(previous_height, MAX_TERRAIN)
        else:
            return random.randint(MIN_TERRAIN, previous_height)

