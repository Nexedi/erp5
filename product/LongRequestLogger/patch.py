##############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors.
#
##############################################################################

import sys
from logging import getLogger
from Products.LongRequestLogger.monitor import Monitor

log = getLogger(__name__)

def wrapper(*args, **kw):
    monitor = Monitor()
    try:
        result = wrapper.original(*args, **kw)
        return result
    finally:
        monitor.stop()

def do_patch():
    from ZPublisher.Publish import publish_module_standard as original
    wrapper.original = original
    log.info('patching %s.%s' % (wrapper.original.__module__, 
                                 wrapper.original.__name__))
    setattr(sys.modules[wrapper.original.__module__],
            wrapper.original.__name__,
            wrapper)

def do_unpatch():
    setattr(sys.modules[wrapper.original.__module__],
            wrapper.original.__name__,
            wrapper.original)
