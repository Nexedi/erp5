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

import string

from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base, aq_inner, aq_parent

from Products.ERP5Type import Permissions
from Products.ERP5Type import PropertySheet
from Products.ERP5Type.Document.Folder import Folder
from Products.CMFCategory.Renderer import Renderer

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

class Category(Folder):
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

    meta_type='CMF Category'
    portal_type='Category' # may be useful in the future...
    isPortalContent = 1
    isRADContent = 1
    isCategory = 1
    icon = None

    allowed_types = (
                  'CMF Category',
               )

    # Declarative security
    security = ClassSecurityInfo()
    security.declareProtected(Permissions.ManagePortal,
                              'manage_editProperties',
                              'manage_changeProperties',
                              'manage_propertiesForm',
                                )

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.SimpleItem )

    # Declarative constructors
    constructors =   (manage_addCategoryForm, addCategory)

    # Filtered Types allow to define which meta_type subobjects
    # can be created within the ZMI
    def filtered_meta_types(self, user=None):
        # Filters the list of available meta types.
        # so that only Category objects appear inside the
        # CategoryTool contents
        all = Category.inheritedAttribute('filtered_meta_types')(self)
        meta_types = []
        for meta_type in self.all_meta_types():
            if meta_type['name'] in self.allowed_types:
                meta_types.append(meta_type)
        return meta_types

    security.declareProtected(Permissions.AccessContentsInformation,
                                                    'getLogicalPath')
    def getLogicalPath(self):
      """
        Returns logical path, starting under base category.
      """
      objectlist = []
      base = self.getBaseCategory()
      current = self
      while not current is base :
        objectlist.insert(0, current)
        current = aq_parent(current)

      # it s better for the user to display something than only ''...
      logical_title_list = []
      for object in objectlist:
        logical_title = object.getTitle()
        if logical_title in [None, '']:
          logical_title = object.getId()
        logical_title_list.append(logical_title)
      return '/'.join(logical_title_list)

    security.declareProtected(Permissions.AccessContentsInformation,
                                                    'getCategoryChildValueList')
    def getCategoryChildValueList(self, recursive=1,include_if_child=1,**kw):
      """
          List the child objects of this category and all its subcategories.

          recursive - if set to 1, list recursively
      """
      if not(include_if_child) and len(self.objectValues(self.allowed_types))>0:
        value_list = []
      else:
        value_list = [self]
      if recursive:
        for c in self.objectValues(self.allowed_types):
          value_list.extend(c.getCategoryChildValueList(recursive = 1,include_if_child=include_if_child))
      else:
        for c in self.objectValues(self.allowed_types):
          value_list.append(c)
      return value_list

    # List names recursively
    security.declareProtected(Permissions.AccessContentsInformation,
                                                    'getCategoryChildRelativeUrlList')
    def getCategoryChildRelativeUrlList(self, base='', recursive=1):
      """
          List the path of this category and all its subcategories.

          base -- a boolean or a string. If it is a string, then use
                  that string as a base

          recursive - if set to 1, list recursively
      """
      if base == 0 or base is None: base = '' # Make sure we get a meaningful base
      if base == 1: base = self.getBaseCategoryId() + '/' # Make sure we get a meaningful base
      url_list = []
      for value in self.getCategoryChildValueList(recursive = recursive):
        url_list.append(base + value.getRelativeUrl())
      return url_list

    security.declareProtected(Permissions.AccessContentsInformation, 'getPathList')
    getPathList = getCategoryChildRelativeUrlList

    security.declareProtected(Permissions.AccessContentsInformation,
                                                      'getCategoryChildTitleItemList')
    def getCategoryChildTitleItemList(self, recursive=1, base=0, **kw):
      """
      Returns a list of tuples by parsing recursively all categories in a
      given list of base categories. Uses getTitle as default method
      """
      return self.getCategoryChildItemList(recursive = recursive, display_id='title', base=base, **kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                                                      'getCategoryChildTitleOrIdItemList')
    def getCategoryChildTitleOrIdItemList(self, recursive=1, base=0, **kw):
      """
      Returns a list of tuples by parsing recursively all categories in a
      given list of base categories. Uses getTitle as default method
      """
      return self.getCategoryChildItemList(recursive = recursive, display_id='title_or_id', base=base, **kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                                                      'getCategoryChildLogicalPathItemList')
    def getCategoryChildLogicalPathItemList(self, recursive=1, base=0, **kw):
      """
      Returns a list of tuples by parsing recursively all categories in a
      given list of base categories. Uses getLogicalPath as default method
      """
      return self.getCategoryChildItemList(recursive = recursive, display_id='logical_path', base=base, **kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                                                      'getCategoryChildIdItemList')
    def getCategoryChildIdItemList(self, recursive=1, base=0, **kw):
      """
      Returns a list of tuples by parsing recursively all categories in a
      given list of base categories. Uses getId as default method
      """
      return self.getCategoryChildItemList(recursive = recursive, display_id='id', base=base, **kw)


    security.declareProtected(Permissions.AccessContentsInformation,
                                                      'getCategoryChildItemList')
    def getCategoryChildItemList(self, recursive=1, base=0, **kw):
      """
      Returns a list of tuples by parsing recursively all categories in a
      given list of base categories. Each tuple contains::

        (c.relative_url,c.display_id())

      base -- if set to 1, relative_url will start with the base category id
              if set to 0 and if base_category is a single id, relative_url
              are relative to the base_category (and thus  doesn't start
              with the base category id)

              if set to string, use string as base

      display_id -- method called to build the couple

      recursive -- if set to 0 do not apply recursively
      """
      value_list = self.getCategoryChildValueList(recursive=recursive,**kw)
      return Renderer(base=base, **kw).render(value_list)

    # Alias for compatibility
    security.declareProtected(Permissions.View, 'getFormItemList')
    def getFormItemList(self):
      """
        Alias for compatibility and accelation
      """
      return self.getCategoryChildItemList(base=0,display_none_category=1,recursive=1)

    # Alias for compatibility
    security.declareProtected(Permissions.AccessContentsInformation, 'getBaseItemList')
    def getBaseItemList(self, base=0, prefix=''):
      return self.getCategoryChildItemList(base=base,display_none_category=0,recursive=1)

    security.declareProtected(Permissions.AccessContentsInformation,
                                                        'getCategoryRelativeUrl')
    def getCategoryRelativeUrl(self, base=0 ):
      """
        Returns a relative_url of this category relative
        to its base category (if base is 0) or to
        portal_categories (if base is 1)
      """
      my_parent = aq_parent(self)

      if my_parent is not None:
        if my_parent.meta_type != self.meta_type:
          if base:
            return self.getBaseCategoryId() + '/' + self.id
          else:
            return self.id
        else:
          return my_parent.getCategoryRelativeUrl(base=base) + '/' + self.id
      else:
        if base:
          return self.getBaseCategoryId() + '/' + self.id
        else:
          return self.id


    # Alias for compatibility
    security.declareProtected(Permissions.AccessContentsInformation, 'getCategoryName')
    getCategoryName = getCategoryRelativeUrl

    # Predicate interface
    _operators = []

    def test(self, context):
      """
        A Predicate can be tested on a given context
      """
      return context.isMemberOf(self.getCategoryName())

    security.declareProtected( Permissions.AccessContentsInformation, 'asPythonExpression' )
    def asPythonExpression(self, strict_membership=0):
      """
        A Predicate can be rendered as a python expression. This
        is the preferred approach within Zope.
      """
      return "context.isMemberOf('%s')" % self.getCategoryRelativeUrl(base = 1)

    security.declareProtected( Permissions.AccessContentsInformation, 'asSqlExpression' )
    def asSqlExpression(self, strict_membership=0, table='category'):
      """
        A Predicate can be rendered as an sql expression. This
        can be useful to create reporting trees based on the
        ZSQLCatalog
      """
      #LOG('asSqlExpression', 0, str(self))
      #LOG('asSqlExpression parent', 0, str(self.aq_parent))
      if strict_membership:
        sql_text = '(%s.category_uid = %s AND %s.base_category_uid = %s AND %s.category_strict_membership = 1)' % (table, self.getUid(), table, self.getBaseCategoryUid(), table)
      else:
        sql_text = '(%s.category_uid = %s AND %s.base_category_uid = %s)' % (table, self.getUid(),
                                                                   table, self.getBaseCategoryUid())
      # Now useless since we precompute the mapping
      #for o in self.objectValues():
      #  sql_text += ' OR %s' % o.asSqlExpression()
      return sql_text

    # A Category's categories is self


    security.declareProtected( Permissions.AccessContentsInformation, 'getRelativeUrl' )
    def getRelativeUrl(self):
      """
        We must eliminate portal_categories in the RelativeUrl
        since it is never present in the category list
      """
      return '/'.join(self.portal_url.getRelativeContentPath(self)[1:])

    security.declareProtected( Permissions.View, 'isMemberOf' )
    def isMemberOf(self, category, strict = 0):
      """
        Tests if an object if member of a given category
        Category is a string here. It could be more than a string (ex. an object)
      """
      if strict:
        if self.getRelativeUrl().find(category) >= 0:
          if len(category) == len(self.getRelativeUrl()) + len(self.getRelativeUrl().find(category)):
            return 1
      else:
        if self.getRelativeUrl().find(category) >= 0:
          return 1
      return 0

    security.declareProtected( Permissions.AccessContentsInformation, 'getCategoryMemberValueList' )
    def getCategoryMemberValueList(self, base_category = None,
                            spec=(), filter=None, portal_type=(), strict = 0):
      """
      Returns a list of objects or brains
      """

      return self.portal_categories.getCategoryMemberValueList(self,
            base_category = base_category,
            spec=spec, filter=filter, portal_type=portal_type,strict = strict)

    security.declareProtected( Permissions.AccessContentsInformation, 'getCategoryMemberItemList' )
    def getCategoryMemberItemList(self, **kw):
      """
      Returns a list of objects or brains
      """
      return self.portal_categories.getCategoryMemberItemList(self, **kw)

    security.declareProtected( Permissions.AccessContentsInformation,
                                                               'getCategoryMemberTitleItemList' )
    def getCategoryMemberTitleItemList(self, **kw):
      """
      Returns a list of objects or brains
      """
      kw['display_id'] = 'getTitle'
      kw['display_method'] = None
      return self.portal_categories.getCategoryMemberItemList(self, **kw)

    security.declareProtected( Permissions.AccessContentsInformation, 'getBreadcrumbList' )
    def getBreadcrumbList(self):
      """
      Returns a list of objects or brains
      """
      title_list = []
      if not self.isBaseCategory:
        title_list.extend(self.aq_parent.getBreadcrumbList())
        title_list.append(self.getTitle())
      return title_list

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






