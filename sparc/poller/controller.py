import threading
from zope.component.factory import Factory
from zope import interface
from sparc.poller.stopper import ThreadingEventPollerStopper
from .interfaces import ISparcPollerRunnerController

import logging
logger = logging.getLogger(__name__)

interface.implementer(ISparcPollerRunnerController)
class SparcThreadedPollerRunnerController(object):
    """Poller group controller
    
    Args:
        name: String unique identifier to give to the runner
    Kwargs:
        raise_exceptions: True indicates to re-raise exceptions from pollers
    """
    
    def __init__(self, name, raise_exceptions=False):
        self._raise = raise_exceptions
        self._name = name
        self._pollers = {} # {poller: {'thread':threading.Thread(), 'stopper':stopper}}
    
    #ISparcPollerRunnerController
    def __str__(self):
        return self._name

    def pollers(self):
        return self._pollers.keys()
        
    def is_active(self, poller):
        if poller in self._pollers:
            return self._pollers[poller]['thread'].is_alive()
        return False
    
    def stop(self, pollers):
        for poller in pollers:
            if self.is_active(poller):
                logger.debug("Stop called on active thread poller runner {} on controller {}, stopping thread {}.".format(poller, self, self._pollers[poller]['thread'].name))
                self._pollers[poller]['stopper'].stop()
                self._pollers[poller]['thread'].join() #blocks
                logger.debug("Stopped thread {} for poller runner {} on controller {}".format(self._pollers[poller]['thread'].name, poller, self))
            if poller in self._pollers: 
                #reset the poller thread entry
                self._pollers[poller] = self._poller_thread_entry(poller) 

    def remove(self, pollers):
        self.stop(pollers)
        for poller in pollers:
            if poller in self._pollers:
                del self._pollers[poller]
                logger.debug("Removed poller runner {} from controller {}".format(poller, self))
    
    def start(self, pollers):
        for poller in pollers:
            if poller not in self._pollers:
                _stopper = ThreadingEventPollerStopper()
                self._pollers[poller] = self._poller_thread_entry(poller)
                logger.debug("Added new poller runner {} on thread {} to controller {}".format(poller, self._pollers[poller]['thread'].name, self))
            elif self._pollers[poller]['thread'].is_alive():
                logger.debug("Attempt was made to start the already executing poller runner {} on controller {}, skipping".format(poller, self))
                continue
            elif self._pollers[poller]['thread'].ident: #indicates threads start() method has already been called (e.g. can not be called again)
                logger.debug(
                    "Start called on already executed but no longer running poller runner {}, reseting poller thread {} on controller {}".format(poller, self._pollers[poller]['thread'].name, self))
                self._pollers[poller] = self._poller_thread_entry(poller)
                logger.debug("Reset poller runner {} thread to {} on controller {}".format(poller, self._pollers[poller]['thread'].name, self))
            self._pollers[poller]['thread'].start()
            logger.debug("Starter poller runner {} on thread {} for controller {}".format(poller, self._pollers[poller]['thread'].name, self))
    
    #Support Methods
    def _poller_thread_entry(self, poller):
        _stopper = ThreadingEventPollerStopper()
        return \
                {'thread': threading.Thread(target=self.poll,
                                            args=(poller, _stopper,)),
                 'stopper': _stopper
                 }
        
    def poll(self, poller, stopper):
        while True:
            try:
                if stopper.is_stopped():
                    return
                poller.poller.run(stopper)
                logger.info("finished executing poller {} in controller {}, delaying {} seconds until next run.".format(poller, self, poller.delay))
            except Exception as e:
                logger.exception(e)
                if self._raise:
                    raise e
            stopper.wait(poller.delay) #blocks for delay, unless stopper is triggered (then releases immediately)
SparcThreadedPollerRunnerControllerFactory = Factory(SparcThreadedPollerRunnerController)
