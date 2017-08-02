import threading
from zope.component.factory import Factory
from zope import interface
from .interfaces import ISparcPollerStoppableCall, ISparcPollerStopper

@interface.implementer(ISparcPollerStopper)
class ThreadingEventPollerStopper(object):
    
    def __init__(self, event=None):
        self._stop = threading.Event() if not event else event
    
    def is_stopped(self):
        return self._stop.is_set()
    
    def stop(self):
        self._stop.set()
    
    def clear(self):
        self._stop.clear()
    
    def wait(self, timeout=None):
        self._stop.wait(timeout)
ThreadingEventPollerStopperFactory = Factory(ThreadingEventPollerStopper)

@interface.implementer(ISparcPollerStoppableCall)
class StoppableCall(object):
    def __init__(self, stoppable_call):
        self._stoppable_call = stoppable_call
        
    def __call__(self, stopper):
        self._stoppable_call(stopper)
StoppableCallFactory = Factory(StoppableCall)