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

from erp5.component.document.WebSection import WebSection
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.Cache import CachingMethod

from warnings import warn
from zExceptions import Redirect

WEBSITE_KEY = 'web_site_value'
WEBSITE_LANGUAGE_KEY = 'web_site_language'

class WebSite(WebSection):
  """
      The Web Site root class is specialises WebSection
      by defining a global webmaster user.
  """
  # CMF Type Definition
  meta_type       = 'ERP5 Web Site'
  portal_type     = 'Web Site'

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
  def getExtensibleContent(self, request, name):
    language_list = self.getAvailableLanguageList()
    if language_list and self.isStaticLanguageSelection():
      # Interprete names which could be a language
      # as a language selection only if language_list
      # was defined or set default language
      if name in language_list:
        default_language = self.getDefaultAvailableLanguage()
        if request.get('AcceptLanguage') is not None:
          request['AcceptLanguage'].set(name, 10)
          request.set(WEBSITE_LANGUAGE_KEY, name)
        if self.isTempObject() or name == default_language:
          redirect_path_list = [self.getOriginalDocument().absolute_url()]
          if name != default_language:
            redirect_path_list.append(name)
          redirect_path_list.extend(reversed(request['TraversalRequestNameStack']))
          request['minimum_language_redirect_url'] = '/'.join(redirect_path_list)
          query_string = request.get('QUERY_STRING')
          if query_string:
            request['minimum_language_redirect_url'] += '?' + query_string
        return self.getOriginalDocument().asContext(id=name, __language_web_site=True)
    return WebSection.getExtensibleContent(self, request, name)

  security.declarePublic('isSubtreeIndexable')
  def isSubtreeIndexable(self):
    if self.isTempObject() and getattr(self, '__language_web_site', False):
      # temp Web Site used to select a language must not prevent
      # document indexation
      return self.aq_inner.aq_parent.isSubtreeIndexable()
    return super(WebSite, self).isSubtreeIndexable()

  def _getExtensibleContent(self, request, name):
    """
    Legacy API
    """
    warn("_getExtensibleContent() function is deprecated. Use getExtensibleContent() instead.", \
          DeprecationWarning, stacklevel=2)
    return self.getExtensibleContent(request, name)

  def _getTraversalHookClass(self):
    from Products.ERP5.Document.WebSite import WebSiteTraversalHook
    return WebSiteTraversalHook

  def __before_publishing_traverse__(self, self2, request):
    redirect_url = request.get('minimum_language_redirect_url')
    if redirect_url:
      raise Redirect(redirect_url)
    return super(WebSite, self).__before_publishing_traverse__(self2, request)

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
    return [x.getPermanentURL(document) for x in self.getWebSectionValueList(document)]

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
          if sub_path in section_dict:
            del section_dict[sub_path]

      # Sort by Index
      return sorted(section_dict.values(), key=lambda x: x.getIntIndex())
    else:
      return []