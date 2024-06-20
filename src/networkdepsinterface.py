
import state
import queues
import protocol
import paths
import randomtrackingdict
import addresses
from bmconfigparser import config


def importParentPackageDepsToNetwork():
    """
    Exports parent package dependencies to the network.
    """
    return (state, queues, config, protocol, randomtrackingdict, addresses, paths)