class BaseCategory(Category):
    """
      Base Categories allow to implement virtual categories
      through acquisition
    """
    meta_type='CMF Base Category'
    portal_type='Base Category' # maybe useful some day
    isPortalContent = 1
    isRADContent = 1
    isBaseCategory = 1

    constructors =   (manage_addBaseCategoryForm, addBaseCategory)

    property_sheets = ( PropertySheet.Base
                      , PropertySheet.SimpleItem
                      , PropertySheet.BaseCategory)

    # Declarative security
    security = ClassSecurityInfo()

    def asSqlExpression(self, strict_membership=0, table='category'):
      """
        A Predicate can be rendered as an sql expression. This
        can be useful to create reporting trees based on the
        ZSQLCatalog
      """
      if strict_membership:
        sql_text = '(%s.category_uid = %s AND %s.base_category_uid = %s AND %s.category_strict_membership = 1)' % (table, self.uid, table, self.uid, table)
      else:
        sql_text = '(%s.category_uid = %s AND %s.base_category_uid = %s)' % (table, self.uid, table, self.uid)
      # Now useless since we precompute the mapping
      #for o in self.objectValues():
      #  sql_text += ' OR %s' % o.asSqlExpression()
      return sql_text

    security.declareProtected( Permissions.AccessContentsInformation, 'getBaseCategoryId' )
    def getBaseCategoryId(self):
      """
        The base category of this object
        acquired through portal categories. Very
        useful to implement relations and virtual categories.
      """
      return self.getBaseCategory().id

    security.declareProtected( Permissions.AccessContentsInformation, 'getBaseCategoryUid' )
    def getBaseCategoryUid(self):
      """
        The base category uid of this object
        acquired through portal categories. Very
        useful to implement relations and virtual categories.
      """
      return self.getBaseCategory().getUid()

    security.declareProtected( Permissions.AccessContentsInformation, 'getBaseCategoryValue' )
    def getBaseCategoryValue(self):
      """
        The base category of this object
        acquired through portal categories. Very
        useful to implement relations and virtual categories.
      """
      return self

    security.declareProtected(Permissions.AccessContentsInformation,
                                                    'getCategoryChildValueList')
    def getCategoryChildValueList(self, recursive=1, include_if_child=1):
      """
          List the child objects of this category and all its subcategories.

          recursive - if set to 1, list recursively

          include_if_child - if set to 1, then a category is listed even if
                      has childs. if set to 0, then don't list if child.
                      for example:
                        region/europe
                        region/europe/france
                        region/europe/germany
                        ...
                      becomes:
                        region/europe/france
                        region/europe/germany
                        ...

      """
      value_list = []
      if recursive:
        for c in self.objectValues(self.allowed_types):
          value_list.extend(c.getCategoryChildValueList(recursive = 1,indlude_if_child=include_if_child))
      else:
        for c in self.objectValues(self.allowed_types):
          if include_if_child:
            value_list.append(c)
          else:
            if len(c.objectValues(self.allowed_types))==0:
              value_list.append(c)
      return value_list

    # Alias for compatibility
    security.declareProtected( Permissions.AccessContentsInformation, 'getBaseCategory' )
    getBaseCategory = getBaseCategoryValue

InitializeClass( Category )
InitializeClass( BaseCategory )

