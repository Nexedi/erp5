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

from Acquisition import ImplicitAcquisitionWrapper, aq_base, aq_inner

from AccessControl import ClassSecurityInfo
from AccessControl.User import emergency_user
from AccessControl.SecurityManagement import getSecurityManager, newSecurityManager, setSecurityManager

from Products.CMFCore.utils import getToolByName
from Products.ERP5.Document.Domain import Domain
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface, Cache
from Products.ERP5Type.Base import TempBase

from Products.CMFCore.utils import UniqueObject, _checkPermission, _getAuthenticatedUser

from Globals import get_request

from Persistence import Persistent

from ZPublisher import BeforeTraverse

from zLOG import LOG

WEBSITE_KEY = 'web_site_value'
WEBSECTION_KEY = 'web_section_value'
WEBSITE_USER = 'web_site_user'

class WebSiteTraversalHook(Persistent):
  """
    This is used by WebSite to rewrite URLs in such way
    that once a user gets into a Web Site object, all
    documents referenced by the web site are accessed
    through the web site rather than directly.
    We inherit for persistent, so that pickle mechanism ignores _v_request .
  """

  def _physicalPathToVirtualPath(self, path):
    """
      Remove the path to the VirtualRoot from a physical path
      and add the path to the WebSite if any
    """
    if type(path) is type(''):
      path = path.split( '/')

    # Every Web Section acts as a mini site though layout for document editing is the root layout
    #website_path = self._v_request.get(WEBSECTION_KEY, self._v_request.get(WEBSITE_KEY, None))
    # Only consider Web Site for absolute_url
    website_path = self._v_request.get(WEBSITE_KEY, None) 
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
        if i >= path_len:
          break
        if path[i] == name:
          common_index = i
        i += 1
      # Insert the web site path after the common part of the path
      if path_len > common_index + 1:
        path = website_path + path[common_index + 1:]
    rpp = self._v_request.other.get('VirtualRootPhysicalPath', ('', ))
    i = 0
    for name in rpp[:len(path)]:
      if path[i] == name:
        i = i + 1
      else:
        break
    #if self._v_request.has_key(DOCUMENT_NAME_KEY):
    #  # Replace the last id of the path with the name which
    #  # was used to lookup the document
    #  path = path[:-1] + (self._v_request[DOCUMENT_NAME_KEY],)
    return path[i:]

  def __call__(self, container, request):
    """
      Each time we are traversed, we patch the request instance with our
      rewritted version of physicalPathToVirtualPath
    """
    self._v_request = request
    request.physicalPathToVirtualPath = self._physicalPathToVirtualPath



Domain_getattr = Domain.inheritedAttribute('__getattr__')

# Use a request key to store access attributes and prevent infinite recursion
CACHE_KEY = 'web_site_aq_cache'
DOCUMENT_NAME_KEY = 'web_site_document_name'
reserved_name_dict = { 'getApplicableLayout' : 1,
                       'getLayout' : 1,
                       'Localizer' : 1,
                       'field_render' : 1,
                       'getListItemUrl' : 1,
                       'getLocalPropertyManager' : 1,
                       'getOrderedGlobalActionList' : 1,
                       'allow_discussion' : 1,
                       'im_func' : 1,
                       'id' : 1,
                       'method_id' : 1,
                       'role_map' : 1,  }
reserved_name_dict_init = 0

