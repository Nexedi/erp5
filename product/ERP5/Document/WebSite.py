##############################################################################
#
# Copyright (c) 2002-2006 Nexedi SARL and Contributors. All Rights Reserved.
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

from AccessControl import ClassSecurityInfo
from AccessControl import getSecurityManager
from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type import Permissions, PropertySheet,\
                              Constraint, Interface, Cache
from Products.ERP5.Document.Domain import Domain
from Acquisition import ImplicitAcquisitionWrapper, aq_base, aq_inner
from Products.ERP5Type.Base import TempBase
from Globals import get_request
from Persistence import Persistent
from Products.CMFCore.utils import UniqueObject, _checkPermission,\
                                   _getAuthenticatedUser
from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.User import emergency_user
from AccessControl.SecurityManagement import newSecurityManager,\
                                             setSecurityManager
from ZPublisher import BeforeTraverse

from zLOG import LOG

website_key = 'web_site_value'
class WebSiteTraversalHook(Persistent):
  """This is used by WebSite to rewrite URLs in such way
  that once a user gets into a Web Site object, all
  documents referenced by the web site are accessed
  through the web site rather than directly.
  We inherit for persistent, so that pickle mechanism ignores _v_request
  """

  def _physicalPathToVirtualPath(self, path):
    """
      Remove the path to the VirtualRoot from a physical path
      and add the path to the WebSite is any
    """
    if type(path) is type(''):
      path = path.split( '/')

    website_path = self._v_request.get(website_key, None)
    if website_path:
      website_path = tuple(website_path)    # Make sure all path are tuples
      path = tuple(path)                    # Make sure all path are tuples
      # Search for the common part index
      # XXX more testing should be added to check
      # if the URL is the kind of URL which is a Web Site
      # XXX more support required for ignore_layout
      common_index = 0
      i = 0
      path_len = len(path)
      for name in website_path:
        if i >= path_len: break
        if path[i] == name:
          common_index = i
        i += 1
      # Insert the web site path after the common part of the path
      if path_len > common_index + 1:
        path = website_path + path[common_index + 1:]

    rpp = self._v_request.other.get('VirtualRootPhysicalPath', ('',))
    i = 0
    for name in rpp[:len(path)]:
      if path[i] == name:
        i = i + 1
      else:
        break
    return path[i:]
  
  def __call__(self, container, request):
    """Each time we are traversed, we patch the request instance with our
    rewritted version of physicalPathToVirtualPath"""
    self._v_request = request
    request.physicalPathToVirtualPath = self._physicalPathToVirtualPath

Domain_getattr = Domain.inheritedAttribute('__getattr__')

# Use a request key to store access attributes and prevent infinite recursion
cache_key = 'web_site_aq_cache'

class WebSite(Domain):
    """
      A Web Site root class. This class is used by ERP5 Commerce
      to define the root of an eCommerce site.

      WARNING:
        - Z Catalog Search permission must be set for Anonymous

      TODO:
        - accelerate document lookup by caching acceptable keys
        - fix missing REQUEST information in aq_dynamic documents
    """
    # CMF Type Definition
    meta_type = 'ERP5 Web Site'
    portal_type = 'Web Site'
    isPortalContent = 1
    isRADContent = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    # Default Properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      , PropertySheet.WebSite
                      )

    def _aq_dynamic(self, name):
      """
        Try to find a suitable document based on the
        web site local naming policies as defined by
        the WebSite_getDocument script
      """
      request = self.REQUEST
      # Register current web site physical path for later URL generation
      if not request.has_key(website_key): request[website_key] = self.getPhysicalPath()
      # First let us call the super method
      dynamic = Domain._aq_dynamic(self, name)
      if dynamic is not None :
        return dynamic
      # Do some optimisation here for names which can not be names of documents
      if name.startswith('_') or name.startswith('portal_')\
          or name.startswith('aq_') or name.startswith('selection_') \
          or name.startswith('sort-') or name == 'getLayout' \
          or name == 'getListItemUrl' or name.startswith('WebSite_'):
        return None
      if not request.has_key(cache_key):
        request[cache_key] = {}
      elif request[cache_key].has_key(name):
        return request[cache_key][name]
      try:
        portal = self.getPortalObject()
        # Use the webmaster identity to find documents
        user = portal.acl_users.getUserById(self.getWebmaster())
        if user is not None:
          old_manager = getSecurityManager()
          newSecurityManager(get_request(), user)
        document = self.WebSite_getDocument(portal, name)
        request[cache_key][name] = document
        if user is not None:
          setSecurityManager(old_manager)
      except:
        # Cleanup non recursion dict in case of exception
        if request[cache_key].has_key(name):
          del request[cache_key][name]
        raise
      return document

    security.declarePrivate( 'manage_beforeDelete' )
    def manage_beforeDelete(self, item, container):
      if item is self:
        handle = self.meta_type + '/' + self.getId()
        BeforeTraverse.unregisterBeforeTraverse(item, handle)
      Domain.manage_beforeDelete(self, item, container)

    security.declarePrivate( 'manage_afterAdd' )
    def manage_afterAdd(self, item, container):
      if item is self:
        handle = self.meta_type + '/' + self.getId()
        BeforeTraverse.registerBeforeTraverse(item,
                                              WebSiteTraversalHook(),
                                              handle)
      Domain.manage_afterAdd(self, item, container)

