#import collections
from threading import current_thread, enumerate as threadingEnumerate, RLock
import Queue
import time

#from helper_sql import *
from singleton import Singleton

@Singleton
class DownloadQueue(Queue.Queue):
    # keep a track of objects that have been advertised to us but we haven't downloaded them yet
    maxWait = 300
