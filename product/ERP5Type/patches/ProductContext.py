##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2002,2005 Nexedi SARL and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

# AttrDict patch for more dict-like methods.
try:
    from App.ProductContext import AttrDict

    def AttrDict_getitem(self, name):
        try:
            return getattr(self.ob, name)
        except AttributeError:
            raise KeyError

    def AttrDict_has_key(self, name):
        return hasattr(self.ob, name)

    AttrDict.__getitem__ = AttrDict_getitem
    AttrDict.has_key = AttrDict_has_key
except ImportError:
    pass
