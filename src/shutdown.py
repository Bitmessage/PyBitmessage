import os
import queue as Queue
import threading
import time

from debug import logger
from helper_sql import sqlQuery, sqlStoredProcedure
from helper_threading import StoppableThread
from knownnodes import saveKnownNodes
from inventory import Inventory
from queues import (
    addressGeneratorQueue, objectProcessorQueue, UISignalQueue, workerQueue)
import shared
import state


def doCleanShutdown():
    # Used to tell proof of work worker threads
    # and the objectProcessorThread to exit.
    state.shutdown = 1

    objectProcessorQueue.put(('checkShutdownVariable', 'no data'))
    for thread in threading.enumerate():
        if thread.isAlive() and isinstance(thread, StoppableThread):
            thread.stopThread()

    UISignalQueue.put((
        'updateStatusBar',
        'Saving the knownNodes list of peers to disk...'))
    logger.info('Saving knownNodes list of peers to disk')
    saveKnownNodes()
    logger.info('Done saving knownNodes list of peers to disk')
    UISignalQueue.put((
        'updateStatusBar',
        'Done saving the knownNodes list of peers to disk.'))
    logger.info('Flushing inventory in memory out to disk...')
    UISignalQueue.put((
        'updateStatusBar',
        'Flushing inventory in memory out to disk.'
        ' This should normally only take a second...'))
    Inventory().flush()

    # Verify that the objectProcessor has finished exiting. It should have
    # incremented the shutdown variable from 1 to 2. This must finish before
    # we command the sqlThread to exit.
    while state.shutdown == 1:
        time.sleep(.1)

    # Wait long enough to guarantee that any running proof of work worker
    # threads will check the shutdown variable and exit. If the main thread
    # closes before they do then they won't stop.
    time.sleep(.25)

    for thread in threading.enumerate():
        if (thread is not threading.currentThread() and
            isinstance(thread, StoppableThread) and
                thread.name != 'SQL'):
            logger.debug("Waiting for thread %s", thread.name)
            thread.join()

    # This one last useless query will guarantee that the previous flush
    # committed and that the
    # objectProcessorThread committed before we close the program.
    sqlQuery('SELECT address FROM subscriptions')
    logger.info('Finished flushing inventory.')
    sqlStoredProcedure('exit')

    # flush queues
    for queue in (
            workerQueue, UISignalQueue, addressGeneratorQueue,
            objectProcessorQueue):
        while True:
            try:
                queue.get(False)
                queue.task_done()
            except Queue.Empty:
                break

    if shared.thisapp.daemon or not state.enableGUI: # FIXME redundant?
        logger.info('Clean shutdown complete.')
        shared.thisapp.cleanup()
        os._exit(0)
    else:
        logger.info('Core shutdown complete.')
    for thread in threading.enumerate():
        logger.debug('Thread %s still running', thread.name)