class WebSite(Domain):
    """
      A Web Site root class. This class is used by ERP5 Commerce
      to define the root of an eCommerce site.

      The main idea of the WebSite class is to provide access to
      documents by leveraging aq_dynamic with a user definable
      script: WebSite_getDocumentValue

      This script allows for implementing simple or
      complex document lookup policies:

      - access to documents by a unique reference (ex. as
        in a Wiki)

      - access to published documents only (ex.
        publication_state == 'published')

      - access to most relevant document (ex. latest
        version, applicable language)

      Changing this script allows for configuring completely
      the behaviour of a web site and tweaking document
      lookup policies to fit specific needs.

      WARNING:
        - Z Catalog Search permission must be set for Anonymous
          (XXX is this still true ?)

      TODO:
        - accelerate document lookup by caching acceptable keys
          (XXX is this still true ?)

        - fix missing REQUEST information in aq_dynamic documents
          (XXX is this still true ?)
    """
    # CMF Type Definition
    meta_type       = 'ERP5 Web Site'
    portal_type     = 'Web Site'
    isPortalContent = 1
    isRADContent    = 1

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
        the WebSite_getDocumentValue script
      """
      global reserved_name_dict_init
      global reserved_name_dict
      request = self.REQUEST
      # Register current web site physical path for later URL generation
      if not request.has_key(WEBSITE_KEY):
        request[WEBSITE_KEY] = self.getPhysicalPath()
        # Normalize web parameter in the request
        # Fix common user mistake and transform '1' string to boolean
        for web_param in ['ignore_layout', 'editable_mode']:
          if hasattr(request, web_param):
            if getattr(request, web_param, None) in ('1', 1, True):
              request.set(web_param, True)
            else:
              request.set(web_param, False)
      # First let us call the super method
      dynamic = Domain._aq_dynamic(self, name)
      if dynamic is not None:
        return dynamic
      # Do some optimisation here for names which can not be names of documents
      if  reserved_name_dict.has_key(name) \
          or name.startswith('_') or name.startswith('portal_')\
          or name.startswith('aq_') or name.startswith('selection_') \
          or name.startswith('sort-') or name.startswith('WebSite_') \
          or name.startswith('WebSection_') or name.startswith('Base_'):
        return None
      if not reserved_name_dict_init:
        # Feed reserved_name_dict_init with skin names
        portal = self.getPortalObject()
        for skin_folder in portal.portal_skins.objectValues():
          for id in skin_folder.objectIds():
            reserved_name_dict[id] = 1
        for id in portal.objectIds():
          reserved_name_dict[id] = 1
        reserved_name_dict_init = 1
      #LOG('aq_dynamic name',0, name)
      if not request.has_key(CACHE_KEY):
        request[CACHE_KEY] = {}
      elif request[CACHE_KEY].has_key(name):
        return request[CACHE_KEY][name]
      try:
        portal = self.getPortalObject()
        # Use the webmaster identity to find documents
        if request[CACHE_KEY].has_key(WEBSITE_USER):
          user = request[CACHE_KEY][WEBSITE_USER] # Retrieve user from request cache
        else:
          user = portal.acl_users.getUserById(self.getWebmaster())
          request[CACHE_KEY][WEBSITE_USER] = user # Cache user per request
        if user is not None:
          old_manager = getSecurityManager()
          newSecurityManager(get_request(), user)
        document = self.WebSite_getDocumentValue(name=name, portal=portal)
        request[CACHE_KEY][name] = document
        if user is not None:
          setSecurityManager(old_manager)
      except:
        # Cleanup non recursion dict in case of exception
        if request[CACHE_KEY].has_key(name):
          del request[CACHE_KEY][name]
        raise
      if document is not None:
        document = aq_base(document.asContext(id=name, # Hide some properties to permit location the original
                                              original_container=document.getParentValue(),
                                              original_id=document.getId(),
                                              editable_absolute_url=document.absolute_url()))
      return document

    # Draft - this is being worked on
    security.declareProtected(Permissions.AccessContentsInformation, 'getWebSiteValue')
    def getWebSiteValue(self):
        """
          Returns the current web site (ie. self) though containment acquisition
        """
        return self

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
        BeforeTraverse.registerBeforeTraverse(item, WebSiteTraversalHook(), handle)
      Domain.manage_afterAdd(self, item, container)

    # Experimental methods 
    def findUrlList(self, document):
        """
          Return a list of URLs which exist in the site for
          a given document
        """
        pass