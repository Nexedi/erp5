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
from AccessControl.SecurityManagement import getSecurityManager, newSecurityManager, setSecurityManager
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type import Permissions, PropertySheet,\
                              Constraint, Interface, Cache
from Products.ERP5.Document.Domain import Domain
#from Products.ERP5.Document.WebSite import WebSite
from Acquisition import ImplicitAcquisitionWrapper, aq_base, aq_inner
from Products.ERP5Type.Base import TempBase
from Globals import get_request

from zLOG import LOG

from Products.ERP5.Document.WebSite import reserved_name_dict, reserved_name_dict_init
from Products.ERP5.Document.WebSite import CACHE_KEY, WEBSITE_USER, WEBSECTION_KEY, DOCUMENT_NAME_KEY


class WebSection(Domain):
    """
      A Web Section is a Domain with an extended API intended to
      support the creation of Web front ends to ERP5 contents.
    """
    # CMF Type Definition
    meta_type = 'ERP5 Web Section'
    portal_type = 'Web Section'
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
                      , PropertySheet.SortIndex
                      )

    # Draft - this is being worked on
    # Due to some issues in acquisition, the implementation  of getWebSectionValue
    # through acquisition by containment does not work for URLs
    # such as web_site_module/a/b/c/web_page_module/d
    # getWebSectionValue will return web_site_module/a/b instead
    # of web_site_module/a/b/c
    #security.declareProtected(Permissions.AccessContentsInformation, 'getWebSectionValue')
    #def getWebSectionValue(self):
      #"""
        #Returns the current web section (ie. self) though containment acquisition
      #"""
      #return self

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
      if not request.has_key(WEBSECTION_KEY):
        request[WEBSECTION_KEY] = self.getPhysicalPath()
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
        request[DOCUMENT_NAME_KEY] = name
        document = aq_base(document.asContext(id=name, # Hide some properties to permit location the original
                                              original_container=document.getParentValue(),
                                              original_id=document.getId(),
                                              editable_absolute_url=document.absolute_url()))
      return document

    security.declareProtected(Permissions.AccessContentsInformation, 'getWebSiteValue')
    def getWebSiteValue(self):
      return self.getParentValue().getWebSiteValue()
