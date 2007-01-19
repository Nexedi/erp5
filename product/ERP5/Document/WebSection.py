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

from zLOG import LOG, WARNING

from Products.ERP5Type.Cache import getReadOnlyTransactionCache

# Global keys used for URL generation
WEBSECTION_KEY = 'web_section_value'
WEBSITE_USER = 'web_site_user'

Domain_getattr = Domain.inheritedAttribute('__getattr__')

# We use a request key (CACHE_KEY) to store access attributes and prevent infinite recursion
# We define a couple of reserved names for which we are not
# going to try to do acquisition
CACHE_KEY = 'web_site_aq_cache'
DOCUMENT_NAME_KEY = 'web_section_document_name'
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
                       'role_map' : 1,
                       'func_defaults': 1,  }
reserved_name_dict_init = 0

class WebSection(Domain):
    """
      A Web Section is a Domain with an extended API intended to
      support the creation of Web front ends to
      server ERP5 contents through a pretty and configurable
      user interface.

      WebSection uses the following scripts for customisation:

      - WebSection_getBreadcrumbItemList

      - WebSection_getDocumentValueList

      - WebSection_getPermanentURL

      - WebSection_getDocumentValue

      - WebSection_getDefaultDocumentValue

      - WebSection_getSectionValue

      - WebSection_getWebSiteValue

      It defines the following REQUEST global variables:

      - current_web_section

      - current_web_document

      - is_web_section_default_document
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
                      , PropertySheet.WebSection
                      , PropertySheet.SortIndex
                      , PropertySheet.Predicate
                      )

    web_section_key = WEBSECTION_KEY

    def _aq_dynamic(self, name):
      """
        Try to find a suitable document based on the
        web site local naming policies as defined by
        the getDocumentValue method
      """
      global reserved_name_dict_init
      global reserved_name_dict
      request = self.REQUEST
      # Register current web site physical path for later URL generation
      if not request.has_key(self.web_section_key):
        request[self.web_section_key] = self.getPhysicalPath()
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
          or name.endswith('_getDocumentValue') \
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
          # Cache webmaster for faster lookup
          if not hasattr(aq_base(self), '_v_section_webmaster'):
            self._v_section_webmaster = self.getWebmaster()
          user = portal.acl_users.getUserById(self._v_section_webmaster)
          request[CACHE_KEY][WEBSITE_USER] = user # Cache user per request
        if user is not None:
          old_manager = getSecurityManager()
          newSecurityManager(get_request(), user)
        else:
          LOG('WebSection _aq_dynamic', WARNING, 'No user defined for %s.'
          'This will prevent accessing object through their permanent URL' % self.getWebmaster())
        #LOG('Lookup', 0, str(name))
        document = self.getDocumentValue(name=name, portal=portal)
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

    security.declareProtected(Permissions.AccessContentsInformation, 'getWebSectionValue')
    def getWebSectionValue(self):
      """
        Returns the current web section (ie. self) though containment acquisition.

        To understand the misteries of acquisition and how the rule
        containment vs. acquisition works, please look at
        XXXX (Zope web site)
      """
      return self

    # Default view display
    security.declareProtected(Permissions.View, '__call__')
    def __call__(self):
      """
        If a Web Section has a default document, we render
        the default document instead of rendering the Web Section
        itself.

        The implementation is based on the presence of specific
        variables in the REQUEST (besides editable_mode and
        ignore_layout).

        current_web_section -- defines the Web Section which is
        used to display the current document.

        current_web_document -- defines the Document (ex. Web Page)
        which is being displayed within current_web_section.

        is_web_section_default_document -- a boolean which is
        set each time we display a default document as a section.

        We use REQUEST parameters so that they are reset for every
        Web transaction and can be accessed from widgets. 
      """
      self.REQUEST.set('current_web_section', self)
      if not self.REQUEST.get('editable_mode') and not self.REQUEST.get('ignore_layout'):
        document = self.getDefaultDocumentValue()
        if document is not None:
          self.REQUEST.set('current_web_document', document)
          self.REQUEST.set('is_web_section_default_document', 1)
          return document.__of__(self)()
      return Domain.__call__(self)

    # Layout Selection API
    security.declareProtected(Permissions.AccessContentsInformation, 'getApplicableLayout')
    def getApplicableLayout(self):
      """
        The applicable layout on a section is the container layout.
      """
      return self.getContainerLayout()

    # WebSection API
    security.declareProtected(Permissions.View, 'getDocumentValue')
    def getDocumentValue(self, name=None, portal=None):
      """
        Return the default document with the given
        name. The name parameter may represent anything
        such as a document reference, an identifier,
        etc.

        If name is not provided, the method defaults
        to returning the default document by calling
        getDefaultDocumentValue.

        This method must be implemented through a
        portal type dependent script:
          WebSection_getDocumentValue
      """
      if name is None:
        return self.getDefaultDocumentValue()

      cache = getReadOnlyTransactionCache(self)
      method = None
      if cache is not None:
        key = ('getDocumentValue', self)
        try:
          method = cache[key]
        except KeyError:
          pass

      if method is None: method = self._getTypeBasedMethod('getDocumentValue',
                                        fallback_script_id='WebSection_getDocumentValue')

      if cache is not None:
        if not cache.has_key(key): cache[key] = method

      return method(name, portal=portal)

    security.declareProtected(Permissions.View, 'getDefaultDocumentValue')
    def getDefaultDocumentValue(self):
      """
        Return the default document of the current
        section.

        This method must be implemented through a
        portal type dependent script:
          WebSection_getDefaultDocumentValue
      """
      cache = getReadOnlyTransactionCache(self)
      if cache is not None:
        key = ('getDefaultDocumentValue', self)
        try:
          return cache[key]
        except KeyError:
          pass

      result = self._getTypeBasedMethod('getDefaultDocumentValue',
                     fallback_script_id='WebSection_getDefaultDocumentValue')()

      if cache is not None:
        cache[key] = result

      return result

    security.declareProtected(Permissions.View, 'getDocumentValueList')
    def getDocumentValueList(self, **kw):
      """
        Return the list of documents which belong to the
        current section. The API is designed to
        support additional parameters so that it is possible
        to group documents by reference, version, language, etc.
        or to implement filtering of documents.

        This method must be implemented through a
        portal type dependent script:
          WebSection_getDocumentValueList
      """
      cache = getReadOnlyTransactionCache(self)
      if cache is not None:
        key = ('getDocumentValueList', self) + tuple(kw.items())
        try:
          return cache[key]
        except KeyError:
          pass

      result = self._getTypeBasedMethod('getDocumentValueList',
                     fallback_script_id='WebSection_getDocumentValueList')(**kw)

      if cache is not None:
        cache[key] = result

      return result

    security.declareProtected(Permissions.View, 'getPermanentURL')
    def getPermanentURL(self, document):
      """
        Return a permanent URL of document in the context
        of the current section.

        This method must be implemented through a
        portal type dependent script:
          WebSection_getPermanentURL
      """
      cache = getReadOnlyTransactionCache(self)
      if cache is not None:
        key = ('getDocumentValueList', self, document.getPath())
        try:
          return cache[key]
        except KeyError:
          pass

      result = self._getTypeBasedMethod('getPermanentURL',
                     fallback_script_id='WebSection_getPermanentURL')(document)

      if cache is not None:
        cache[key] = result

      return result

    security.declareProtected(Permissions.View, 'getBreadcrumbItemList')
    def getBreadcrumbItemList(self, document):
      """
        Return a section dependent breadcrumb in the form
        of a list of (title, document) tuples.

        This method must be implemented through a
        portal type dependent script:
          WebSection_getBreadcrumbItemList
      """
      cache = getReadOnlyTransactionCache(self)
      if cache is not None:
        key = ('getDocumentValueList', self, document.getPath())
        try:
          return cache[key]
        except KeyError:
          pass

      result = self._getTypeBasedMethod('getBreadcrumbItemList',
                     fallback_script_id='WebSection_getBreadcrumbItemList')(document)

      if cache is not None:
        cache[key] = result

      return result
