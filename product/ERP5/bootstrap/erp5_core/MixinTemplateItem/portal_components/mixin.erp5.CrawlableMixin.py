# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
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

import six
from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type import Permissions
from Products.ERP5Type.Utils import normaliseUrl
from six.moves.urllib.parse import urlsplit, urlunsplit
from lxml import html as etree_html

class CrawlableMixin:
  """
  Generic implementation of ICrawlable interface
  """
  # Declarative security
  security = ClassSecurityInfo()

  security.declareProtected(Permissions.AccessContentsInformation, 'getFrequencyIndex')
  def getFrequencyIndex(self):
    """
      Returns the document update frequency as an integer
      which is used by alamrs to decide which documents
      must be updates at which time. The index represents
      a time slot (ex. all days in a month, all hours in a week).
    """
    try:
      return self.getUpdateFrequencyValue().getIntIndex()
    except AttributeError:
      # Catch Attribute error or Key error - XXX not beautiful
      return 0

  security.declareProtected(Permissions.AccessContentsInformation, 'getCreationDateIndex')
  def getCreationDateIndex(self, at_date = None):
    """
    Returns the document Creation Date Index which is the creation
    date converted into hours modulo the Frequency Index.
    """
    frequency_index = self.getFrequencyIndex()
    if not frequency_index: return -1 # If not update frequency is provided, make sure we never update

    from erp5.component.module.DateUtils import convertDateToHour,\
      number_of_hours_in_day, number_of_hours_in_year
    hour = convertDateToHour(date=self.getCreationDate())
    creation_date_index = hour % frequency_index
    # in the case of bisextile year, we substract 24 hours from the creation date,
    # otherwise updating documents (frequency=yearly update) created the last
    # 24 hours of bissextile year will be launched once every 4 years.
    if creation_date_index >= number_of_hours_in_year:
      creation_date_index = creation_date_index - number_of_hours_in_day

    return creation_date_index

  security.declareProtected(Permissions.AccessContentsInformation, 'isUpdatable')
  def isUpdatable(self):
    """
      This method is used to decide which document can be updated
      in the crawling process. This can depend for example on
      workflow states (publication state,
      validation state) or on roles on the document.
    """
    method = self._getTypeBasedMethod('isUpdatable',
        fallback_script_id = 'Document_isUpdatable')
    return method()

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getContentURLList')
  def getContentURLList(self):
    """
    Returns a list of URLs referenced by the content of this document.
    Default implementation consists in analysing the document
    converted to HTML. Subclasses may overload this method
    if necessary. However, it is better to extend the conversion
    methods in order to produce valid HTML, which is useful to
    many people, rather than overload this method which is only
    useful for crawling.
    """
    html_content = self.asEntireHTML()
    html_tree = etree_html.fromstring(html_content)
    base_href = self.getContentBaseURL()
    if base_href:
      html_tree.make_links_absolute(base_href)
    href_list = []
    for _, attribute_name, link, _ in html_tree.iterlinks():
      # For now take into acount only a and img tags
      if attribute_name not in ('href',):
        continue
      if six.PY2 and isinstance(link, six.text_type):
        link = link.encode('utf-8')
      href_list.append(link)
    return href_list

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getContentBaseURL')
  def getContentBaseURL(self):
    """
    Returns the content base URL based on the actual content or
    on its URL.
    """
    raw_url = self.asURL() or ''
    splitted_url = urlsplit(raw_url)
    path_part = splitted_url[2]
    path_part = '/'.join(path_part.split('/')[:-1])
    base_url = urlunsplit((splitted_url[0], splitted_url[1], path_part, None,
                           None))
    if six.PY2 and isinstance(base_url, six.text_type):
      base_url = base_url.encode('utf-8')
    return base_url


  security.declareProtected(Permissions.AccessContentsInformation,
                            'getContentNormalisedURLList')
  def getContentNormalisedURLList(self):
    """
    Call url normalizer for each url returned by getContentURLList
    Return only url associated to the same Domain
    """
    reference_domain = urlsplit(normaliseUrl(self.asURL() or ''))[1]
    # in www.example.com or www.3.example.com
    # keep only the example.com part
    reference_domain = ''.join(reference_domain.split('.')[-2:])
    if six.PY2 and isinstance(reference_domain, six.text_type):
      reference_domain = reference_domain.encode('utf-8')
    url_list = []
    base_url = self.getContentBaseURL()
    for url in self.getContentURLList():
      try:
        url = normaliseUrl(url, base_url=base_url)
      except UnicodeDecodeError:
        # Ignore wrong encoding errors
        # Web is not a kind world
        continue
      if not url:
        continue
      url_domain = urlsplit(url)[1]
      if six.PY2 and isinstance(url_domain, six.text_type):
        url_domain = url_domain.encode('utf-8')
      if url_domain and ''.join(url_domain.split('.')[-2:]) != reference_domain:
        continue
      # if domain is empty (relative link) or domain is same, then OK
      url_list.append(url)
    return url_list

InitializeClass(CrawlableMixin)
