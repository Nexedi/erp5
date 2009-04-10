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

from Products.ERP5.Document.WebSection import WebSection, WEBSECTION_KEY
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface, Cache
from Products.ERP5Type.Cache import CachingMethod

from Globals import get_request
from Persistence import Persistent
from ZPublisher import BeforeTraverse

from zLOG import LOG

WEBSITE_KEY = 'web_site_value'
WEBSITE_LANGUAGE_KEY = 'web_site_language'

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
    if isinstance(path, str):
      path = path.split( '/')

    # Every Web Section acts as a mini site though layout for document editing is the root layout
    #website_path = self._v_request.get(WEBSECTION_KEY, self._v_request.get(WEBSITE_KEY, None))
    # Only consider Web Site for absolute_url
    request = getattr(self, '_v_request', None)
    if request is None: request = self._v_request = get_request()
    # In ignore_layout case, we only remove empty element from path
    # XXX more support required for ignore_layout?
    if request.get('ignore_layout', None):
      return tuple([x for x in path if x])
    website_path = request.get(WEBSITE_KEY, None)
    select_language = request.get(WEBSITE_LANGUAGE_KEY, None)
    if website_path:
      website_path = tuple(website_path)    # Make sure all path are tuples
      path = tuple(path)                    # Make sure all path are tuples
      if select_language:
        website_path = website_path + (select_language,)      # Add the language part
      # Search for the common part index
      # XXX more testing should be added to check
      # if the URL is the kind of URL which is a Web Site
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
    rpp = request.other.get('VirtualRootPhysicalPath', ('', ))
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
      own version of physicalPathToVirtualPath and we set a default
      language
    """
    self._v_request = request
    request.physicalPathToVirtualPath = self._physicalPathToVirtualPath

    # If a skin selection is defined in this web site, change the skin now.
    skin_selection_name = container.getSkinSelectionName()
    if skin_selection_name and request.get('portal_skin', None) is None:
      container.getPortalObject().changeSkin(skin_selection_name)

    # Set default language if any
    default_language = container.getDefaultAvailableLanguage()
    if default_language and container.isStaticLanguageSelection():
      if request.get('AcceptLanguage') is not None:
        request['AcceptLanguage'].set(default_language, 80)

class WebSite(WebSection):
    """
      The Web Site root class is specialises WebSection
      by defining a global webmaster user.
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
                      , PropertySheet.WebSection
                      , PropertySheet.WebSite
                      , PropertySheet.Predicate
                      )

    web_section_key = WEBSITE_KEY

    security.declareProtected(Permissions.AccessContentsInformation, 'getWebSiteValue')
    def getWebSiteValue(self):
        """
          Returns the current web site (ie. self) though containment acquisition
        """
       
        return self

    # Static Language Selection support
    def _getExtensibleContent(self, request, name):
      language_list = self.getAvailableLanguageList()
      if language_list and self.isStaticLanguageSelection():
        # Interprete names which could be a language
        # as a language selection only if language_list
        # was defined or set default language
        if name in language_list:
          if request.get('AcceptLanguage') is not None:
            request['AcceptLanguage'].set(name, 100)
            request.set(WEBSITE_LANGUAGE_KEY, name)
          return self.asContext(id=name)
      return WebSection._getExtensibleContent(self, request, name)

    # Virtual Hosting Support
    security.declarePrivate( 'manage_beforeDelete' )
    def manage_beforeDelete(self, item, container):
      if item is self:
        handle = self.meta_type + '/' + self.getId()
        BeforeTraverse.unregisterBeforeTraverse(item, handle)
      WebSection.manage_beforeDelete(self, item, container)

    security.declarePrivate( 'manage_afterAdd' )
    def manage_afterAdd(self, item, container):
      if item is self:
        handle = self.meta_type + '/' + self.getId()
        BeforeTraverse.registerBeforeTraverse(item, WebSiteTraversalHook(), handle)
      WebSection.manage_afterAdd(self, item, container)

    security.declareProtected(Permissions.AccessContentsInformation, 'getPermanentURLList')
    def getPermanentURLList(self, document):
      """
        Return a list of URLs which exist in the site for
        a given document. This could be implemented either
        by keep a history of documents which have been
        accessed or by parsing all WebSections and listing
        all documents in each of them to build a reverse
        mapping of getPermanentURL
      """
      return map(lambda x:x.getPermanentURL(document), self.getWebSectionValueList())

    security.declareProtected(Permissions.AccessContentsInformation, 'getWebSectionValueList')
    def getWebSectionValueList(self, document):
      """
        Returns a list of sections which a given document is
        part of.

        This could be implemented either by testing all sections
        and building a cache or by using the predicate API
        to find which sections apply.
      """
      def getWebSectionUidList(section):
        # Only return visible web section
        if section.isVisible():
          result = [section.getUid()]
        else:
          result = []
        for o in section.contentValues(portal_type='Web Section'):
          result.extend(getWebSectionUidList(o))
        return result

      _getWebSectionUidList = CachingMethod(getWebSectionUidList,
                         id='WebSite._getWebSectionUidList',
                         cache_factory='erp5_content_medium')

      web_section_uid_list = _getWebSectionUidList(self)
      if web_section_uid_list:
        section_list = self.portal_domains.searchPredicateList(document, 
                          portal_type='Web Section',
                          uid=web_section_uid_list)

        section_dict = {}

        for section in section_list:
          section_dict[section.getPhysicalPath()] = section

        # Eliminate path
        for section in section_list:
          path = section.getPhysicalPath()
          for i in range(0, len(path)):
            sub_path = tuple(path[0:i])
            if section_dict.has_key(sub_path):
              del section_dict[sub_path]

        section_list = section_dict.values()

        # Sort by Index
        section_list.sort(key=lambda x: x.getIntIndex())

        return section_list
      else:
        return []
