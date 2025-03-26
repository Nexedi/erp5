##############################################################################
#
# Copyright (c) 2025 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import json
import logging
import random
import string

from AccessControl import ClassSecurityInfo
from AccessControl.SecurityManagement import noSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from zope.component import queryMultiAdapter
from zope.publisher.browser import BrowserView
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces.browser import IBrowserPublisher
from ZPublisher.BaseRequest import DefaultPublishTraverse
from ZPublisher.interfaces import UseTraversalDefault
import webdav.Resource
import webdav.NullResource
from webdav.common import absattr
import zope.component
import zope.interface
from zope.datetime import rfc1123_date
from zExceptions import Unauthorized, MethodNotAllowed

from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.XMLObject import XMLObject
from erp5.component.mixin.EncryptedPasswordMixin import EncryptedPasswordMixin

logger = logging.getLogger(__name__)


def random_password():
  return ''.join(
    random.SystemRandom().sample(string.ascii_letters + string.digits, 20))


class SuperProductivityBrowserView(BrowserView):
  """Minimal web dav view
  """
  def __call__(self, *args, **kw):
    auth = self.request._authUserPW()
    request_method = self.request.method.upper()
    response = self.request.response
    # TODO: configure option to configure the origin
    response.setHeader('Access-Control-Allow-Origin', '*')
    response.setHeader(
      'Access-Control-Allow-Methods',
      'PROPFIND,GET, POST, PUT, DELETE, OPTIONS')
    response.setHeader(
      'Access-Control-Allow-Headers', 'Content-Type, Authorization, Depth')
    response.setHeader('Access-Control-Allow-Credentials', 'true')

    if request_method == 'OPTIONS':
      response.setBody(b'', lock=True)
      response.setStatus(204, lock=True)
      return

    if not auth:
      raise Unauthorized()

    wrapper = self.context
    context = wrapper.context
    user_id, password = auth

    # minimal authentication so that we don't have to provide an actual password in super productivity
    # sync settings
    if not context.checkPassword(password):
      logger.info('Wrong password for %s', user_id)
      raise Unauthorized()

    user = context.getWrappedOwner()
    logger.info('Authenticated %s for %s', user, user_id)
    try:
      newSecurityManager(self.request, user)
      portal = context.getPortalObject()
      web_page_module = portal.web_page_module
      # TODO: option for reference pattern ?
      document_reference = 'superproductivity-%s/%s' % (
        wrapper.__parent__.name,
        wrapper.name,
      )
      doc = next(
        (
          b.getObject() for b in portal.portal_catalog.getDocumentValueList(
            reference=document_reference, )), None)
      if doc is None:
        doc = web_page_module.newContent(
          portal_type='Web Page',
          content_type='text/plain',
          reference=document_reference,
          # publication_section=...  # TODO options for publication_section / classification so that the document remain personal
        )
        doc.shareAlive()

      if request_method in ('GET', 'HEAD'):
        response.setHeader('Content-Type', 'application/json')
        response.setHeader('Content-Length', absattr(doc.getSize()))
        response.setHeader(
          'Last-Modified', rfc1123_date(doc.getModificationDate()))
        if request_method == 'HEAD':
          return
        return bytes(doc.getData() or b'')

      if request_method == 'PUT':
        data = json.loads(self.request['BODY'])
        doc.setData(json.dumps(data, indent=True))
        response.setStatus(200, lock=True)
        return

      raise MethodNotAllowed()
    finally:
      noSecurityManager()


@zope.interface.implementer(IPublishTraverse, IBrowserPublisher)
class SuperProductivitySyncWrapper(object):
  """Wrapper for traversal, we traverse twice, one for the folder, one for the document,
  MAIN.json or ARCHIVE.json 
  """
  __roles__ = ['Anonymous']

  def __init__(self, context, request, name):
    self.context = context
    self.request = request
    self.name = name

    # disable redirection to login page
    def unauthorized():
      raise Unauthorized()

    request.response.unauthorized = unauthorized

  def __getattr__(self, name):
    if name[0] == '_' or name[:3] == 'aq_':
      raise AttributeError(name)
    wrapper = SuperProductivitySyncWrapper(
      self.context,
      self.request,
      name,
    )
    wrapper.__parent__ = self
    return wrapper

  def __getitem__(self, name):
    try:
      return getattr(self, name)
    except AttributeError:
      raise KeyError(name)

  def publishTraverse(self, request, name):
    return getattr(self, name)

  def browserDefault(self, request):
    return SuperProductivityBrowserView(self, request), ()


@zope.interface.implementer(IPublishTraverse)
class SuperProductivitySync(XMLObject, EncryptedPasswordMixin):
  """
    Usage:
    1. create "Super Productivity Sync" in portal_web_services, the owner of this document will be the owner of the Web Pages
      used for sync storage. Change the ID to something meaningfull, such as super_prod_sync
    2. view https://erp5/portal_web_services/super_prod_sync/initializePassword this will give you the password to use for
      synchronization.
    3. open https://github.com/johannesjo/super-productivity , the web app https://app.super-productivity.com/#/config works fine
    4. configure synchronization with:
      * Base Url: https://erp5/portal_web_services/super_prod_sync
      * Username: anything, this is not important
      * Passsword: the secret from step2

  """

  # CMF Type Definition
  meta_type = 'Super Productivity Sync'
  portal_type = 'Super Productivity Sync'  # TODO: this name is not good, maybe "Super Productivity WebDAV Synchronization Service" ?

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Default Properties
  property_sheets = (
    PropertySheet.Base,
    PropertySheet.XMLObject,
    PropertySheet.CategoryCore,
    PropertySheet.DublinCore,
  )

  def publishTraverse(self, request, name):
    method = request.method.upper()
    if method in ('PUT', 'DELETE'):
      # don't use default traversal for PUT and DELETE methods, because they are
      # handled as WebDAV before the hooks are called.
      return SuperProductivitySyncWrapper(self, request, name)
    adapter = DefaultPublishTraverse(self, request)

    obj = None
    try:
      obj = adapter.publishTraverse(request, name)
    except (KeyError, AttributeError):
      view = queryMultiAdapter((self, request), name=name)
      if view is not None:
        return view
    if obj is None or isinstance(obj, webdav.NullResource.NullResource):
      return SuperProductivitySyncWrapper(self, request, name)
    return obj

  def __bobo_traverse__(self, request, name):
    raise UseTraversalDefault

  @security.protected(Permissions.AccessContentsInformation)
  def initializePassword(self):
    """Initialize a password to use for synchronization
    """
    password = random_password()
    self._forceSetPassword(password)
    return password
