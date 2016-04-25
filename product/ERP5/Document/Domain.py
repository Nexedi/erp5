##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
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

from Products.ERP5Type import Permissions, PropertySheet

from Products.ERP5.Document.MetaResource import MetaResource
from Products.ERP5.Document.MetaNode import MetaNode
from Products.ERP5Type.Core.Predicate import Predicate

class Domain(Predicate, MetaNode, MetaResource):
  """
    Domain can be used as MetaNodes or MetaResources. For example,
    a Domain viewed as a MetaNode can search for all emerging movements
    and compare it with its capacity.

    Structure is:
       - base domain (like base category)
       - sub domain (like category)

    Allows to define ranges:
       - price between X and Y
       - portal_type in (a, b, c)
       - price between X and Y and region in (a, b, c)

    Reports:
       - listbox allows to produce reports
         - output to html, pdf or ooffice
         - definition through the web (ie. which field in which column, which statistics)
         - definition of selection (to list)
         - ability for use to "save" favourite report (user reports)
         - library of favourite reports (global reports)
       - matrixbox allows to produce reports
         - output to html, pdf or ooffice
         - definition through the web (ie. which base_category or base_domain in which axis)
         - definition of selection (to map to matrix)
         - ability for use to "save" favourite report (user reports)
         - library of favourite reports (global reports)

    Domain and Domain Generators are now unified. Any domain may act
    as a domain generator or as a simple predicate.

    A Domain Generator uses a method (SQL, Python) to select objects
    which are then wrapped as Virtual Domains. This can be used for
    example to provide the list the 10 best selling shops to
    a report tree.
  """
  meta_type = 'ERP5 Domain'
  portal_type = 'Domain'
  add_permission = Permissions.AddPortalContent

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.Predicate
                    , PropertySheet.Domain
                    , PropertySheet.SortIndex
                    , PropertySheet.CategoryCore
                    )

  security.declareProtected( Permissions.AccessContentsInformation, 'getRelativeUrl' )
  def getRelativeUrl(self):
    """
      We must eliminate portal_categories in the RelativeUrl
      since it is never present in the category list
    """
    content_path = self.portal_url.getRelativeContentPath(self)
    if content_path[0] in ('portal_categories', 'portal_domains'):
      return '/'.join(content_path[1:])
    return '/'.join(content_path)

  # Generator API

  # How to define a generated subdomain
  security.declareProtected( Permissions.AccessContentsInformation, 'getDomainGeneratorList' )
  def getDomainGeneratorList(self, depth=0):
    """
    We call a script which builds for us a list DomainGenerator instances
    We need a way to know how deep we are in the domain generation
    to prevent infinite recursion XXX not implemented
    """
    klass = tmp_domain_generator = self.newContent(portal_type='Domain Generator', temp_object=1)
    script = self.getDomainGeneratorMethodId('')
    return tmp_domain_generator.getDomainGeneratorList(depth=depth, klass=klass, script=script, parent=self)

  security.declareProtected( Permissions.AccessContentsInformation, 'generateTempDomain' )
  def generateTempDomain(self, id):
    """
    We generate temp domain here because we must set an aquisition wrapper
    """
    domain = self.newContent(id=id, portal_type='Domain', temp_object=1)
    return domain.__of__(self)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getChildDomainValueList')
  def getChildDomainValueList(self, parent = None, **kw):
    """
    Return child domain objects already present or me may generate
    dynamically childs.
    """
    if parent is None:
      parent = self
    return self.portal_domains.getChildDomainValueList(parent, **kw)

  # Experimental - WebDAV browsing support - ask JPS
    security.declareProtected(Permissions.AccessContentsInformation,
                              'experimental_listDAVObjects')
  def experimental_listDAVObjects(self):
    result = self.objectValues(portal_type = self.getPortalType())
    result.extend(self.portal_catalog(selection_domain = self))
    return result

  def getPrice(self):
    """Workaround price lookup error on domains)"""
    return None

