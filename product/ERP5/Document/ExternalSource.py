##############################################################################
#
# Copyright (c) 2002-2007 Nexedi SARL and Contributors. All Rights Reserved.
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
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5.Document.Url import UrlMixIn

import mimetypes
import re
import urllib
from htmlentitydefs import name2codepoint
from DateTime import DateTime

class ExternalSource(XMLObject, UrlMixIn):
  """
  An External Source consists of single URL which defines the
  root of a collection of documents, each of which can be accessed
  individually. The URL can be an http site, an ftp site, a local repository,
  a samba server, etc.

  The main purpose of External Sources is to group related documents
  and define shared security policies, shared updated policies, etc.
  For example, all pages of
  a wiki with restricted access rights share the same security policy
  (ex. team, project, etc.). Another purpose of the External Source class is
  to make it easy to manage external sources of knowledge (adding them,
  removing them, etc.).

  The second purpose of an external source is to provide a way to search
  contents stored externally in a system which is not compatible with
  ERP5 Catalog.

  Example of external sources:

  - a Web Site

  - a SAMBA share

  - an FTP server

  - a backup server

  - a mail directory

  - a mailing list archive

  ExternalSource may be subclassed to provide more automation
  features. This is useful for example to manage the creation
  of a mailing list, the deletion of mailing list and the
  definition of the members of a mailing list in a centralised way.

  NOTE: RSS feeds are not external sources but standard Text
  documents with transformation and update policy. They use
  the populateContent method to create subcontent from
  a root content. This is different with crawling.

  NOTE2: access to filesystems through URL requires to extend
  urllib2 so that directories are handled as if they were web
  pages OR RSS feed with a list of files (and associated URL).
  Complete implemetation of external sources will require
  major extensions to urllib2 (or equivalent).

  NOTE3: it is possible to make external search sources persistent
  by triggering an activity with newContent for every displayed
  result. This can be done by wrapping the results in a generator
  (yield). The interest of this approach is to make it possible to
  search already searched contents without having to go through the
  external source search (ie. with the front page search).
  """
  # CMF Type Definition
  meta_type = 'ERP5 External Source'
  portal_type = 'External Source'
  isPortalContent = 1
  isRADContent = 1

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Version
                    , PropertySheet.Reference
                    , PropertySheet.Document
                    , PropertySheet.TextDocument
                    , PropertySheet.Url
                    , PropertySheet.ExternalDocument
                    , PropertySheet.Periodicity
                    )

  # Crawling API
  security.declareProtected(Permissions.ModifyPortalContent, 'crawlContent')
  def crawlContent(self):
    """
    Creates the initial content from the URL by crawling the root
    """
    self.portal_contributions.crawlContent(self, container=self)

  security.declareProtected(Permissions.AccessContentsInformation, 'getContentURLList')
  def getContentURLList(self):
    """
    Returns the root of the crawling process
    """
    return [self.asURL()]

  security.declareProtected(Permissions.AccessContentsInformation, 'getContentBaseURL')
  def getContentBaseURL(self):
    """
    Returns None to force crawler to ignore this parameter
    """
    return None

  security.declareProtected(Permissions.View, 'isIndexContent')
  def isIndexContent(self, content=None):
    """
      This method is able to answer a content object if it is an index or a
      "real" content.  Sometimes (though not often) we want to define a content
      as index (e.g. if it is only a list of mailing list messages), so that we
      do not index it for searching etc).  Default implementation returns
      False.
    """
    if content is None: 
      # this means that we are called directly, and external source 
      # is an index by definition
      return True
    method = self._getTypeBasedMethod('isIndexContent')
    if method is None:
      return False
    return method(content)

  # Search API
  security.declareProtected(Permissions.SearchCatalog, 'searchResults')
  def searchResults(self, **kw):
    """
    Search results. There is no notion of security here since
    the source is external.

    NOTE: implementation is delegated to a script so that different
    kinds of sources may be implemented using different portal
    types.

    NOTE2: a typical implementation consists in creating
    a specific SQL method with a dedicated connector then
    force the SQL catalog to use that method instead of the standard
    ones, yet delegate the SQL generation to the catalog.
    """
    method = self._getTypeBasedMethod('searchResults')
    return method(**kw)

  security.declareProtected(Permissions.SearchCatalog, 'countResults')
  def countResults(self, **kw):
    """
    Count results. There is no notion of security here since
    the source is external.

    NOTE: implementation is delegated to a script so that different
    kinds of sources may be implemented using different portal
    types.
    """
    method = self._getTypeBasedMethod('countResults')
    return method(**kw)
