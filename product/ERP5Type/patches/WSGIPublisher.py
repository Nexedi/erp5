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
import logging

from six import binary_type
from six import PY3
from six import reraise
from six import text_type
from six.moves._thread import allocate_lock

import transaction
import zExceptions
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from Acquisition import aq_acquire
from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.ERP5Type.Timeout import wrap_call_object
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
from Zope2.App.startup import validated_hook
from ZPublisher import pubevents, Retry
from ZPublisher.HTTPRequest import HTTPRequest
from ZPublisher.HTTPResponse import HTTPResponse
from ZPublisher.Iterators import IUnboundStreamIterator
from ZPublisher.mapply import mapply
from ZPublisher.WSGIPublisher import call_object as call_object_orig
from ZPublisher.WSGIPublisher import missing_name, WSGIResponse


if sys.version_info >= (3, ):
    _FILE_TYPES = (IOBase, )
else:
    _FILE_TYPES = (IOBase, file)  # NOQA

_DEFAULT_DEBUG_MODE = False
_DEFAULT_REALM = None
_MODULE_LOCK = allocate_lock()
_MODULES = {}
call_object = wrap_call_object(call_object_orig)


AC_LOGGER = logging.getLogger('event.AccessControl')

if 1: # upstream moved WSGIResponse to HTTPResponse.py

    def finalize(self):
        headers = self.headers
        # According to PEP 333, WSGI applications and middleware are forbidden
        # from using HTTP/1.1 "hop-by-hop" features or headers.
        headers.pop('Connection', None)

        if 'content-length' in headers:
            # There's a bug in 'App.ImageFile.index_html': when it returns a 304
            # status code, 'Content-Length' is equal to a nonzero value.
            if self.status == 304:
                del headers['content-length']
        # set 204 (no content) status if 200 and response is empty and not
        # streaming
        elif ('content-type' not in headers and self.status == 200
              and not self._streaming):
            self.status = 204

        return '%s %s' % (self.status, self.errmsg), self.listHeaders()

    WSGIResponse.finalize = finalize

    class Success(Exception):
        """
        """
    zExceptions.Success = Success

    def write(self, data):
        raise AttributeError(
            "This method must not be used anymore and will be removed in the"
            " future. Either return a stream iterator or raise"
            " zExceptions.Success")

    HTTPResponse.write = write
    WSGIResponse.write = write


# From ZPublisher.utils
def recordMetaData(object, request):
    if hasattr(object, 'getPhysicalPath'):
        path = '/'.join(object.getPhysicalPath())
    else:
        # Try hard to get the physical path of the object,
        # but there are many circumstances where that's not possible.
        to_append = ()

        if hasattr(object, '__self__') and hasattr(object, '__name__'):
            # object is a Python method.
            to_append = (object.__name__,)
            object = object.__self__

        while object is not None and not hasattr(object, 'getPhysicalPath'):
            if getattr(object, '__name__', None) is None:
                object = None
                break
            to_append = (object.__name__,) + to_append
            object = aq_parent(aq_inner(object))

        if object is not None:
            path = '/'.join(object.getPhysicalPath() + to_append)
        else:
            # As Jim would say, "Waaaaaaaa!"
            # This may cause problems with virtual hosts
            # since the physical path is different from the path
            # used to retrieve the object.
            path = request.get('PATH_INFO')

    T = transaction.get()
    T.note(safe_unicode(path))
    auth_user = request.get('AUTHENTICATED_USER', None)
    if auth_user:
        auth_folder = aq_parent(auth_user)
        if auth_folder is None:
            AC_LOGGER.warning(
                'A user object of type %s has no aq_parent.',
                type(auth_user))
            auth_path = request.get('AUTHENTICATION_PATH')
        else:
            auth_path = '/'.join(auth_folder.getPhysicalPath()[1:-1])
        user_id = auth_user.getId()
        user_id = safe_unicode(user_id) if user_id else u'None'
        T.setUser(user_id, safe_unicode(auth_path))


