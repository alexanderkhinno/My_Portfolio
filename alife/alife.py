"""
An artificial life simulation.
Rabbits hopping around a field of grass.

Model Final:  Rabbits can reproduce!
This should be the starting point for HW5.

"""

import random as rnd
import copy
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import ListedColormap


ARRSIZE = 200   # The dimensions of the field
FIGSIZE = 8     # The size of the animation (inches)
INIT_RABBITS = 800  # Initial # of rabbits
INIT_FOXES = 100 # Initial # of foxes
GRASS_RATE = 0.50  # Probability that grass grows back at any given location
OFFSPRING = 5  # Maximum number of offspring

rabbit_pop = []
fox_pop = []


class Animal:
    def __init__(self, max_offspring=1, starvation_level=1, reproduction_level=1):
        """ Constructor """
        self.x = rnd.randrange(0, ARRSIZE)
        self.y = rnd.randrange(0, ARRSIZE)
        self.eaten = 0  # how much grass the rabbit has consumed
        self.max_offspring = max_offspring
        self.starvation_level = starvation_level
        self.reproduction_level = reproduction_level
        self.hunger = 0
        self.alive = True

    def move(self):
        """ Moving up, down, left, right randomly
        In this world the field wraps around """
        self.x = (self.x + rnd.choice([-1, 0, 1])) % ARRSIZE
        self.y = (self.y + rnd.choice([-1, 0, 1])) % ARRSIZE

    def eat(self, amount):
        """ Animals eat"""
        self.eaten += amount

    def reproduce(self):
        """ Animals make babies """
        #self.eaten = 0
        return copy.deepcopy(self)


class Field:
    """ A field is a patch of grass with 0 or more rabbits hopping around """

    def __init__(self):
        self.rabbits = []   # a list of rabbit objects
        self.foxes = []
        self.field = np.ones(shape=(ARRSIZE, ARRSIZE), dtype=int)

    def add_rabbit(self, rabbit):
        """ A new rabbit is added to the field """
        self.rabbits.append(rabbit)

    def add_fox(self, fox):
        self.foxes.append(fox)

    def move(self):
        """ All the rabbits move! """
        for r in self.rabbits + self.foxes:
            r.move()

    def eat(self):
        """ Rabbits eat grass (if they find grass where they are) """

        for r in self.rabbits:
            if r.alive and self.field[r.x, r.y] > 0:
                r.eat(self.field[r.x, r.y])
                self.field[r.x, r.y] = 0

        rabbit_map = {}
        for r in self.rabbits:
            if r.alive:
                key = (r.x, r.y)
                if key not in rabbit_map:
                    rabbit_map[key] = []
                rabbit_map[key].append(r)

        for f in self.foxes:
            key = (f.x, f.y)
            if key in rabbit_map:
                for r in rabbit_map[key]:
                    if r.alive:
                        r.alive = False
                        f.eat(1)

    def survive(self):
        """ Rabbits who eat some grass live to eat another day! """
        rabbit_survivors = []
        for r in self.rabbits:
            if r.eaten == 0:
                r.hunger +=1
                if r.hunger >= r.starvation_level:
                    r.alive = False
            else:
                r.hunger = 0
            r.eaten = 0
            if r.alive:
                rabbit_survivors.append(r)
        self.rabbits = rabbit_survivors

        fox_survivors = []
        for f in self.foxes:
            if f.eaten == 0:
                f.hunger += 1
                if f.hunger >= f.starvation_level:
                    f.alive = False
            else:
                f.hunger = 0
            f.eaten = 0
            if f.alive:
                fox_survivors.append(f)
        self.foxes = fox_survivors

    def grow(self):
        """ Grass grows back with some probability at each location """
        growloc = (np.random.rand(ARRSIZE, ARRSIZE) < GRASS_RATE) * 1
        self.field = np.maximum(self.field, growloc)

    def reproduce(self):
        """ animals reproduce like animals """

        rabbit_born = []
        for r in self.rabbits:
            if r.eaten >= r.reproduction_level:
                for _ in range(rnd.randint(0, r.max_offspring)):
                    rabbit_born.append(r.reproduce())

        self.rabbits += rabbit_born   # append the new rabbits to the field!

        fox_born = []
        for f in self.foxes:
            if f.eaten >= f.reproduction_level:
                for _ in range(rnd.randint(0,f.max_offspring)):
                    fox_born.append(f.reproduce())
        self.foxes += fox_born

    def generation(self):
        """ One generation of rabbits """
        self.move()
        self.eat()
        self.reproduce()
        self.survive()
        self.grow()

    def color_map(self):
        """ Create a color map"""
        display = np.copy(self.field)

        for r in self.rabbits:
            if r.alive:
                display[r.x, r.y] = 2 # white

        for f in self.foxes:
            if f.alive:
                display[f.x, f.y] = 3 # red

        return display


def animate(i, field, im):
    """ Creates the animation"""
    field.generation()
    im.set_array(field.color_map())   # inject updated data into the image
    plt.title(f"generation: {i}  Nrabbits: {len(field.rabbits)}")

    rabbit_pop.append(len(field.rabbits))
    fox_pop.append(len(field.foxes))

    return im,  # don't forget the comma!

def main():

    # Create the field object (ecosystem)
    field = Field()

    # Add some rabbits at random locations
    for _ in range(INIT_RABBITS):
        field.add_rabbit(Animal(starvation_level=2, reproduction_level=2))

    for _ in range(INIT_FOXES):
        field.add_fox(Animal(max_offspring=5, starvation_level=50, reproduction_level=1))

    # Set up the animation with FuncAnimation
    fig = plt.figure(figsize=(FIGSIZE, FIGSIZE))
    cmap = ListedColormap(['black', 'green', 'white', 'red'])
    im = plt.imshow(field.color_map(), cmap=cmap, interpolation='hamming', vmin=0, vmax=3)
    anim = animation.FuncAnimation(fig, animate, fargs=(field, im), frames=5000, interval=1)
    plt.show()

    plt.figure(figsize=(10, 5))
    plt.plot(rabbit_pop, label="Rabbits", color='gray')
    plt.plot(fox_pop, label="Foxes", color='red')
    plt.xlabel("Generation")
    plt.ylabel("Population")
    plt.title("Population of Rabbits and Foxes Over Time")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    main()
