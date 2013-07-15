#! /usr/bin/python
# -*- coding: utf-8 -*-
# cody by linker.lin@me.com

__author__ = 'linkerlin'


import threading
import Queue
import time

class bgWorker(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.q = Queue.Queue()
        self.setDaemon(True)

    def post(self,job):
        self.q.put(job)

    def run(self):
        while 1:
            job=None
            try:
                job = self.q.get(block=True)
                if job:
                    job()
            except Exception as ex:
                print "Error,job exception:",ex.message,type(ex)
                time.sleep(0.05)
            else:
                #print "job: ", job, " done"
                pass
            finally:
                time.sleep(0.05)

bgworker = bgWorker()
bgworker.start()
