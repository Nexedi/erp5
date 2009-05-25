##############################################################################
#
# Copyright (c) 2002-2008 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type import Permissions, PropertySheet,\
                              Constraint, Interface, Cache
from Products.ERP5.Document.Domain import Domain
from Products.ERP5.Document.Document import PermanentURLMixIn
from Acquisition import ImplicitAcquisitionWrapper, aq_base, aq_inner
from Products.ERP5Type.Base import TempBase
from Products.ERP5Type.UnrestrictedMethod import UnrestrictedMethod
from AccessControl import Unauthorized
from zLOG import LOG, WARNING
import sys

from Products.ERP5Type.Cache import getReadOnlyTransactionCache

# Global keys used for URL generation
WEBSECTION_KEY = 'web_section_value'
MARKER = []

class WebSection(Domain, PermanentURLMixIn):
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

      - WebSection_getWebSectionValue
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

    security.declareProtected(Permissions.View, '__bobo_traverse__')
    def __bobo_traverse__(self, request, name):
      """
        If no subobject is found through Folder API
        then try to lookup the object by invoking getDocumentValue
      """
      # Register current web site physical path for later URL generation
      if request.get(self.web_section_key, MARKER) is MARKER:
        request[self.web_section_key] = self.getPhysicalPath()
        # Normalize web parameter in the request
        # Fix common user mistake and transform '1' string to boolean
        for web_param in ['ignore_layout', 'editable_mode']:
          if hasattr(request, web_param):
            param = getattr(request, web_param, None)
            if isinstance(param, (list, tuple)):
              param = param[0]
            if param in ('1', 1, True):
              request.set(web_param, True)
            else:
              request.set(web_param, False)

      return PermanentURLMixIn.__bobo_traverse__(self, request, name)

    security.declareProtected(Permissions.AccessContentsInformation, 'getLayoutProperty')
    def getLayoutProperty(self, key, default=None):
      """
        A simple method to get a property of the current by
        acquiring it from the current section or its parents.
      """
      section = aq_inner(self)
      while section.getPortalType() in ('Web Section', 'Web Site'):
        result = section.getProperty(key, MARKER)
        if result not in (MARKER, None):
          return result
        section = section.aq_parent
      return default

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
      # Register current web site physical path for later URL generation
      if self.REQUEST.get(self.web_section_key, MARKER) is MARKER:
        self.REQUEST[self.web_section_key] = self.getPhysicalPath()
      self.REQUEST.set('current_web_section', self)
      if not self.REQUEST.get('editable_mode') and not self.REQUEST.get('ignore_layout'):
        # Try to use a custom renderer if any
        custom_render_method_id = self.getCustomRenderMethodId()
        if custom_render_method_id is not None:
          return getattr(self, custom_render_method_id)()
        if self.isDefaultPageDisplayed():
          # The following could be moved to a typed based method for more flexibility
          document = self.getDefaultDocumentValue()
          if document is None:
            # no document found for current user, still such document may exists
            # in some cases user (like Anonymous) can not view document according to portal catalog
            # but we may ask him to login if such a document exists
            isAuthorizationForced = getattr(self, 'isAuthorizationForced', None)
            if isAuthorizationForced is not None and isAuthorizationForced():
              getDefaultDocumentValue = UnrestrictedMethod(self.getDefaultDocumentValue)
              if getDefaultDocumentValue() is not None:
                # force user to login as specified in Web Section
                raise Unauthorized
          if document is not None and document.getReference() is not None:
            # we use web_site_module/site_id/section_id/page_reference
            # as the url of the default document.
            self.REQUEST.set('current_web_document', document)
            self.REQUEST.set('is_web_section_default_document', 1)
            document = aq_base(document.asContext(
                id=document.getReference(),
                original_container=document.getParentValue(),
                original_id=document.getId(),
                editable_absolute_url=document.absolute_url()))
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

      if result is not None:
        result = result.__of__(self)

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

      if result is not None:
        result = [doc.__of__(self) for doc in result]

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
        key = ('getPermanentURL', self, document.getPath())
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
    def getBreadcrumbItemList(self, document=None):
      """
        Return a section dependent breadcrumb in the form
        of a list of (title, document) tuples.

        This method must be implemented through a
        portal type dependent script:
          WebSection_getBreadcrumbItemList
      """
      if document is None:
        document = self
      cache = getReadOnlyTransactionCache(self)
      if cache is not None:
        key = ('getBreadcrumbItemList', self, document.getPath())
        try:
          return cache[key]
        except KeyError:
          pass

      result = self._getTypeBasedMethod('getBreadcrumbItemList',
                     fallback_script_id='WebSection_getBreadcrumbItemList')(document)

      if cache is not None:
        cache[key] = result

      return result

    security.declareProtected(Permissions.View, 'getSiteMapTree')
    def getSiteMapTree(self, **kw):
      """
        Return a site map tree section dependent breadcrumb in the
        form of a list of dicts whose structure is provided as a tree
        so that it is easy to implement recursive call with TAL/METAL:

        [
          {
            'url'      : '/erp5/web_site_module/site/section',
            'level'    : 1,
            'translated_title' : 'Section Title',
            'subsection' : [
              {
                'url'      : '/erp5/web_site_module/site/section/reference',
                'level'    : 2,
                'translated_title' : 'Sub Section Title',
                'subsection' : None,
              },
              ...
            ],
          }
          ...
        ]

        This method must be implemented through a
        portal type dependent script:
          WebSection_getSiteMapTree
      """
      cache = getReadOnlyTransactionCache(self)
      if cache is not None:
        key = ('getSiteMapTree', self) + tuple(kw.items())
        try:
          return cache[key]
        except KeyError:
          pass

      result = self._getTypeBasedMethod('getSiteMapTree',
                     fallback_script_id='WebSection_getSiteMapTree')(**kw)

      if cache is not None:
        cache[key] = result

      return result
