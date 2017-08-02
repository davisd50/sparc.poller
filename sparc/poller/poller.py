from zope.component.factory import Factory
from zope import interface

from .interfaces import ISparcPoller, ISparcPollerRunner

@interface.implementer(ISparcPoller)
class SparcPoller(object):
    def __init__(self, name, stoppable_call):
        """A generic poller
        
        kwargs:
            name: String name of the poller.  will be returned by calls to __str__()
            stoppable_call: sparc.poller.ISparcPollerStoppableCall provider
        """
        self._name = name
        self._stoppable_call = stoppable_call
    
    def __str__(self):
        return self._name
    
    def run(self, stopper):
        self._stoppable_call(stopper)
SparcPollerFactory = Factory(SparcPoller)

@interface.implementer(ISparcPollerRunner)
class SparcPollerRunner(object):
    def __init__(self, delay, poller):
        self.delay = delay
        self.poller = poller
SparcPollerRunnerFactory = Factory(SparcPollerRunner)