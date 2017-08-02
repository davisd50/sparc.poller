import os
import unittest
import zope.testrunner
from sparc.testing.fixture import test_suite_mixin
from sparc.poller.testing import SPARC_POLLER_INTEGRATION_LAYER

import time
from zope import component

class ExceptionTest(Exception):
    pass

my_call_3_counter = 0
class SparcPollerControllerTestCase(unittest.TestCase):
    layer = SPARC_POLLER_INTEGRATION_LAYER
    
    def setUp(self):
        self.ctlrs = set()
    
    def tearDown(self):
        for ctlr in self.ctlrs:
            ctlr.stop(ctlr.pollers())
    
    def test_controller_raises(self):
        def my_call_2(stopper):
            raise ExceptionTest('Test exception, unit tests can ignore this.')
        def my_call_3(stopper):
            global my_call_3_counter
            my_call_3_counter += 1
        
        s_call_2 = component.createObject(u"sparc.poller.stoppable_call", my_call_2)
        s_call_3 = component.createObject(u"sparc.poller.stoppable_call", my_call_3)
        poller_2 = component.createObject(u"sparc.poller.poller",
                                name="test poller 2", stoppable_call=s_call_2)
        poller_3 = component.createObject(u"sparc.poller.poller",
                                name="test poller 3", stoppable_call=s_call_3)
        p_runner_2 = component.createObject(u"sparc.poller.poller_runner",
                                            delay=60, poller=poller_2)
        p_runner_3 = component.createObject(u"sparc.poller.poller_runner",
                                            delay=2, poller=poller_3)
        ctlr_2 = component.createObject("sparc.poller.threaded_poller_runner_controller",
                                        name='controller 2', raise_exceptions=True)
        self.ctlrs.add(ctlr_2) #for tearDown()
        ctlr_2.start([p_runner_2, p_runner_3]) #p_runner_2 raises
        time.sleep(1) #give the threads a little time to process
        self.assertFalse(ctlr_2.is_active(p_runner_2)) #p_runner_2 is no longer active
        self.assertTrue(ctlr_2.is_active(p_runner_3)) #p_runner_3 is no effected

class test_suite(test_suite_mixin):
    package = 'sparc.poller'
    module = 'controller'
    layer = SPARC_POLLER_INTEGRATION_LAYER
    
    def __new__(cls):
        suite = super(test_suite, cls).__new__(cls)
        suite.addTest(unittest.makeSuite(SparcPollerControllerTestCase))
        return suite


if __name__ == '__main__':
    zope.testrunner.run([
                         '--path', os.path.dirname(__file__),
                         '--tests-pattern', os.path.splitext(
                                                os.path.basename(__file__))[0]
                         ])