def safe_unicode(value):
    if isinstance(value, text_type):
        return value
    elif isinstance(value, binary_type):
        try:
            value = text_type(value, 'utf-8')
        except UnicodeDecodeError:
            value = value.decode('utf-8', 'replace')
    return value


def dont_publish_class(klass, request):
    request.response.forbiddenError("class %s" % klass.__name__)


def get_module_info(module_name='Zope2'):
    global _MODULES
    info = _MODULES.get(module_name)
    if info is not None:
        return info

    with _MODULE_LOCK:
        module = __import__(module_name)
        app = getattr(module, 'bobo_application', module)
        realm = _DEFAULT_REALM if _DEFAULT_REALM is not None else module_name
        error_hook = getattr(module,'zpublisher_exception_hook', None)
        _MODULES[module_name] = info = (app, realm, _DEFAULT_DEBUG_MODE, error_hook)
    return info


def _exc_view_created_response(exc, request, response):
    view = queryMultiAdapter((exc, request), name=u'index.html')
    parents = request.get('PARENTS')

    if view is None and parents:
        # Try a fallback based on the old standard_error_message
        # DTML Method in the ZODB
        view = queryMultiAdapter((exc, request),
                                 name=u'standard_error_message')
        root_parent = parents[0]
        try:
            aq_acquire(root_parent, 'standard_error_message')
        except (AttributeError, KeyError):
            view = None

    if view is not None:
        # Wrap the view in the context in which the exception happened.
        if parents:
            view.__parent__ = parents[0]

        # Set status and headers from the exception on the response,
        # which would usually happen while calling the exception
        # with the (environ, start_response) WSGI tuple.
        response.setStatus(exc.__class__)
        if hasattr(exc, 'headers'):
            for key, value in exc.headers.items():
                response.setHeader(key, value)

        # Set the response body to the result of calling the view.
        response.setBody(view())
        return True

    return False


@contextmanager
def transaction_pubevents(request, response, err_hook, tm=transaction.manager):
    try:
        setDefaultSkin(request)
        newInteraction()
        tm.begin()
        notify(pubevents.PubStart(request))

        yield

        notify(pubevents.PubBeforeCommit(request))
        if tm.isDoomed():
            tm.abort()
        else:
            tm.commit()
        notify(pubevents.PubSuccess(request))
    except Exception as exc:
        # Normalize HTTP exceptions
        # (For example turn zope.publisher NotFound into zExceptions NotFound)
        exc_type, _ = upgradeException(exc.__class__, None)
        if not isinstance(exc, exc_type):
            exc = exc_type(str(exc))

        # Create new exc_info with the upgraded exception.
        exc_info = (exc_type, exc, sys.exc_info()[2])

        try:
            # Raise exception from app if handle-errors is False
            # (set by zope.testbrowser in some cases)
            if request.environ.get('x-wsgiorg.throw_errors', False):
                reraise(*exc_info)

            if err_hook:
                parents = request['PARENTS']
                if parents:
                    parents = parents[0]
                retry = False
                try:
                    try:
                        r = err_hook(parents, request, *exc_info)
                        assert r is response
                        exc_view_created = True
                    except Retry:
                        if request.supports_retry():
                            retry = True
                        else:
                            r = err_hook(parents, request, *sys.exc_info())
                            assert r is response
                            exc_view_created = True
                except (Redirect, Unauthorized):
                    response.exception()
                    exc_view_created = True
                except BaseException as e:
                    if e is not exc:
                        raise
                    exc_view_created = False
            else:
                # Handle exception view
                exc_view_created = _exc_view_created_response(
                    exc, request, response)

                if isinstance(exc, Unauthorized):
                    # _unauthorized modifies the response in-place. If this hook
                    # is used, an exception view for Unauthorized has to merge
                    # the state of the response and the exception instance.
                    exc.setRealm(response.realm)
                    response._unauthorized()
                    response.setStatus(exc.getStatus())

                retry = isinstance(exc, TransientError) and request.supports_retry()

            notify(pubevents.PubBeforeAbort(request, exc_info, retry))
            tm.abort()
            notify(pubevents.PubFailure(request, exc_info, retry))

            if retry:
                reraise(*exc_info)

            if not (exc_view_created or isinstance(exc, Unauthorized)):
                reraise(*exc_info)
        finally:
            # Avoid traceback / exception reference cycle.
            del exc, exc_info
    finally:
        endInteraction()


