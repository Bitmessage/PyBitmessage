"""
The objectProcessor thread, of which there is only one,
processes the network objects
"""
import logging
import random
import threading

import queues
import state

# from helper_sql import sql_ready, sqlExecute, sqlQuery
# from network import bmproto

logger = logging.getLogger('default')


class objectProcessor(threading.Thread):
    """
    The objectProcessor thread, of which there is only one, receives network
    objects (msg, broadcast, pubkey, getpubkey) from the receiveDataThreads.
    """
    def __init__(self):
        threading.Thread.__init__(self, name="objectProcessor")
        random.seed()
        # It may be the case that the last time Bitmessage was running,
        # the user closed it before it finished processing everything in the
        # objectProcessorQueue. Assuming that Bitmessage wasn't closed
        # forcefully, it should have saved the data in the queue into the
        # objectprocessorqueue table. Let's pull it out.

        # sql_ready.wait()
        # queryreturn = sqlQuery(
        #     'SELECT objecttype, data FROM objectprocessorqueue')
        # for objectType, data in queryreturn:
        #     queues.objectProcessorQueue.put((objectType, data))
        # sqlExecute('DELETE FROM objectprocessorqueue')
        # logger.debug(
        #     'Loaded %s objects from disk into the objectProcessorQueue.',
        #     len(queryreturn))
        # self._ack_obj = bmproto.BMStringParser()
        self.successfullyDecryptMessageTimings = []

    def run(self):
        """Process the objects from `.queues.objectProcessorQueue`"""
        while True:
            # pylint: disable=unused-variable
            objectType, data = queues.objectProcessorQueue.get()

            if state.shutdown:
                state.shutdown = 2
                break
