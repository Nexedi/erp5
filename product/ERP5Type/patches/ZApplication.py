##############################################################################
#
# Copyright (c) 2001, 2002 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""
Make sure that ZODB Connections are closed when ZPublisher has processed a request
"""

from App import ZApplication
from App.ZApplication import ZApplicationWrapper, connection_open_hooks

if 1:

    def __bobo_traverse__(self, REQUEST=None, name=None):
        db, aname = self._stuff
        conn = db.open()

        if connection_open_hooks:
            for hook in connection_open_hooks:
                hook(conn)

        # arrange for the connection to be closed when the request goes away
        request_clear = REQUEST.clear
        def clear():
            request_clear()
            conn.close()
        REQUEST.clear = clear

        conn.setDebugInfo(REQUEST.environ, REQUEST.other)

        v=conn.root()[aname]

        if name is not None:
            if hasattr(v, '__bobo_traverse__'):
                return v.__bobo_traverse__(REQUEST, name)

            if hasattr(v,name): return getattr(v,name)
            return v[name]

        return v

    ZApplicationWrapper.__bobo_traverse__ = __bobo_traverse__

    del ZApplication.Cleanup