def publish(request, module_info):
    obj, realm, debug_mode = module_info

    request.processInputs()
    response = request.response

    if debug_mode:
        response.debug_mode = debug_mode

    if realm and not request.get('REMOTE_USER', None):
        response.realm = realm

    noSecurityManager()

    # Get the path list.
    # According to RFC1738 a trailing space in the path is valid.
    path = request.get('PATH_INFO')
    request['PARENTS'] = [obj]

    obj = request.traverse(path, validated_hook=validated_hook)
    notify(pubevents.PubAfterTraversal(request))
    recordMetaData(obj, request)

    try:
        result = mapply(obj,
                        request.args,
                        request,
                        call_object,
                        1,
                        missing_name,
                        dont_publish_class,
                        request,
                        bind=1)
    except Success as exc:
        result, = exc.args or ('',)
    if result is not response:
        response.setBody(result)

    return response


@contextmanager
def load_app(module_info):
    app_wrapper, realm, debug_mode = module_info
    # Loads the 'OFS.Application' from ZODB.
    app = app_wrapper()

    try:
        yield (app, realm, debug_mode)
    finally:
        if transaction.manager._txn is not None:
            # Only abort a transaction, if one exists. Otherwise the
            # abort creates a new transaction just to abort it.
            transaction.abort()
        app._p_jar.close()


def publish_module(environ, start_response,
                   _publish=publish,  # only for testing
                   _response=None,
                   _response_factory=WSGIResponse,
                   _request=None,
                   _request_factory=HTTPRequest,
                   _module_name='Zope2'):
    module_info = get_module_info(_module_name)
    module_info, err_hook = module_info[:3], module_info[3]
    result = ()

    path_info = environ.get('PATH_INFO')
    if path_info and PY3:
        # The WSGI server automatically treats the PATH_INFO as latin-1 encoded
        # bytestrings. Typically this is a false assumption as the browser
        # delivers utf-8 encoded PATH_INFO. We, therefore, need to encode it
        # again with latin-1 to get a utf-8 encoded bytestring.
        path_info = path_info.encode('latin-1')
        # But in Python 3 we need text here, so we decode the bytestring.
        path_info = path_info.decode('utf-8')

        environ['PATH_INFO'] = path_info
    if 1:
        new_response = (
            _response
            if _response is not None
            else _response_factory(stdout=None, stderr=None))
        new_response._http_version = environ['SERVER_PROTOCOL'].split('/')[1]
        new_response._server_version = environ.get('SERVER_SOFTWARE')

        new_request = (
            _request
            if _request is not None
            else _request_factory(environ['wsgi.input'],
                                  environ,
                                  new_response))

        for i in range(getattr(new_request, 'retry_max_count', 3) + 1):
            request = new_request
            response = new_response
            setRequest(request)
            try:
                with load_app(module_info) as new_mod_info:
                    with transaction_pubevents(request, response, err_hook):
                        response = _publish(request, new_mod_info)
                break
            except TransientError:
                if request.supports_retry():
                    new_request = request.retry()
                    new_response = new_request.response
                else:
                    raise
            finally:
                request.close()
                clearRequest()

        # Start the WSGI server response
        status, headers = response.finalize()
        start_response(status, headers)

        if isinstance(response.body, _FILE_TYPES) or \
           IUnboundStreamIterator.providedBy(response.body):
            result = response.body
        else:
            result = response.body,

        for func in response.after_list:
            func()

    # Return the result body iterable.
    return result


sys.modules['ZPublisher.WSGIPublisher'] = sys.modules[__name__]
