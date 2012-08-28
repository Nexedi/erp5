##############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors.
#
##############################################################################

import os
from select import select
from threading import Thread
from Products.LongRequestLogger.dumper import Dumper

class Monitor(Thread):
    """Logs the stack-trace of a thread until it's stopped

    m = Monitor(dumper)

    Wait dumper.timeout seconds before calling dumper() every
    dumper.interval seconds.

    m.stop()

    Stop the monitoring, whether timed-out or not
    """

    dumper = None

    def __init__(self, dumper=None):
        Thread.__init__(self)
        if dumper is None:
            dumper = Dumper()
        if dumper.is_enabled():
            self._event_pipe = os.pipe()
            self.dumper = dumper
            self.start()

    def waiting(self, timeout):
        r, _ = self._event_pipe
        read_ready_list, _, _ = select([r], [], [], timeout)
        if read_ready_list:
            os.read(r, 1)
            # stop() called by monitored thread.
            # Stop waiting:
            return False
        # Still waiting for the other thread to finish
        return True

    def stop(self):
        """Stop monitoring the other thread"""
        if self.dumper is not None:
            r, w = self._event_pipe
            os.write(w, '\0')
            self.join()
            map(os.close, self._event_pipe)

    def run(self):
        timeout = self.dumper.timeout
        while self.waiting(timeout):
            self.dumper()
            timeout = self.dumper.interval
