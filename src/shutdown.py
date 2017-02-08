import os
import pickle
import Queue
import threading
import time

from class_outgoingSynSender import outgoingSynSender
from class_sendDataThread import sendDataThread
from configparser import BMConfigParser
from debug import logger
from helper_sql import sqlQuery, sqlStoredProcedure
from helper_threading import StoppableThread
from knownnodes import knownNodes, knownNodesLock
from inventory import Inventory
import protocol
from queues import addressGeneratorQueue, objectProcessorQueue, parserInputQueue, UISignalQueue, workerQueue
import shared
import state

def doCleanShutdown():
    state.shutdown = 1 #Used to tell proof of work worker threads and the objectProcessorThread to exit.
    try:
        parserInputQueue.put(None, False)
    except Queue.Full:
        pass
    protocol.broadcastToSendDataQueues((0, 'shutdown', 'no data'))   
    objectProcessorQueue.put(('checkShutdownVariable', 'no data'))
    for thread in threading.enumerate():
        if thread.isAlive() and isinstance(thread, StoppableThread):
            thread.stopThread()
    
    knownNodesLock.acquire()
    UISignalQueue.put(('updateStatusBar','Saving the knownNodes list of peers to disk...'))
    output = open(state.appdata + 'knownnodes.dat', 'wb')
    logger.info('finished opening knownnodes.dat. Now pickle.dump')
    pickle.dump(knownNodes, output)
    logger.info('Completed pickle.dump. Closing output...')
    output.close()
    knownNodesLock.release()
    logger.info('Finished closing knownnodes.dat output file.')
    UISignalQueue.put(('updateStatusBar','Done saving the knownNodes list of peers to disk.'))

    logger.info('Flushing inventory in memory out to disk...')
    UISignalQueue.put((
        'updateStatusBar',
        'Flushing inventory in memory out to disk. This should normally only take a second...'))
    Inventory().flush()

    # Verify that the objectProcessor has finished exiting. It should have incremented the 
    # shutdown variable from 1 to 2. This must finish before we command the sqlThread to exit.
    while state.shutdown == 1:
        time.sleep(.1)
    
    # This one last useless query will guarantee that the previous flush committed and that the
    # objectProcessorThread committed before we close the program.
    sqlQuery('SELECT address FROM subscriptions')
    logger.info('Finished flushing inventory.')
    sqlStoredProcedure('exit')
    
    # Wait long enough to guarantee that any running proof of work worker threads will check the
    # shutdown variable and exit. If the main thread closes before they do then they won't stop.
    time.sleep(.25)

    for thread in threading.enumerate():
        if isinstance(thread, sendDataThread):
            thread.sendDataThreadQueue.put((0, 'shutdown','no data'))
        if thread is not threading.currentThread() and isinstance(thread, StoppableThread) and not isinstance(thread, outgoingSynSender):
            logger.debug("Waiting for thread %s", thread.name)
            thread.join()

    # flush queued
    for queue in (workerQueue, UISignalQueue, addressGeneratorQueue, objectProcessorQueue):
        while True:
            try:
                queue.get(False)
                queue.task_done()
            except Queue.Empty:
                break

    if BMConfigParser().safeGetBoolean('bitmessagesettings','daemon'):
        logger.info('Clean shutdown complete.')
        shared.thisapp.cleanup()
        os._exit(0)
    else:
        logger.info('Core shutdown complete.')
    for thread in threading.enumerate():
        logger.debug("Thread %s still running", thread.name)
