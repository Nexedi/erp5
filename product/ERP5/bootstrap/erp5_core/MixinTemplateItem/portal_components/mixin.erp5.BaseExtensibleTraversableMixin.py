# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Ivan Tyagov <ivan@nexedi.com>
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

from warnings import warn
import six
if six.PY2:
  from base64 import decodestring as decodebytes
else:
  from base64 import decodebytes

from zLOG import LOG, WARNING
from AccessControl import ClassSecurityInfo, getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from Products.CMFCore.utils import getToolByName

from erp5.component.mixin.ExtensibleTraversableMixin import ExtensibleTraversableMixin
from Products.ERP5Type.Cache import getReadOnlyTransactionCache
from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type import Permissions
from Products.ERP5Type.Globals import get_request
from Products.ERP5Type.Utils import str2bytes, bytes2str

# XXX: these duplicate ones in ERP5.Document
_MARKER = []

class BaseExtensibleTraversableMixin(ExtensibleTraversableMixin):
  """
  This class provides a generic base mixin implementation of IExtensibleTraversable.

  Provides access to documents through their permanent URL.
  This class shoulf be used as a base mixin class using which can be used create
  "extensible" mixin classes.
  """

  def _getExtensibleContent(self, request, name):
    """
    Legacy API
    """
    warn("_getExtensibleContent() function is deprecated. Use getExtensibleContent() instead.", \
          DeprecationWarning, stacklevel=2)
    return self.getExtensibleContent(request, name)

  # Declarative security
  security = ClassSecurityInfo()

  def _forceIdentification(self, request):
    # force identification (usable for extensible content)
    # This is normally called from __bobo_traverse__ during publication.
    # Publication works in two phases (for what matters here):
    # - phase 1: traverse the entire path (request URL path)
    # - phase 2: locate a user folder and find a user allowed to access
    #   published document
    # This does not work for extensible traversable: here, we must look the
    # document up, typically using catalog, and we need to have an
    # authenticated user to do so.
    # Because we do not expect to have multiple layers of user_folders (only
    # one at the portal and one at zope root), and we are below both, we can
    # already reliably look for the user up, authenticating the request and
    # setting up a reasonable security context to use in catalog lookup
    # (or executing other restricted code).
    # XXX: this is certainly not the most elegant way of doing so.
    old_manager = getSecurityManager()
    cache = getReadOnlyTransactionCache()
    if cache is None:
      cache = {}
    key = ('__bobo_traverse__', self, 'user')
    try:
      user = cache[key]
    except KeyError:
      old_user = old_manager.getUser()
      user = None # By default, do nothing
      if old_user is None or old_user.getUserName() == 'Anonymous User':
        try:
          auth = request._auth
        except AttributeError:
          # This kind of error happens with unrestrictedTraverse,
          # because the request object is a fake, and it is just
          # a dict object. Nothing can be done with such an object.
          user = None
        else:
          need_published = 'PUBLISHED' not in request.other
          try:
            if need_published:
              # request['PUBLISHED'] is required by validate
              request['PUBLISHED'] = self
            portal = self.getPortalObject()
            # XXX: this is a simplification of the user validation logic from ZPublisher
            # - only two specific locations are checked for user folder existence
            # - user folder name is hardcoded (instead of going though __allow_groups__)
            # - no request.role handling
            for user_folder_parent in (
              portal,
              portal.aq_parent,
            ):
              user = user_folder_parent.acl_users.validate(request, auth)
              if user is not None:
                if user.getUserName() == 'Anonymous User':
                  # If the user which is connected is anonymous, do not try to change SecurityManager
                  user = None
                  continue
                break
          except Exception:
            LOG("ERP5 WARNING", WARNING,
                "Failed to retrieve user in __bobo_traverse__ of WebSection %s" % self.getPath(),
                error=True)
            user = None
          finally:
            if need_published:
              del request.other['PUBLISHED']
      cache[key] = user

    if user is None:
      old_manager = None
    else:
      # We need to perform identification
      newSecurityManager(get_request(), user)

    return old_manager, user

  security.declareProtected(Permissions.View, 'getDocumentValue')
  def getDocumentValue(self, name=None, portal=None, **kw):
    """
      Return the default document with the given
      name. The name parameter may represent anything
      such as a document reference, an identifier,
      etc.

      If name is not provided, the method defaults
      to returning the default document by calling
      getDefaultDocumentValue.

      kw parameters can be useful to filter content
      (ex. force a given validation state)

      This method must be implemented through a
      portal type dependent script:
        WebSection_getDocumentValue
    """
    if name is None:
      return self.getDefaultDocumentValue()

    method = self._getTypeBasedMethod('getDocumentValue',
              fallback_script_id='WebSection_getDocumentValue')

    document = method(name, portal=portal, **kw)
    if document is not None:
      return document.__of__(self)

InitializeClass(BaseExtensibleTraversableMixin)
