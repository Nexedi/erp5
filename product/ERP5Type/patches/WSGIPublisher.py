# Backport (with modified code) from Zope4

##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
""" Python Object Publisher -- Publish Python objects on web servers
"""
import sys
from contextlib import closing
from contextlib import contextmanager
from io import BytesIO
from io import IOBase
import itertools
import logging

from six import binary_type
from six import PY3
from six import reraise
from six import text_type
from six.moves._thread import allocate_lock

import transaction
from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from Acquisition import aq_acquire
from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.ERP5Type.Timeout import getPublisherDeadlineValue
from transaction.interfaces import TransientError
from zExceptions import Redirect
from zExceptions import Unauthorized
from zExceptions import upgradeException
from zope.component import queryMultiAdapter
from zope.event import notify
from zope.globalrequest import clearRequest
from zope.globalrequest import setRequest
from zope.publisher.skinnable import setDefaultSkin
from zope.security.management import endInteraction
from zope.security.management import newInteraction
from ZPublisher import pubevents
from ZPublisher.HTTPRequest import WSGIRequest
from ZPublisher.HTTPResponse import WSGIResponse
from ZPublisher.Iterators import IStreamIterator, IUnboundStreamIterator
from ZPublisher.mapply import mapply
from ZPublisher.utils import recordMetaData
from ZPublisher.WSGIPublisher import (
    _FILE_TYPES,
    _DEFAULT_DEBUG_EXCEPTIONS,
    _DEFAULT_DEBUG_MODE,
    _DEFAULT_REALM,
    _MODULE_LOCK,
    _MODULES,
    _WEBDAV_SOURCE_PORT,
    call_object,
    dont_publish_class,
    missing_name,
    validate_user,
    set_default_debug_exceptions,
    set_webdav_source_port,
    get_debug_exceptions,
    set_default_debug_mode,
    set_default_authentication_realm,
    get_module_info,
    _exc_view_created_response,
    transaction_pubevents,
    publish as _original_publish,
    load_app,
    publish_module
)


if 1: # upstream moved WSGIResponse to HTTPResponse.py

    def write(self, data):
        if not self._streaming:

            notify(pubevents.PubBeforeStreaming(self))

            self._streaming = 1
            self._locked_body = 1
            self.finalize()
            self.stdout.flush()

        self.stdout.write(data)

    WSGIResponse.write = write

    # According to PEP 333, WSGI applications and middleware are forbidden from
    # using HTTP/1.1 "hop-by-hop" features or headers. This patch prevents Zope
    # from sending 'Connection' and 'Transfer-Encoding' headers.
    def _finalize(self):

        headers = self.headers
        body = self.body

        # <patch>

        # There's a bug in 'App.ImageFile.index_html': when it returns a 304 status
        # code, 'Content-Length' is equal to a nonzero value.
        if self.status == 304:
          headers.pop('content-length', None)

        # Force the removal of "hop-by-hop" headers
        headers.pop('Connection', None)

        # </patch>

        # set 204 (no content) status if 200 and response is empty
        # and not streaming
        if ('content-type' not in headers and
            'content-length' not in headers and
            not self._streaming and self.status == 200):
            self.setStatus('nocontent')

        # add content length if not streaming
        content_length = headers.get('content-length')

        if content_length is None and not self._streaming:
            self.setHeader('content-length', len(body))

        # <patch>
        # backport from Zope 4.0b1
        # (see commit be5b14bd858da787c41a39e2533b0aabcd246fd5)
        # </patch>

        return '%s %s' % (self.status, self.errmsg), self.listHeaders()

    WSGIResponse._finalized = None

    def finalize(self):
        if not self._finalized:
            self._finalized = _finalize(self)
        return self._finalized

    WSGIResponse.finalize = finalize


def publish(request, module_info):
    with getPublisherDeadlineValue(request):
        return _original_publish(request, module_info)


sys.modules['ZPublisher.WSGIPublisher'] = sys.modules[__name__]
