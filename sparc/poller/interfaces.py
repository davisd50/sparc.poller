from zope import interface

class ISparcPollerStopper(interface.Interface):
    """Stopping mechanism for active pollers"""
    def is_stopped():
        """True indicates the stopping mechanism has been previously triggered"""
    def stop():
        """Triggers the stopping mechanism"""
    def clear():
        """Reset the stopping mechanism"""
    def wait(timeout):
        """Block floating timeout seconds until stop is called"""

class ISparcPoller(interface.Interface):
    """A Sparc poller"""
    def __str__():
        """Poller identity"""
    def start(stop):
        """Poller activity.  Well behaved pollers will periodically check to 
        see if they are cancelled.
        
        Args:
            stop: ISparcPollerStopper provider
        """

class ISparcPollerRunner(interface.Interface):
    """A Sparc poller runner"""
    delay = interface.Attribute("Minimum Integer delay in seconds between poler runs")
    poller = interface.Attribute("ISparcPoller provider")

class ISparcPollerRunnerGroup(interface.Interface):
    """Concurrently runs pollers"""
    pollers = interface.Attribute('Set of ISparcPollerRunner providers run by call')
    def __str__():
        """Group poller runner identity"""
    def start():
        """Runs all pollers concurrrently in infinite loop"""
    def stop():
        """Blocks and cancels all running group pollers"""
    def is_active():
        """True indicates that pollers are currently active"""