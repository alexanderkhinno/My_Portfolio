"""
An artificial life simulation.
Rabbits hopping around a field of grass.

Model B:  Grass grows back!   What happens?

"""

import random as rnd
import copy
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation


ARRSIZE = 200   # The dimensions of the field
FIGSIZE = 8     # The size of the animation (inches)
INIT_RABBITS = 100  # Initial # of rabbits
GRASS_RATE = 0.1  # Probability that grass grows back at any given location


class Rabbit:
    def __init__(self):
        """ Constructor """
        self.x = rnd.randrange(0, ARRSIZE)
        self.y = rnd.randrange(0, ARRSIZE)
        self.eaten = 0  # how much grass the rabbit has consumed

    def move(self):
        """ Moving up, down, left, right randomly
        In this world the field wraps around """
        self.x = (self.x + rnd.choice([-1, 0, 1])) % ARRSIZE
        self.y = (self.y + rnd.choice([-1, 0, 1])) % ARRSIZE

    def eat(self, amount):
        self.eaten += amount

    def reproduce(self):
        self.eaten = 0
        return copy.deepcopy(self)


class Field:
    """ A field is a patch of grass with 0 or more rabbits hopping around """

    def __init__(self):
        self.rabbits = []   # a list of rabbit objects
        self.field = np.ones(shape=(ARRSIZE, ARRSIZE), dtype=int)

    def add_rabbit(self, rabbit):
        """ A new rabbit is added to the field """
        self.rabbits.append(rabbit)

    def move(self):
        """ All the rabbits move! """
        for r in self.rabbits:
            r.move()

    def eat(self):
        """ Rabbits eat grass (if they find grass where they are) """
        for r in self.rabbits:
            r.eat(self.field[r.x, r.y])
            self.field[r.x, r.y] = 0

    def grow(self):
        """ Grass grows back with some probability at each location """
        growloc = (np.random.rand(ARRSIZE, ARRSIZE) < GRASS_RATE) * 1
        self.field = np.maximum(self.field, growloc)

    def generation(self):
        """ One generation of rabbits """
        self.move()
        self.eat()
        self.grow()


def animate(i, field, im):
    field.generation()
    im.set_array(field.field)   # inject updated data into the image
    plt.title(f"generation: {i}  Nrabbits: {len(field.rabbits)}")
    return im,  # don't forget the comma!


def main():

    # Create the field object (ecosystem)
    field = Field()

    # Add some rabbits at random locations
    for _ in range(INIT_RABBITS):
        field.add_rabbit(Rabbit())

    # Set up the animation with FuncAnimation
    fig = plt.figure(figsize=(FIGSIZE, FIGSIZE))
    im = plt.imshow(field.field, cmap='viridis', interpolation='hamming', vmin=0, vmax=1)
    anim = animation.FuncAnimation(fig, animate, fargs=(field, im), frames=5000, interval=1)
    plt.show()


if __name__ == '__main__':
    main()
