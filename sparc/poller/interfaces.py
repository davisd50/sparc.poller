from zope import interface

class ISparcPollerStopper(interface.Interface):
    """Stopping mechanism for active pollers"""
    def is_stopped():
        """True indicates the stopping mechanism has been previously triggered"""
    def stop():
        """Triggers the stopping mechanism"""
    def clear():
        """Reset the stopping mechanism"""
    def wait(timeout=None):
        """Block floating timeout seconds until stop is called"""

class ISparcPollerStoppableCall(interface.Interface):
    """A callable with a stopping mechanism"""
    def __call__(stopper):
        """A callable target with a stopping mechanism
        
        Returns when completed or when stopper is triggered.
        
        kwargs:
           stopper:  ISparcPollerStopper provider
        
        Returns:
            None
        """

class ISparcPoller(interface.Interface):
    """A Sparc poller"""
    def __str__():
        """Poller identity"""
    def run(stopper):
        """Poller activity.  Well behaved pollers will periodically check to 
        see if they are cancelled.
        
        Args:
            stopper: ISparcPollerStopper provider
        
        Returns:
            None
        """

class ISparcPollerRunner(interface.Interface):
    """A Sparc poller runner"""
    delay = interface.Attribute("Minimum Integer delay in seconds between poler runs")
    poller = interface.Attribute("ISparcPoller provider")

class ISparcPollerRunnerController(interface.Interface):
    """Controls concurrently executing poller runners"""
    def __str__():
        """Group poller runner identity"""
    def start(pollers):
        """Runs pollers concurrently in infinite loop
        
        kwargs:
            poller: Iterable of ISparcPollerRunner providers.
        """
    def pollers():
        """Returns iterable of ISparcPollerRunner providers previously started and not removed"""
    def remove(pollers):
        """Block and stops pollers then removes them from controller, they will no longer be returned by calls to poller() method"""
    def stop(pollers):
        """Blocks and stops pollers"""
    def is_active(poller):
        """True indicates that pollers are currently active"""