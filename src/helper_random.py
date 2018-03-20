import os
import random
from pyelliptic.openssl import OpenSSL


def randomBytes(n):
    """Method randomBytes."""
    try:
        return os.urandom(n)
    except NotImplementedError:
        return OpenSSL.rand(n)


def randomshuffle(population):
    """Method randomShuffle.

    shuffle the sequence x in place.
    shuffles the elements in list in place,
    so they are in a random order.
    """
    return random.shuffle(population)


def randomsample(population, k):
    """Method randomSample.

    return a k length list of unique elements
    chosen from the population sequence.
    Used for random sampling
    without replacement
    """
    return random.sample(population, k)


def randomrandrange(x, y):
    """Method randomRandrange.

    return a randomly selected element from
    range(start, stop). This is equivalent to
    choice(range(start, stop)),
    but doesnt actually build a range object.
    """
    return random.randrange(x, y)
