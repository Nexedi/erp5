##############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors.
#
##############################################################################

import time

class Sleeper(object):
    """This class exists solely to inflate the stack trace, and to be in a
    file where the stack trace won't be affected by editing of the test file
    that uses it.
    """

    def __init__(self, interval):
      self.interval = interval

    def sleep(self):
        self._sleep1()

    def _sleep1(self):
        self._sleep2()

    def _sleep2(self):
        time.sleep(self.interval)

class App(object):

    def __call__(self, interval):
        Sleeper(interval).sleep()
        return "OK"

# Enable this module to be published with ZPublisher.Publish.publish_module()
bobo_application = App()
