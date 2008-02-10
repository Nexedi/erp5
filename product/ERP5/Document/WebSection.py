##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2002-2006 Nexedi SARL and Contributors. All Rights Reserved.
# Copyright (c) 2006-2007 Nexedi SA and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
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
import sys

from Products.ERP5Type.Cache import getReadOnlyTransactionCache

# Global keys used for URL generation
WEBSECTION_KEY = 'web_section_value'
MARKER = []

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
            if getattr(request, web_param, None) in ('1', 1, True):
              request.set(web_param, True)
            else:
              request.set(web_param, False)

      # Normal traversal
      try:
        return getattr(self, name)
      except AttributeError:
        pass

      try:
        return self[name]
      except KeyError:
        pass

      # Permanent URL traversal
      # First we must get the logged user by forcing identification
      cache = getReadOnlyTransactionCache(self)
      # LOG('getReadOnlyTransactionCache', 0, repr(cache)) # Currently, it is always None
      if cache is not None:
        key = ('__bobo_traverse__', self, 'user')
        try:
          user = cache[key]
        except KeyError:
          user = MARKER
      else:
        user = MARKER
      old_user = getSecurityManager().getUser()
      if user is MARKER:
        user = None # By default, do nothing
        if old_user is None or old_user.getUserName() == 'Anonymous User':
          user_folder = getToolByName(self, 'acl_users', None)
          if user_folder is not None:
            try:
              if request.get('PUBLISHED', MARKER) is MARKER:
                # request['PUBLISHED'] is required by validate
                request.other['PUBLISHED'] = self
                has_published = False
              else:
                has_published = True
              user = user_folder.validate(request)
              if not has_published:
                del request.other['PUBLISHED']
            except:
              LOG("ERP5 WARNING",0,
                  "Failed to retrieve user in __bobo_traverse__ of WebSection %s" % self.getPath(),
                  error=sys.exc_info())
              user = None
        if user is not None and user.getUserName() == 'Anonymous User':
          user = None # If the user which is connected is anonymous,
                      # do not try to change SecurityManager
        if cache is not None:
          cache[key] = user
      if user is not None:
        # We need to perform identification
        old_manager = getSecurityManager()
        newSecurityManager(get_request(), user)
      # Next get the document per name
      portal = self.getPortalObject()
      document = self.getDocumentValue(name=name, portal=portal)
      # Last, cleanup everything
      if user is not None:
        setSecurityManager(old_manager)
      if document is not None:
        document = aq_base(document.asContext(id=name, # Hide some properties to permit locating the original
                                              original_container=document.getParentValue(),
                                              original_id=document.getId(),
                                              editable_absolute_url=document.absolute_url()))
        return document.__of__(self)

      # Not found section
      method = request.get('REQUEST_METHOD', 'GET')
      if not method in ('GET', 'POST'):
        return NullResource(self, name, request).__of__(self)
      # Waaa. unrestrictedTraverse calls us with a fake REQUEST.
      # There is proabably a better fix for this.
      try:
        request.RESPONSE.notFoundError("%s\n%s" % (name, method))
      except AttributeError:
        raise KeyError, name

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
        # Try to use a custom renderer if any
        custom_render_method_id = self.getCustomRenderMethodId()
        if custom_render_method_id is not None:
          return getattr(self, custom_render_method_id)()
        # The following could be moved to a typed based method for more flexibility
        document = self.getDefaultDocumentValue()
        if document is not None:
          self.REQUEST.set('current_web_document', document.__of__(self)) # Used to be document
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
        if cache.get(key, MARKER) is MARKER: cache[key] = method

      return method(name, portal=portal, **kw)

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
