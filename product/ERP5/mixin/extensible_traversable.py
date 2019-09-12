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

from zLOG import LOG
from Acquisition import aq_base
from Products.ERP5Type.Globals import get_request
from AccessControl import Unauthorized
from Products.ERP5Type.ExtensibleTraversable import ExtensibleTraversableMixIn
from Products.ERP5Type.Cache import getReadOnlyTransactionCache
from AccessControl import ClassSecurityInfo, getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager, setSecurityManager
from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type import Permissions
from Products.CMFCore.utils import getToolByName, _checkConditionalGET, _setCacheHeaders, _ViewEmulator
from OFS.Image import File as OFSFile
from warnings import warn
from base64 import decodestring
from Products.ERP5Type.UnrestrictedMethod import unrestricted_apply
from Products.ERP5.Document.Document import ConversionError, NotConvertedError

# XXX: these duplicate ones in ERP5.Document
_MARKER = []
EMBEDDED_FORMAT = '_embedded'

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

class DocumentExtensibleTraversableMixin(BaseExtensibleTraversableMixin):
  """
  This class provides a implementation of IExtensibleTraversable for Document classed based documents.
  """

  def getExtensibleContent(self, request, name):
    old_manager, user = self._forceIdentification(request)
    # Next get the document per name
    portal = self.getPortalObject()
    document = self.getDocumentValue(name=name, portal=portal)
    # restore original security context if there's a logged in user
    if user is not None:
      setSecurityManager(old_manager)
    if document is not None:
      document = aq_base(document.asContext(id=name, # Hide some properties to permit locating the original
                                            original_container=document.getParentValue(),
                                            original_id=document.getId(),
                                            editable_absolute_url=document.absolute_url()))
      return document.__of__(self)

    # no document found for current user, still such document may exists
    # in some cases user (like Anonymous) can not view document according to portal catalog
    # but we may ask him to login if such a document exists
    isAuthorizationForced = getattr(self, 'isAuthorizationForced', None)
    if isAuthorizationForced is not None and isAuthorizationForced():
      if unrestricted_apply(self.getDocumentValue, (name, portal)) is not None:
        # force user to login as specified in Web Section
        raise Unauthorized

class OOoDocumentExtensibleTraversableMixin(BaseExtensibleTraversableMixin):
  """
  This class provides a implementation of IExtensibleTraversable for OOoDocument classed based documents.
  """

  def getExtensibleContent(self, request, name):
    # Be sure that html conversion is done,
    # as it is required to extract extensible content
    old_manager, user = self._forceIdentification(request)
    web_cache_kw = {'name': name,
                    'format': EMBEDDED_FORMAT}
    try:
      self._convert(format='html')
      view = _ViewEmulator().__of__(self)
      # If we have a conditional get, set status 304 and return
      # no content
      if _checkConditionalGET(view, web_cache_kw):
        return ''
      # call caching policy manager.
      _setCacheHeaders(view, web_cache_kw)
      mime, data = self.getConversion(format=EMBEDDED_FORMAT, filename=name)
      document = OFSFile(name, name, data, content_type=mime).__of__(self.aq_parent)
    except (NotConvertedError, ConversionError, KeyError):
      document = DocumentExtensibleTraversableMixin.getExtensibleContent(self, request, name)
    # restore original security context if there's a logged in user
    if user is not None:
      setSecurityManager(old_manager)
    return document
