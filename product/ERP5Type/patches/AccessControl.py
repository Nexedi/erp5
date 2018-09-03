##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
# Copyright (c) 2018 Nexedi SARL and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import AccessControl.users
from Acquisition import aq_inContextOf, aq_base

# Patch description:
# Original _check_context checks whether given "object" is a method by
# accessing im_self on it. If there is none, it will suddenly be trying to
# acquire one (and failing to, which is good). That acquisition costs a lot
# of time compared to this method simplicity.
# Instead, backport part of
#  https://github.com/zopefoundation/AccessControl/commit/14db9b87483471b15e442c10bab1400c88b079a5
# which switched to __self__ attribute. As this attribute starts with an
# underscore, acquisition will ignore it, avoiding this waste of time.
def _check_context(self, object):
    # Check that 'object' exists in the acquisition context of
    # the parent of the acl_users object containing this user,
    # to prevent "stealing" access through acquisition tricks.
    # Return true if in context, false if not or if context
    # cannot be determined (object is not wrapped).
    parent = getattr(self, '__parent__', None)
    context = getattr(parent, '__parent__', None)
￼   if context is not None:
￼       if object is None:
￼           return 1
￼       if getattr(object, '__self__', None) is not None:
￼           # This is a method.  Grab its self.
￼           object = object.__self__
￼       return aq_inContextOf(object, context, 1)

AccessControl.users.BasicUser._check_context = _check_context
