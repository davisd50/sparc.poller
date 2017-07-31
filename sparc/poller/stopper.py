import threading
from zope.component.factory import Factory
from zope import interface
from .interfaces import ISparcPollerStopper

@interface.implementer(ISparcPollerStopper)
class ThreadingEventPollerStopper(object):
    
    def __init__(self):
        self._stop = threading.Event()
    
    def is_stopped(self):
        return self._stop.is_set()
    
    def stop(self):
        self._stop.set()
    
    def clear(self):
        self._stop.clear()
    
    def wait(self, timeout):
        self._stop.wait(timeout)

ThreadingEventPollerStopperFactory = Factory(ThreadingEventPollerStopper)