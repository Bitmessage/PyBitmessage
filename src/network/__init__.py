"""
Network subsystem package
"""

from announcethread import AnnounceThread
from connectionpool import BMConnectionPool
from receivequeuethread import ReceiveQueueThread
from threads import StoppableThread


__all__ = [
    "AnnounceThread", "BMConnectionPool",
    "ReceiveQueueThread", "StoppableThread"
    # "AddrThread", "AnnounceThread", "BMNetworkThread", "Dandelion",
    # "DownloadThread", "InvThread", "UploadThread",
]


def start():
    """Start network threads"""
    from addrthread import AddrThread
    from dandelion import Dandelion
    from downloadthread import DownloadThread
    from invthread import InvThread
    from networkthread import BMNetworkThread
    from knownnodes import readKnownNodes
    from uploadthread import UploadThread

    readKnownNodes()
    # init, needs to be early because other thread may access it early
    Dandelion()
    BMConnectionPool().connectToStream(1)
    asyncoreThread = BMNetworkThread()
    asyncoreThread.daemon = True
    asyncoreThread.start()
    invThread = InvThread()
    invThread.daemon = True
    invThread.start()
    addrThread = AddrThread()
    addrThread.daemon = True
    addrThread.start()
    downloadThread = DownloadThread()
    downloadThread.daemon = True
    downloadThread.start()
    uploadThread = UploadThread()
    uploadThread.daemon = True
    uploadThread.start()
