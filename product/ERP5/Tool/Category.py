##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solane <jp@nexedi.com>
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
from Products.CMFCategory.Category import BaseCategory as CMFBaseCategory
from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo

from Products.ERP5.Document.MetaNode import MetaNode
from Products.ERP5.Document.MetaResource import MetaResource
from Products.ERP5Type import Interface, Permissions, PropertySheet
from Products.ERP5.Document.PredicateGroup import PredicateGroup

from zLOG import LOG

manage_addCategoryForm=DTMLFile('dtml/category_add', globals())

def addCategory( self, id, title='', REQUEST=None ):
    """
        Add a new Category and generate UID by calling the
        ZSQLCatalog
    """
    sf = Category( id )
    sf._setTitle(title)
    self._setObject( id, sf )
    sf = self._getOb( id )
    sf.reindexObject()
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

class Category(CMFCategory, PredicateGroup, MetaNode, MetaResource):
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

    # Declarative constructors
    constructors =   (manage_addCategoryForm, addCategory)

    # Declarative security
    security = ClassSecurityInfo()
    security.declareProtected(Permissions.ManagePortal,
                              'manage_editProperties',
                              'manage_changeProperties',
                              'manage_propertiesForm',
                                )

    property_sheets = ( PropertySheet.Base
                      , PropertySheet.SimpleItem )

    # Declarative interfaces
    __implements__ = ( Interface.Predicate , )

    def recursiveReindexObject(self):
      """
        Fixes the hierarchy structure (use of Base class)
        XXXXXXXXXXXXXXXXXXXXXXXX
        BUG here : when creating a new base category
      """
      self.activate().recursiveImmediateReindexObject()

    def recursiveImmediateReindexObject(self):
        """
          Applies immediateReindexObject recursively
        """
        # Reindex self
        self.immediateReindexObject()
        # Reindex contents
        for c in self.objectValues():
          c.recursiveImmediateReindexObject()

manage_addBaseCategoryForm=DTMLFile('dtml/base_category_add', globals())

def addBaseCategory( self, id, title='', REQUEST=None ):
    """
        Add a new Category and generate UID
    """
    sf = BaseCategory( id )
    sf._setTitle(title)
    self._setObject( id, sf )
    sf = self._getOb( id )
    sf.reindexObject()
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

class BaseCategory(CMFBaseCategory):
    """
      Base Categories allow to implement virtual categories
      through acquisition
    """
    meta_type='ERP5 Base Category'
    portal_type='Base Category' # maybe useful some day
    allowed_types = ('ERP5 Category',)
    isPortalContent = 1
    isRADContent = 1
    isCategory = 1

    # Declarative constructors
    constructors =   (manage_addBaseCategoryForm, addBaseCategory)

    property_sheets = ( PropertySheet.Base
                      , PropertySheet.SimpleItem
                      , PropertySheet.BaseCategory)

InitializeClass( Category )
InitializeClass( BaseCategory )
