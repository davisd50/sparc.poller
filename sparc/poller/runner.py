import threading
from zope import component
from zope import interface
from sparc.poller.stopper import ThreadingEventPollerStopper
from .interfaces import ISparcPoller
from .interfaces import ISparcPollerRunnerGroup

import logging
logger = logging.getLogger(__name__)

interface.implementer(ISparcPollerRunnerGroup)
class SparcThreadedPollerRunnerGroup(object):
    """Poller group runner
    
    Args:
        pollers: Iterable of ISparcPollerRunner providers
        name: String unique identifier to give to the runner
    
    Usage:
    >>> my_pollers = set(poller_1, poller_2) # where poller_1/2 are some ISparcPollerRunner providers
    >>> g_runner = SparcThreadedPollerRunnerGroup(my_pollers, 'my name')
    >>> import threading
    >>> t = threading.Thread(target=g_runner.start)
    >>> t.start() #executes g_runner.start() in a thread
    >>> g_runner.is_active() #reports status
    True
    >>> g_runner.cancel() #blocks until all runners are canceled
    >>> g_runner.is_active()
    False
    """
    
    def __init__(self, pollers, name, raise_exceptions=False):
        self._raise = raise_exceptions
        self._lock = threading.RLock()
        self._threads = set()
        self._stop = ThreadingEventPollerStopper()
        self.pollers = pollers
        self._name = name
    
    #ISparcPollerRunner
    def is_active(self):
        with self._lock:
            active = len(self._threads) > 0
        return active
    
    def stop(self):
        logger.info("Stop called on group poller runner {}, stopping threads immediately")
        self._stop_join_and_remove_threads()
    
    def __str__(self):
        return self.name
    
    def start(self):
        if self.is_active():
            logger.warning("attempt made to restart active poller group, unable to restart active poller group.")
            return
        logger.info("Starting poller group runner {}".format(self))
        try:
            for poller in self.pollers:
                logger.info("launching poller {} with cycle delay {} seconds".format(poller, poller.delay))
                with self._lock:
                    t = threading.Thread(target=self.poll, args=(poller))
                    t.start()
                    self._threads.add(t)
            for t in self._threads:
                t.join()
            logger.info("All pollers are completed for {}".format(self))
        finally:
            if self.is_active():
                logger.info("Alive poller threads found for {}, shutting them down now.".format(self))
                self.stop()
                logger.info("All poller threads have been stopped and removed for {}".format(self))
            with self._lock:
                self._stop.clear()
    
    #Support Methods
    def _stop_join_and_remove_threads(self):
        with self._lock:
            self._stop.stop()
            for t in self._threads:
                t.join()
            self._threads &= set() #reset set, while keeping reference
            self._stop.clear()
        
    def poll(self, poller, stopper):
        while True:
            try:
                if self._stop.is_stopped():
                    return
                logger.info("executing poller {} in group runner {}".format(poller, self))
                poller(self._stop)
                logger.info("finished executing poller {} in group runner {}, delaying {} seconds until next run.".format(poller, self, poller.delay))
            except Exception as e:
                logger.exception(e)
                if self._raise:
                    raise e
            self._stop.wait(poller.delay) #blocks for delay, unless stopper is triggered (then releases immediately)


interface.implementer(ISparcPollerRunnerGroup)
class SparcThreadedRegisteredPollerRunner(SparcThreadedPollerRunnerGroup):
    def __init__(self, raise_exceptions=False):
        super(SparcThreadedRegisteredPollerRunner, self).__init__(
                            pollers=self.pollers(),
                            name="Registered poller runner at {}".format(id(self)))
    
    def pollers(self):
        for poller in component.getAllUtilitiesRegisteredFor(ISparcPoller):
            yield poller