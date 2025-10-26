"""
A demonstration of sorting using evocomp without
implementing an explicit sorting algorithm
"""

from dstrut.evo_p import Evo
import random as rnd


def unsorted(L):
    return sum ([x-y for x, y in zip(L, L[1:]) if y<x])

def sumratio(L):
    """ Ratio of sum of first-half values to 2nd half values """
    sz = len(L)
    return round(sum(L[:sz//2]) / sum(L[sz//2+1:]), 5)





def swapper(solutions):
    L = solutions[0]
    i = rnd.randrange(0, len(L))
    j = rnd.randrange(0, len(L))
    L[i], L[j] = L[j], L[i]
    return L



def main():

    # Create our Evo instance
    E = Evo()

    # Register the objectives
    E.add_objective("unsorted", unsorted)
    E.add_objective("sumratio", sumratio)

    # Register agents
    E.add_agent("swapper", swapper, k=1)

    # Add an intial solution
    N = 50
    L = [rnd.randrange(1, 100) for _ in range(N)]
    E.add_solution(L)
    print(E)

    E.evolve(n=10**100, dom=100)
    print(E)


main()
