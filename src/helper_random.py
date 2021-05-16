"""Convenience functions for random operations. Not suitable for security / cryptography operations."""

import os
import random

from pyelliptic.openssl import OpenSSL

NoneType = type(None)


def seed():
    """Initialize random number generator"""
    random.seed()


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
    As Shuffle will alter data in-place,
    so its input must be a mutable sequence.
    In contrast, sample produces a new list
    and its input can be much more varied
    (tuple, string, xrange, bytearray, set, etc)
    """
    random.shuffle(population)


def randomsample(population, k):
    """Method randomSample.

    return a k length list of unique elements
    chosen from the population sequence.
    Used for random sampling
    without replacement, its called
    partial shuffle.
    """
    return random.sample(population, k)


def randomrandrange(x, y=None):
    """Method randomRandrange.

    return a randomly selected element from
    range(start, stop). This is equivalent to
    choice(range(start, stop)),
    but doesnt actually build a range object.
    """
    if isinstance(y, NoneType):
        return random.randrange(x)  # nosec
    return random.randrange(x, y)  # nosec


def randomchoice(population):
    """Method randomchoice.

    Return a random element from the non-empty
    sequence seq. If seq is empty, raises
    IndexError.
    """
    return random.choice(population)  # nosec
