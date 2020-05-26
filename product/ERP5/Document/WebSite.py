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

from Products.ERP5.Document.WebSection import WebSectionTraversalHook
from Products.ERP5Type.Globals import get_request
from ZPublisher.HTTPRequest import HTTPRequest

WEBSITE_KEY = 'web_site_value'
WEBSITE_LANGUAGE_KEY = 'web_site_language'

# WebSite Document class has been migrated to ZODB Components and this module
# has been kept here because of WebSiteTraversalHook which is not an ERP5
# object
kept_for_backward_compatibility_only = True
class WebSiteTraversalHook(WebSectionTraversalHook):
  """Traversal Hook for websites

  * Change the skin selection to the one defined on the website (same as websection)
  * Select default website language
  * Change URL generation so that content URLs includes the website in the URL

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
      return HTTPRequest.physicalPathToVirtualPath(request, path)
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

    # Set skin selection
    WebSectionTraversalHook.__call__(self, container, request)

    # Set default language if any
    default_language = container.getDefaultAvailableLanguage()
    if default_language and container.isStaticLanguageSelection():
      if request.get('AcceptLanguage') is not None:
        request['AcceptLanguage'].set(default_language, 80)
    else:
      accept_language = request.get('AcceptLanguage')
      if accept_language is not None:
        selected_language = accept_language.select_language(
            container.getAvailableLanguageList())
        if selected_language:
          request['AcceptLanguage'].set(selected_language, 80)
        elif default_language:
          request['AcceptLanguage'].set(default_language, 80)
