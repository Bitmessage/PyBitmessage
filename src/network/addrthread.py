"""
Announce addresses as they are received from other hosts
"""
from six.moves import queue


import state
from helper_random import randomshuffle
from network.assemble import assemble_addr
from network.connectionpool import BMConnectionPool
from queues import addrQueue
from threads import StoppableThread


class AddrThread(StoppableThread):
    """(Node) address broadcasting thread"""
    name = "AddrBroadcaster"

    def run(self):
        while not state.shutdown:
            chunk = []
            while True:
                try:
                    data = addrQueue.get(False)
                    chunk.append(data)
                except queue.Empty:
                    break

            if chunk:
                # Choose peers randomly
                connections = BMConnectionPool().establishedConnections()
                randomshuffle(connections)
                for i in connections:
                    randomshuffle(chunk)
                    filtered = []
                    for stream, peer, seen, destination in chunk:
                        # peer's own address or address received from peer
                        if i.destination in (peer, destination):
                            continue
                        if stream not in i.streams:
                            continue
                        filtered.append((stream, peer, seen))
                    if filtered:
                        i.append_write_buf(assemble_addr(filtered))

            addrQueue.iterate()
            for i in range(len(chunk)):
                addrQueue.task_done()
            self.stop.wait(1)
