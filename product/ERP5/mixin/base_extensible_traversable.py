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
from base64 import decodestring

from zLOG import LOG
from AccessControl import ClassSecurityInfo, getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager, setSecurityManager
from Products.CMFCore.utils import getToolByName

from Products.ERP5Type.ExtensibleTraversable import ExtensibleTraversableMixIn
from Products.ERP5Type.Cache import getReadOnlyTransactionCache
from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type import Permissions
from Products.ERP5Type.Globals import get_request

# XXX: these duplicate ones in ERP5.Document
_MARKER = []

class BaseExtensibleTraversableMixin(ExtensibleTraversableMixIn):
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
    cache = getReadOnlyTransactionCache()
    if cache is not None:
      key = ('__bobo_traverse__', self, 'user')
      try:
        user = cache[key]
      except KeyError:
        user = _MARKER
    else:
      user = _MARKER
    old_user = getSecurityManager().getUser()
    if user is _MARKER:
      user = None # By default, do nothing
      if old_user is None or old_user.getUserName() == 'Anonymous User':
        portal_membership = getToolByName(self.getPortalObject(),
                                          'portal_membership')
        if portal_membership is not None:
          try:
            if request.get('PUBLISHED', _MARKER) is _MARKER:
              # request['PUBLISHED'] is required by validate
              request['PUBLISHED'] = self
              has_published = False
            else:
              has_published = True
            try:
              name = None
              acl_users = self.getPortalObject().acl_users
              user_list = acl_users._extractUserIds(request, acl_users.plugins)
              if len(user_list) > 0:
                name = user_list[0][0]
              else:
                auth = request._auth
                # this logic is copied from identify() in
                # AccessControl.User.BasicUserFolder.
                if auth and auth.lower().startswith('basic '):
                  name = decodestring(auth.split(' ')[-1]).split(':', 1)[0]
              if name is not None:
                user = portal_membership._huntUser(name, self)
              else:
                user = None
            except AttributeError:
              # This kind of error happens with unrestrictedTraverse,
              # because the request object is a fake, and it is just
              # a dict object.
              user = None
            if not has_published:
              try:
                del request.other['PUBLISHED']
              except AttributeError:
                # The same here as above. unrestrictedTraverse provides
                # just a plain dict, so request.other does not exist.
                del request['PUBLISHED']
          except:
            LOG("ERP5 WARNING",0,
                "Failed to retrieve user in __bobo_traverse__ of WebSection %s" % self.getPath(),
                error=True)
            user = None
      if user is not None and user.getUserName() == 'Anonymous User':
        user = None # If the user which is connected is anonymous,
                    # do not try to change SecurityManager
      if cache is not None:
        cache[key] = user

    old_manager = None
    if user is not None:
      # We need to perform identification
      old_manager = getSecurityManager()
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
