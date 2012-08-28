##############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors.
#
##############################################################################


def initialize(context):
    from Products.LongRequestLogger.dumper import do_enable
    from Products.LongRequestLogger.patch import do_patch
    if do_enable():
        # if not enabled on startup, it won't be enabled, period.
        # it can be disabled at runtime afterwards, but will not be unpatched.
        do_patch()

