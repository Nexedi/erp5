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

from Products.CMFCategory.Category import Category as CMFCategory
from AccessControl import ClassSecurityInfo

from Products.ERP5.Document.MetaNode import MetaNode
from Products.ERP5.Document.MetaResource import MetaResource
from Products.ERP5Type import interfaces, Permissions, PropertySheet
from Products.ERP5Type.Base import Base
from Products.ERP5.Document.Predicate import Predicate

from zLOG import LOG


class Category(CMFCategory, Predicate, MetaNode, MetaResource):
    """
        Category objects allow to define classification categories
        in an ERP5 portal. For example, a document may be assigned a color
        attribute (red, blue, green). Rather than assigning an attribute
        with a pop-up menu (which is still a possibility), we can prefer
        in certain cases to associate to the object a category. In this
        example, the category will be named color/red, color/blue or color/green

        Categories can include subcategories. For example, a region category can
        define
            region/europe
            region/europe/west/
            region/europe/west/france
            region/europe/west/germany
            region/europe/south/spain
            region/americas
            region/americas/north
            region/americas/north/us
            region/americas/south
            region/asia

        In this example the base category is 'region'.

        Categories are meant to be indexed with the ZSQLCatalog (and thus
        a unique UID will be automatically generated each time a category is
        indexed).

        Categories allow define sets and subsets of objects and can be used
        for many applications :

        - association of a document to a URL

        - description of organisations (geographical, professional)

        Through acquisition, it is possible to create 'virtual' classifications based
        on existing documents or categories. For example, if there is a document at
        the URL
            organisation/nexedi
        and there exists a base category 'client', then the portal_categories tool
        will allow to create a virtual category
            client/organisation/nexedi

        Virtual categories allow not to duplicate information while providing
        a representation power equivalent to RDF or relational databases.

        Categories are implemented as a subclass of BTreeFolders

        NEW: categories should also be able to act as a domain. We should add
        a Domain interface to categories so that we do not need to regenerate
        report trees for categories.
    """

    meta_type='ERP5 Category'
    portal_type='Category' # may be useful in the future...
    isPortalContent = 1
    isRADContent = 1
    isCategory = 1
    allowed_types = ('ERP5 Category', )

    # Declarative security
    security = ClassSecurityInfo()
    security.declareProtected(Permissions.ManagePortal,
                              'manage_editProperties',
                              'manage_changeProperties',
                              'manage_propertiesForm',
                                )

    property_sheets = ( PropertySheet.Base
                      , PropertySheet.SimpleItem
                      , PropertySheet.CategoryCore
                      , PropertySheet.Codification
                      , PropertySheet.Reference
                      , PropertySheet.SortIndex)

    # Inheritance
    __init__ = Predicate.__init__
 
    # Experimental - virtual document access
    def _experimental_aq_dynamic(self, name):
      result = Base._aq_dynamic(self, name)
      if result is not None:
        return result
      # Do some optimisation here for names which can not be names of documents
      if name.startswith('_') or name.startswith('portal_')\
          or name.startswith('aq_') or name.startswith('selection_') \
          or name.startswith('sort-') or name == 'getLayout' \
          or name == 'getListItemUrl' or name.startswith('WebSite_'):
        return None
      # Use a non recursion variable
      cache_key = 'web_site_aq_cache'
      request = self.REQUEST
      # Prevent infinite recursion
      if not request.has_key(cache_key):
        request[cache_key] = {}
      elif request[cache_key].has_key(name):
        return request[cache_key][name]
      try:
        result_list = self.portal_catalog(portal_type="Person", id = name)
        if len(result_list):
          return result_list[0].getObject()
      except:
        # Cleanup non recursion dict in case of exception
        if request[cache_key].has_key(name):
          del request[cache_key][name]
        raise
      return None

    # Experimental - WebDAV browsing support - ask JPS
    def experimental_listDAVObjects(self):
      """
      """
      from zLOG import LOG
      LOG("Category listDAVObjects" ,0, "listDAVObjects")
      # XXX - We should try to use only Lazy Maps and to set a limit to the
      # number of objects
      # First show the subcategories
      result = list(self.objectValues(spec=('ERP5 Category', 'ERP5 Base Category')))
      # Then show the related documents
      result.extend(self.portal_categories.getRelatedValueList(
                    self, self.getBaseCategory().getId(), portal_type="Person"))
      return result

