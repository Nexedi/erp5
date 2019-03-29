# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

from Acquisition import aq_base

from zExceptions import MethodNotAllowed
from zExceptions import Forbidden

from webdav.common import UnsupportedMediaType
from webdav.common import Locked
from webdav.common import isDavCollection
from webdav.common import PreconditionFailed
from webdav.interfaces import IWriteLock

def MKCOL(self, REQUEST, RESPONSE):
    """Create a new collection resource."""
    self.dav__init(REQUEST, RESPONSE)
    if REQUEST.get('BODY', ''):
        raise UnsupportedMediaType('Unknown request body.')

    name=self.__name__
    parent = self.__parent__

    if hasattr(aq_base(parent), name):
        raise MethodNotAllowed('The name %s is in use.' % name)
    if not isDavCollection(parent):
        raise Forbidden('Cannot create collection at this location.')

    ifhdr = REQUEST.get_header('If', '')
    if IWriteLock.providedBy(parent) and parent.wl_isLocked():
        if ifhdr:
            parent.dav__simpleifhandler(REQUEST, RESPONSE, col=1)
        else:
            raise Locked
    elif ifhdr:
        # There was an If header, but the parent is not locked
        raise PreconditionFailed

    # Add hook for webdav/FTP MKCOL (Collector #2254) (needed for CMF)
    # Monkey patched to not acquire MKCOL_handler() from ERP5Site
    if hasattr(aq_base(parent), 'MKCOL_handler'):
        mkcol_handler = parent.MKCOL_handler
    else:
        mkcol_handler = parent.manage_addFolder

    mkcol_handler(name)

    RESPONSE.setStatus(201)
    RESPONSE.setBody('')
    return RESPONSE

from webdav.NullResource import NullResource
NullResource.MKCOL = MKCOL
