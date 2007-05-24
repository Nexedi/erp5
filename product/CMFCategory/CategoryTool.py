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

"""\
ERP portal_categories tool.
"""

from OFS.Folder import Folder
from Products.CMFCore.utils import UniqueObject
from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from Products.ERP5Type import Permissions
from Products.ERP5Type.Base import Base
from Products.ERP5Type.Cache import getReadOnlyTransactionCache
from Products.CMFCategory import _dtmldir
from Products.CMFCore.PortalFolder import ContentFilter
from Products.CMFCategory.Renderer import Renderer
from OFS.Traversable import NotFound

import re

from zLOG import LOG, PROBLEM

_marker = object()

class CategoryError( Exception ):
    pass

class CategoryTool( UniqueObject, Folder, Base ):
    """
      The CategoryTool object is the placeholder for all methods
      and algorithms related to categories and relations in CMF.

      The default category tool (this one) implements methods such
      as getCategoryMembershipList and setCategoryMembershipList
      which store categorymembership as a list of relative url in
      a property called categories.

      Category membership lists are ordered. For each base_category
      the first category membership in the category membership list is
      called the default category membership. For example, if a resource
      can be counted in meters, kilograms and cubic meters and if the
      default unit is meters, the category membership list for this resource
      from the quantity_unit point of view is::

        quantity_unit/length/meter
        quantity_unit/weight/kilogram
        quantity_unit/volume/m3

      Membership is ordered and multiple. For example, if a swim suit uses
      three colors (eg : color1, color2, color3 which are used in the top, belt
      and in the bottom) and if a particular variation of that swim suit has
      two of the three colors the same (eg black, blue, black) then the
      category membership list from the color point of view is::

        color/black
        color/blue
        color/black

        TODO: Add sort methods everywhere

        NB:
          All values are by default acquired
          Future accessors should provide non acquired values

        XX:
          Why is portal_categoires a subclass of Base ? Because of uid ?
          If yes, then it should be migrated into ERP5Category and __init__ indefined here
    """

    id              = 'portal_categories'
    meta_type       = 'CMF Categories'
    portal_type     = 'Category Tool'
    allowed_types = ( 'CMF Base Category', )


    # Declarative Security
    security = ClassSecurityInfo()

    #
    #   ZMI methods
    #
    manage_options = ( ( { 'label'      : 'Overview'
                         , 'action'     : 'manage_overview'
                         }
                        ,
                        )
                     + Folder.manage_options
                     )

    security.declareProtected( Permissions.ManagePortal
                             , 'manage_overview' )
    manage_overview = DTMLFile( 'explainCategoryTool', _dtmldir )


    # Multiple inheritance inconsistency caused by Base must be circumvented
    def __init__( self, *args, **kwargs ):
      Base.__init__(self, self.id, **kwargs)

    # Filter content (ZMI))
    def filtered_meta_types(self, user=None):
        # Filters the list of available meta types.
        all = CategoryTool.inheritedAttribute('filtered_meta_types')(self)
        meta_types = []
        for meta_type in self.all_meta_types():
            if meta_type['name'] in self.allowed_types:
                meta_types.append(meta_type)
        return meta_types

    # Filter Utilities
    def _buildFilter(self, spec, filter, kw):
      if filter is None:
        filt = {}
      else:
        # Work on a copy since we are going to modify it
        filt = filter.copy()
      if spec is not None: filt['meta_type'] = spec
      filt.update(kw)
      return filt

    def _buildQuery(self, spec, filter, kw):
      return apply( ContentFilter, (), self._buildFilter(spec, filter, kw) )

    # Category accessors
    security.declareProtected(Permissions.AccessContentsInformation, 'getBaseCategoryList')
    def getBaseCategoryList(self, context=None):
      """
        Returns the ids of base categories of the portal_categories tool
        if no context is provided, otherwise, returns the base categories
        defined for the class

        Two alias are provided :

        getBaseCategoryIds -- backward compatibility with early ERP5 versions

        baseCategoryIds -- for zope users conveniance
      """
      if context is None:
        return self.objectIds()
      else:
        return context._categories # XXX Incompatible with ERP5Type per portal type categories

    security.declareProtected(Permissions.AccessContentsInformation, 'getBaseCategoryIds')
    getBaseCategoryIds = getBaseCategoryList

    security.declareProtected(Permissions.AccessContentsInformation, 'baseCategoryIds')
    baseCategoryIds = getBaseCategoryIds

    security.declareProtected(Permissions.AccessContentsInformation, 'getBaseCategoryValueList')
    def getBaseCategoryValueList(self, context=None):
      """
        Returns the base categories of the portal_categories tool
        if no context is provided, otherwise returns the base categories
        for the class

        Two alias are provided :

        getBaseCategoryValues -- backward compatibility with early ERP5 versions

        baseCategoryValues -- for zope users conveniance
      """
      if context is None:
        return self.objectValues()
      else:
        return [self[x] for x in context._categories] # XXX Incompatible with ERP5Type per portal type categories

    security.declareProtected(Permissions.AccessContentsInformation,
                                                         'getBaseCategoryValues')
    getBaseCategoryValues = getBaseCategoryValueList

    security.declareProtected(Permissions.AccessContentsInformation, 'baseCategoryValues')
    baseCategoryValues = getBaseCategoryValues

    security.declareProtected(Permissions.AccessContentsInformation, 'getCategoryValue')
    def getCategoryValue(self, relative_url, base_category = None):
      """
        Returns a Category object from a given category url
        and optionnal base category id
      """
      cache = getReadOnlyTransactionCache(self)
      if cache is not None:
        key = ('getCategoryValue', relative_url, base_category)
        try:
          return cache[key]
        except KeyError:
          pass

      try:
        relative_url = str(relative_url)
        if base_category is not None:
          relative_url = '%s/%s' % (base_category, relative_url)
        node = self.unrestrictedTraverse(relative_url)
        value = node
      except (TypeError, KeyError, NotFound):
        value = None

      if cache is not None:
        cache[key] = value

      return value

#     security.declareProtected(Permissions.AccessContentsInformation, 'getCategoryValue')
#     def getCategoryValue(self, relative_url, base_category = None):
#       """
#         Returns a Category object from a given category url
#         and optionnal base category id
#       """
#       try:
#         relative_url = str(relative_url)
#         context = aq_base(self)
#         if base_category is not None:
#           context = context.unrestrictedTraverse(base_category)
#           context = aq_base(context)
#         node = context.unrestrictedTraverse(relative_url)
#         return node.__of__(self)
#       except:
#         return None

    security.declareProtected(Permissions.AccessContentsInformation, 'getCategoryUid')
    def getCategoryUid(self, relative_url, base_category = None):
      """
        Returns the uid of a Category from a given base category
        and the relative_url of a category
      """
      node = self.getCategoryValue(relative_url,  base_category = base_category)
      if node is not None:
        return node.uid
      else:
        return None

    security.declareProtected(Permissions.AccessContentsInformation, 'getCategoryValueFromUid')
    def getCategoryValueFromUid(self, uid):
      """
        Returns the a Category object from its uid by looking up in a
        a portal_catalog which must be ZSQLCataglog
      """
      return self.portal_catalog.getobject(uid)

    security.declareProtected(Permissions.AccessContentsInformation, 'getBaseCategoryId')
    def getBaseCategoryId(self, relative_url, base_category = None):
      """
        Returns the id of the base category from a given relative url
        and optional base category
      """
      if base_category is not None:
        return base_category
      try:
        return relative_url.split('/', 1)[0]
      except KeyError :
        return None

    security.declareProtected(Permissions.AccessContentsInformation, 'getBaseCategoryUid')
    def getBaseCategoryUid(self, relative_url, base_category = None):
      """
        Returns the uid of the base category from a given relative_url
        and optional base category
      """
      try:
        return self.getCategoryValue(self.getBaseCategoryId(relative_url,
                        base_category = base_category)).uid
      except (AttributeError, KeyError):
        return None

    security.declareProtected(Permissions.AccessContentsInformation, 'getCategoryParentUidList')
    def getCategoryParentUidList(self, relative_url, base_category = None, strict=0):
      """
        Returns the uids of all categories provided in categorie. This
        method can support relative_url such as site/group/a/b/c which
        base category is site yet use categories defined in group.

        It is also able to use acquisition to create complex categories
        such as site/group/a/b/c/b1/c1 where b and b1 are both children
        categories of a.

        relative_url -- a single relative url of a list of
                        relative urls

        strict       -- if set to 1, only return uids of parents, not
                        relative_url
      """
      uid_dict = {}
      if isinstance(relative_url, str):
        relative_url = (relative_url,)
      for path in relative_url:
        try:
          o = self.getCategoryValue(path, base_category=base_category)
          if o is not None:
            my_base_category = self.getBaseCategoryId(path)
            bo = self.get(my_base_category, None)
            if bo is not None:
              bo_uid = int(bo.getUid())
              uid_dict[(int(o.uid), bo_uid, 1)] = 1 # Strict Membership
              if o.meta_type == 'CMF Category' or o.meta_type == 'CMF Base Category':
                # This goes up in the category tree
                # XXX we should also go up in some other cases....
                # ie. when some documents act as categories
                if not strict:
                  while o.meta_type == 'CMF Category':
                    o = o.aq_parent # We want acquisition here without aq_inner
                    uid_dict[(int(o.uid), bo_uid, 0)] = 1 # Non Strict Membership
        except (KeyError, AttributeError):
          LOG('WARNING: CategoriesTool',0, 'Unable to find uid for %s' % path)
      return uid_dict.keys()

    security.declareProtected(Permissions.AccessContentsInformation, 'getUids')
    getUids = getCategoryParentUidList

    security.declareProtected(Permissions.AccessContentsInformation, 'getCategoryChildUidList')
    def getCategoryChildUidList(self, relative_url, base_category = None, strict=0):
      """
        Returns the uids of all categories provided in categories

        relative_url -- a single relative url of a list of
                        relative urls

        strict       -- if set to 1, only return uids of parents, not
                        relative_url
      """
      ## TBD

    # Recursive listing API
    security.declareProtected(Permissions.AccessContentsInformation,
                                                  'getCategoryChildRelativeUrlList')
    def getCategoryChildRelativeUrlList(self, base_category=None, base=0, recursive=1):
      """
      Returns a list of relative urls by parsing recursively all categories in a
      given list of base categories

      base_category -- A single base category id or a list of base category ids
                       if not provided, base category will be set with the list
                       of all current category ids

      base -- if set to 1, relative_url will start with the base category id
              if set to 0 and if base_category is a single id, relative_url
              are relative to the base_category (and thus  doesn't start
              with the base category id)

      recursive -- if set to 0 do not apply recursively
      """
      if base_category is None:
        base_category_list = self.getBaseCategoryList()
      elif isinstance(base_category, str):
        base_category_list = [base_category]
      else:
        base_category_list = base_category
      result = []
      for base_category in base_category_list:
        category = self[base_category]
        if category is not None:
          result.extend(category.getCategoryChildRelativeUrlList(base=base,recursive=recursive))
      return result

    security.declareProtected(Permissions.AccessContentsInformation, 'getPathList')
    getPathList = getCategoryChildRelativeUrlList # Exists for backward compatibility

    security.declareProtected(Permissions.AccessContentsInformation, 'getCategoryChildList')
    getCategoryChildList = getCategoryChildRelativeUrlList # This is more consistent

    security.declareProtected(Permissions.AccessContentsInformation,
                                                      'getCategoryChildTitleItemList')
    def getCategoryChildTitleItemList(self, base_category=None,
                                recursive=1, base=0, display_none_category=0, sort_id=None):
      """
      Returns a list of tuples by parsing recursively all categories in a
      given list of base categories. Uses getTitle as default method
      """
      return self.getCategoryChildItemList(base_category=base_category, recursive = recursive,base=base,
       display_none_category=display_none_category,display_id='getTitle', sort_id=sort_id)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getCategoryChildIdItemList')
    def getCategoryChildIdItemList(self, base_category=None,
              recursive=1, base=0, display_none_category=0, sort_id=None):
      """
      Returns a list of tuples by parsing recursively all categories in a
      given list of base categories. Uses getId as default method
      """
      return self.getCategoryChildItemList(
                          base_category=base_category,
                          recursive = recursive,
                          base=base,
                          display_none_category=display_none_category,
                          display_id='getId',
                          sort_id=sort_id )

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getCategoryChildItemList')
    def getCategoryChildItemList(self, base_category=None, display_id = None,
          recursive=1, base=0, display_none_category=1, sort_id=None, **kw):
      """
      Returns a list of tuples by parsing recursively all categories in a
      given list of base categories. Each tuple contains::

        (c.relative_url,c.display_id())

      base_category -- A single base category id or a list of base category ids
                       if not provided, base category will be set with the list
                       of all current category ids

      base -- if set to 1, relative_url will start with the base category id
              if set to 0 and if base_category is a single id, relative_url
              are relative to the base_category (and thus  doesn't start
              with the base category id)

      display_id -- method called to build the couple

      recursive -- if set to 0 do not apply recursively

      See Category.getCategoryChildItemList for extra accepted arguments
      """
      if isinstance(base_category, str):
        base_category_list = [base_category]
      elif base_category is None:
        base_category_list = self.getBaseCategoryList()
      else:
        base_category_list = base_category
      if display_none_category:
        result = [('', '')]
      else:
        result = []
      for base_category in base_category_list:
        category = self[base_category]
        if category is not None:
          result.extend(category.getCategoryChildItemList(
                               base=base,
                               recursive=recursive,
                               display_id=display_id,
                               **kw ))
      return result

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getBaseItemList')
    getBaseItemList = getCategoryChildItemList

    # Category to Tuple Conversion
    security.declareProtected(Permissions.View, 'asItemList')
    def asItemList(self, relative_url, base_category=None,**kw):
      """
      Returns a list of tuples, each tuple is calculated by applying
      display_id on each category provided in relative_url

      base_category -- A single base category id or a list of base category ids
                       if not provided, base category will be set with the list
                       of all current category ids

      base -- if set to 1, relative_url will start with the base category id
              if set to 0 and if base_category is a single id, relative_url
              are relative to the base_category (and thus  doesn't start
              with the base category id)

      display_id -- method called to build the couple

      recursive -- if set to 0 do not apply recursively
      """
      #if display_id is None:
      #  for c in relative_url:
      #    result += [(c, c)]
      #else:
#       LOG('CMFCategoryTool.asItemList, relative_url',0,relative_url)
      value_list = []
      for c in relative_url:
        o = self.getCategoryValue(c, base_category=base_category)
#         LOG('CMFCategoryTool.asItemList, (o,c)',0,(o,c))
        if o is not None:
          value_list.append(o)
        else:
          LOG('WARNING: CategoriesTool',0, 'Unable to find category %s' % c)

      #if sort_id is not None:
      #  result.sort()

#       LOG('CMFCategoryTool.asItemList, value_list',0,value_list)
      return Renderer(base_category=base_category,**kw).render(value_list)

    security.declareProtected(Permissions.View, 'getItemList')
    getItemList = asItemList

    # Convert a list of membership to path
    security.declareProtected(Permissions.View, 'asPathList')
    def asPathList(self, base_category, category_list):
      if isinstance(category_list, str):
        category_list = [category_list]
      if category_list is None:
        category_list = []
      new_list = []
      for v in category_list:
        new_list.append('%s/%s' % (base_category, v))
      return new_list

    # Alias for compatibility
    security.declareProtected(Permissions.View, 'formSelectionToPathList')
    formSelectionToPathList = asPathList


    # Category implementation
    security.declareProtected( Permissions.AccessContentsInformation,
                                                  'getCategoryMembershipList' )
    def getCategoryMembershipList(self, context, base_category, base=0,
                                  spec=(), filter=None, **kw  ):
      """
        Returns a list of category membership
        represented as a list of relative URLs

        context       --    the context on which we are looking for categories

        base_category --    a single base category (string) or a list of base categories

        spec          --    a list or a tuple of portal types

        base          --    if set to 1, returns relative URLs to portal_categories
                            if set to 0, returns relative URLs to the base category
      """
      # XXX We must use filters in the future
      # where_expression = self._buildQuery(spec, filter, kw)
      portal_type = kw.get('portal_type', ())
      if spec is (): spec = portal_type

      # LOG('getCategoryMembershipList',0,str(spec))
      # LOG('getCategoryMembershipList',0,str(base_category))
      membership = []
      if not isinstance(base_category, (tuple, list)):
        category_list = [base_category]
      else:
        category_list = base_category
      if not isinstance(spec, (tuple, list)):
        spec = [spec]
      for path in self._getCategoryList(context):
        # LOG('getCategoryMembershipList',0,str(path))
        my_base_category = path.split('/', 1)[0]
        for my_category in category_list:
          if isinstance(my_category, str):
            category = my_category
          else:
            category = my_category.getRelativeUrl()
          if my_base_category == category:
            if spec is ():
              if base:
                membership.append(path)
              else:
                membership.append(path[len(category)+1:])
            else:
              try:
               o = self.unrestrictedTraverse(path)
               # LOG('getCategoryMembershipList',0,str(o.portal_type))
               if o.portal_type in spec:
                if base:
                  membership.append(path)
                else:
                  membership.append(path[len(category)+1:])
              except KeyError:
                LOG('WARNING: CategoriesTool',0, 'Unable to find object for path %s' % path)
      # We must include parent if specified explicitely
      if 'parent' in category_list:
        parent = context.aq_parent
        if parent.portal_type in spec:
          if base:
            membership.append('parent/' + parent.getRelativeUrl())
          else:
            membership.append(parent.getRelativeUrl())
      return membership

    security.declareProtected( Permissions.AccessContentsInformation, 'setCategoryMembership' )
    def setCategoryMembership(self, context, base_category_list, category_list, base=0, keep_default=1,
                                 spec=(), filter=None, **kw ):
      """
        Sets the membership of the context on the specified base_category
        list and for the specified portal_type spec

        context            --    the context on which we are looking for categories

        base_category_list --    a single base category (string) or a list of base categories
                                 or a single base category object or a list of base category objects

        category_list      --    a single category (string) or a list of categories

        spec               --    a list or a tuple of portal types

      """
      #LOG("set Category 1",0,str(category_list))
      # XXX We must use filters in the future
      # where_expression = self._buildQuery(spec, filter, kw)
      portal_type = kw.get('portal_type', ())
      if isinstance(portal_type, str):
        portal_type = (portal_type,)
      if spec is ():
        spec = portal_type
      default_dict = {}
      self._cleanupCategories(context)
      if isinstance(category_list, str):
        category_list = (category_list,)
      elif category_list is None:
        category_list = ()
      elif isinstance(category_list, (list, tuple)):
        pass
      else:
        raise TypeError, 'Category must be of string, tuple of string or list of string type.'
      if isinstance(base_category_list, str):
        base_category_list = [base_category_list]
      new_category_list = []
      for path in self._getCategoryList(context):
        my_base_id = self.getBaseCategoryId(path)
        if my_base_id not in base_category_list:
          # Keep each membership which is not in the
          # specified list of base_category ids
          new_category_list.append(path)
        else:
          if spec is ():
            # If spec is (), then we should keep nothing
            # Everything will be replaced
            keep_it = 0
          else:
            # Only keep this if not in our spec
            try:
              my_type = self.unrestrictedTraverse(path).portal_type
              keep_it = (my_type not in spec)
            except (KeyError, AttributeError):
              keep_it = 0
          if keep_it:
            new_category_list.append(path)
          elif keep_default:
            # We must remember the default value
            # for each replaced category
            if not default_dict.has_key(my_base_id):
              default_dict[my_base_id] = path
      # We now create a list of default category values
      default_new_category_list = []
      for path in default_dict.values():
        if base or len(base_category_list) > 1:
          if path in category_list:
            default_new_category_list.append(path)
        else:
          if path[len(base_category_list[0])+1:] in category_list:
            default_new_category_list.append(path)
      # Before we append new category values (except default values)
      # We must make sure however that multiple links are possible
      default_path_found = {}
      for path in category_list:
        if path != '':
          if base or len(base_category_list) > 1:
            # Only keep path which are member of base_category_list
            if self.getBaseCategoryId(path) in base_category_list:
              if path not in default_new_category_list or default_path_found.has_key(path):
                default_path_found[path] = 1
                new_category_list.append(path)
          else:
            new_path = base_category_list[0] + '/' + path
            if new_path not in default_new_category_list:
              new_category_list.append(new_path)
      #LOG("set Category",0,str(new_category_list))
      #LOG("set Category",0,str(default_new_category_list))
      self._setCategoryList(context, tuple(default_new_category_list + new_category_list))

    security.declareProtected( Permissions.AccessContentsInformation, 'setDefaultCategoryMembership' )
    def setDefaultCategoryMembership(self, context, base_category, default_category,
                                              spec=(), filter=None, portal_type=(), base=0 ):
      """
        Sets the membership of the context on the specified base_category
        list and for the specified portal_type spec

        context            --    the context on which we are looking for categories

        base_category_list --    a single base category (string) or a list of base categories
                                 or a single base category object or a list of base category objects

        category_list      --    a single category (string) or a list of categories

        spec               --    a list or a tuple of portal types

      """
      self._cleanupCategories(context)
      if isinstance(default_category, (tuple, list)):
        default_category = default_category[0]
      category_list = self.getCategoryMembershipList(context, base_category,
                           spec=spec, filter=filter, portal_type=portal_type, base=base)
      new_category_list = [default_category]
      found_one = 0
      # We will keep from the current category_list
      # everything except the first occurence of category
      # this allows to have multiple occurences of the same category
      for category in category_list:
        if category == default_category:
          found_one = 1
        elif category != default_category or found_one:
          new_category_list.append(category)
      self.setCategoryMembership(context, base_category, new_category_list,
           spec=spec, filter=filter, portal_type=portal_type, base=base, keep_default = 0)

    security.declareProtected( Permissions.AccessContentsInformation,
                                                        'getSingleCategoryMembershipList' )
    def getSingleCategoryMembershipList(self, context, base_category, base=0,
                                          spec=(), filter=None, **kw):
      """
        Returns the local membership of the context for a single base category
        represented as a list of relative URLs

        context       --    the context on which we are looking for categories

        base_category --    a single base category (string)

        spec          --    a list or a tuple of portal types

        base          --    if set to 1, returns relative URLs to portal_categories
                            if set to 0, returns relative URLs to the base category
      """
      # XXX We must use filters in the future
      # where_expression = self._buildQuery(spec, filter, kw)
      portal_type = kw.get('portal_type', ())
      if spec is (): spec = portal_type

      # We must treat parent in a different way
      #LOG('getSingleCategoryMembershipList', 0, 'base_category = %s, spec = %s, base = %s, context = %s, context.aq_inner.aq_parent = %s' % (repr(base_category), repr(spec), repr(base), repr(context), repr(context.aq_inner.aq_parent)))
      if base_category == 'parent':
        parent = context.aq_inner.aq_parent # aq_inner is required to make sure we use containment
        if parent.portal_type in spec:
          if base:
            return ['parent/' + parent.getRelativeUrl()]
          else:
            return [parent.getRelativeUrl()]
        #LOG('getSingleCategoryMembershipList', 0, 'not in spec: parent.portal_type = %s, spec = %s' % (repr(parent.portal_type), repr(spec)))
        return []

      result = []
      append = result.append
      # XXX We must use filters in the future
      # where_expression = self._buildQuery(spec, filter, kw)
      spec = kw.get('portal_type', ())
      # Make sure spec is a list or tuple
      if isinstance(spec, str):
        spec = [spec]
      # Filter categories
      if getattr(aq_base(context), 'categories', _marker) is not _marker:
        for category_url in self._getCategoryList(context):
          try:
            index = category_url.index('/')
            my_base_category = category_url[:index]
          except ValueError:
            my_base_category = category_url
          if my_base_category == base_category:
            #LOG("getSingleCategoryMembershipList",0,"%s %s %s %s" % (context.getRelativeUrl(),
            #                  my_base_category, base_category, category_url))
            if spec is ():
              if base:
                append(category_url)
              else:
                append(category_url[len(my_base_category)+1:])
            else:
              my_reference = self.unrestrictedTraverse(category_url, None)
              if my_reference is not None:
                if my_reference.portal_type in spec:
                  if base:
                    append(category_url)
                  else:
                    append(category_url[len(my_base_category)+1:])
      return result

    security.declareProtected( Permissions.AccessContentsInformation,
                                      'getSingleCategoryAcquiredMembershipList' )
    def getSingleCategoryAcquiredMembershipList(self, context, base_category, base=0,
                                         spec=(), filter=None, acquired_object_dict = None, **kw ):
      cache = getReadOnlyTransactionCache(self)
      if cache is not None:
        key = ('getSingleCategoryAcquiredMembershipList', context._p_oid, base_category, base, spec,
               filter, str(kw))
        try:
          return cache[key]
        except KeyError:
          pass

      result = self._getSingleCategoryAcquiredMembershipList(context, base_category, base=base,
                                                             spec=spec, filter=filter,
                                                             acquired_object_dict = acquired_object_dict,
                                                             **kw)
      if cache is not None:
        cache[key] = result

      return result


    def _getSingleCategoryAcquiredMembershipList(self, context, base_category,
                                         base = 0, spec = (), filter = None,
                                         acquired_portal_type = (),
                                         acquired_object_dict = None,
                                         **kw ):
      """
        Returns the acquired membership of the context for a single base category
        represented as a list of relative URLs

        context       --    the context on which we are looking for categories

        base_category --    a single base category (string)

        spec          --    a list or a tuple of portal types

        base          --    if set to 1, returns relative URLs to portal_categories
                            if set to 0, returns relative URLs to the base category

        acquired_object_dict      --    this is the list of object used by acquisition, so
                                        we can check if we already have used this object

        alt_base_category         --    an alternative base category if the first one fails

        acquisition_copy_value    --    if set to 1, the looked up value will be copied
                            as an attribute of self

        acquisition_mask_value    --    if set to 1, the value of the category of self
                            has priority on the looked up value

        acquisition_sync_value    --    if set to 1, keep self and looked up value in sync

      """
      #LOG("Get Acquired Category ",0,str((base_category, context,)))
      #LOG("Get Acquired Category acquired_object_dict: ",0,str(acquired_object_dict))
      # XXX We must use filters in the future
      # where_expression = self._buildQuery(spec, filter, kw)

      portal_type = kw.get('portal_type', ())
      if spec is (): spec = portal_type # This is bad XXX - JPS - spec is for meta_type, not for portal_type - be consistent !

      if isinstance(spec, str):
        spec = [spec]

      if isinstance(acquired_portal_type, str):
        acquired_portal_type = [acquired_portal_type]

      if acquired_object_dict is None:
        acquired_object_dict = {} # Initial call may include filter, etc. - do not keep
      else:
        context_base_key = (tuple(context.getPhysicalPath()), base_category)
        if context_base_key in acquired_object_dict:
          acquired_object_dict = acquired_object_dict.copy()
          type_dict = acquired_object_dict[context_base_key].copy()
          if spec is ():
            if () in type_dict:
              return []
            else:
              type_dict[()] = 1
          else:
            for pt in spec:
              if pt in type_dict:
                return []
              else:
                type_dict[pt] = 1
          acquired_object_dict[context_base_key] = type_dict
        else:
          type_dict = {}
          if spec is ():
            type_dict[()] = 1
          else:
            for pt in spec:
              type_dict[pt] = 1
          acquired_object_dict = acquired_object_dict.copy()
          acquired_object_dict[context_base_key] = type_dict

      result = self.getSingleCategoryMembershipList( context, base_category, base=base,
                            spec=spec, filter=filter, **kw ) # Not acquired because this is the first try
                                                             # to get a local defined category

      base_category_value = self.getCategoryValue(base_category)
      #LOG("result", 0, str(result))
      if base_category_value is not None:
        # If we do not mask or append, return now if not empty
        if base_category_value.getAcquisitionMaskValue() and \
                not base_category_value.getAcquisitionAppendValue() and \
                len(result) > 0:
          # If acquisition masks and we do not append values, then we must return now
          return result
        # First we look at local ids
        for object_id in base_category_value.getAcquisitionObjectIdList():
          my_acquisition_object = None
          if object_id in context.objectIds():
            my_acquisition_object = getattr(context, object_id)
          if my_acquisition_object is not None:
            #my_acquisition_object_path = my_acquisition_object.getPhysicalPath()
            #if my_acquisition_object_path in acquired_object_dict:
            #  continue
            #acquired_object_dict[my_acquisition_object_path] = 1
            if my_acquisition_object.portal_type in base_category_value.getAcquisitionPortalTypeList():
              new_result = self.getSingleCategoryAcquiredMembershipList(my_acquisition_object,
                  base_category, spec=spec, filter=filter, portal_type=portal_type, base=base, acquired_object_dict=acquired_object_dict)
            else:
              new_result = []
            #if base_category_value.acquisition_mask_value:
            #  # If acquisition masks, then we must return now
            #  return new_result
            if getattr(base_category_value, 'acquisition_append_value', False):
              # If acquisition appends, then we must append to the result
              result.extend(new_result)
            elif len(new_result) > 0:
              return new_result # Found enough information to return
        # Next we look at references
        #LOG("Get Acquired BC", 0, base_category_value.getAcquisitionBaseCategoryList())
        acquisition_base_category_list = base_category_value.getAcquisitionBaseCategoryList()
        alt_base_category_list = base_category_value.getFallbackBaseCategoryList()
        all_acquisition_base_category_list = acquisition_base_category_list + alt_base_category_list
        acquisition_pt = base_category_value.getAcquisitionPortalTypeList(())
        for my_base_category in base_category_value.getAcquisitionBaseCategoryList():
          # We implement here special keywords
          if my_base_category == 'parent':
            parent = context.aq_inner.aq_parent # aq_inner is required to make sure we use containment
            if getattr(aq_base(parent), 'portal_type', _marker) is _marker:
              my_acquisition_object_list = []
            else:
              #LOG("Parent Object List ",0,str(parent.getRelativeUrl()))
              #LOG("Parent Object List ",0,str(parent.portal_type))
              #LOG("Parent Object List ",0,str(acquisition_pt))
              #my_acquisition_object_path = parent.getPhysicalPath()
              #if my_acquisition_object_path in acquired_object_dict:
              if acquisition_pt is () or parent.portal_type in acquisition_pt:
                my_acquisition_object_list = [parent]
              else:
                my_acquisition_object_list = []
          else:
            #LOG('getAcquiredCategoryMembershipList', 0, 'my_acquisition_object = %s, acquired_object_dict = %s' % (str(context), str(acquired_object_dict)))
            my_acquisition_list = self.getSingleCategoryAcquiredMembershipList(context,
                        my_base_category,
                        portal_type=tuple(base_category_value.getAcquisitionPortalTypeList(())),
                        acquired_object_dict=acquired_object_dict)
            my_acquisition_object_list = []
            for c in my_acquisition_list:
              o = self.resolveCategory(c)
              if o is not None:
                my_acquisition_object_list.append(o)
            #my_acquisition_object_list = context.getValueList(my_base_category,
            #                       portal_type=tuple(base_category_value.getAcquisitionPortalTypeList(())))
          #LOG("Get Acquired PT",0,str(base_category_value.getAcquisitionPortalTypeList(())))
          #LOG("Object List ",0,str(my_acquisition_object_list))
          original_result = result
          result = list(result) # make a copy
          for my_acquisition_object in my_acquisition_object_list:
            #LOG('getSingleCategoryAcquiredMembershipList', 0, 'my_acquisition_object = %s, acquired_object_dict = %s' % (str(my_acquisition_object), str(acquired_object_dict)))
            #LOG('getSingleCategoryAcquiredMembershipList', 0, 'my_acquisition_object.__dict__ = %s' % str(my_acquisition_object.__dict__))
            #LOG('getSingleCategoryAcquiredMembershipList', 0, 'my_acquisition_object.__hash__ = %s' % str(my_acquisition_object.__hash__()))
            #if my_acquisition_object is not None:
            if my_acquisition_object is not None:
              #my_acquisition_object_path = my_acquisition_object.getPhysicalPath()
              #if my_acquisition_object_path in acquired_object_dict:
              #  continue
              #acquired_object_dict[my_acquisition_object_path] = 1
              #if hasattr(my_acquisition_object, '_categories'): # This would be a bug since we have category acquisition
                # We should only consider objects which define that category
                #LOG('my_acquisition_object',0, str(getattr(my_acquisition_object, '_categories', ())))
                #LOG('my_acquisition_object',0, str(base_category))
                if base_category in getattr(my_acquisition_object, '_categories', ()):
                  if (not acquired_portal_type) or my_acquisition_object.portal_type in acquired_portal_type:
                    #LOG("Recursive call ",0,str((spec, my_acquisition_object.portal_type)))
                    new_result = self.getSingleCategoryAcquiredMembershipList(my_acquisition_object,
                        base_category, spec=spec, filter=filter, portal_type=portal_type, base=base,
                        acquired_portal_type=acquired_portal_type,
                        acquired_object_dict=acquired_object_dict)
                  else:
                    #LOG("No recursive call ",0,str((spec, my_acquisition_object.portal_type)))
                    new_result = []
                  if getattr(base_category_value, 'acquisition_append_value', False):
                    # If acquisition appends, then we must append to the result
                    result.extend(new_result)
                  elif len(new_result) > 0:
                    #LOG("new_result ",0,str(new_result))
                    if (getattr(base_category_value, 'acquisition_copy_value', False) and len(original_result) == 0) \
                                                    or getattr(base_category_value, 'acquisition_sync_value', False):
                      # If copy is set and result was empty, then copy it once
                      # If sync is set, then copy it again
                      self.setCategoryMembership( context, base_category, new_result,
                                    spec=spec, filter=filter, portal_type=portal_type, base=base )
                    # We found it, we can return
                    return new_result


          if (getattr(base_category_value, 'acquisition_copy_value', False) or \
              getattr(base_category_value, 'acquisition_sync_value', False))\
              and len(result) > 0:
            # If copy is set and result was empty, then copy it once
            # If sync is set, then copy it again
            self.setCategoryMembership( context, base_category, result,
                                         spec=spec, filter=filter, portal_type=portal_type, base=base )
        if len(result)==0 and len(base_category_value.getFallbackBaseCategoryList())>0:
          # We must then try to use the alt base category
          for base_category in base_category_value.getFallbackBaseCategoryList():
            # First get the category list
            category_list = self.getSingleCategoryAcquiredMembershipList( context, base_category, base=1,
                                 spec=spec, filter=filter, acquired_object_dict=acquired_object_dict, **kw )
            # Then convert it into value
            category_value_list = [self.resolveCategory(x) for x in category_list]
            # Then build the alternate category
            if base:
              base_category_id = base_category_value.getId()
              for category_value in category_value_list:
                if category_value is None :
                  message = "category does not exists for %s (%s)"%(
                                       context.getPath(), category_list)
                  LOG('CMFCategory', PROBLEM, message)
                  raise CategoryError (message)
                else :
                  result.append('%s/%s' % (base_category_id, category_value.getRelativeUrl()))
            else :
              for category_value in category_value_list:
                if category_value is None :
                  message = "category does not exists for %s (%s)"%(
                                       context.getPath(), category_list)
                  LOG('CMFCategory', PROBLEM, message)
                  raise CategoryError (message)
                else :
                  result.append(category_value.getRelativeUrl())
      # WE MUST IMPLEMENT HERE THE REST OF THE SEMANTICS
      #LOG("Get Acquired Category Result ",0,str(result))
      return result

    security.declareProtected( Permissions.AccessContentsInformation,
                                               'getAcquiredCategoryMembershipList' )
    def getAcquiredCategoryMembershipList(self, context, base_category = None, base=1,
                                          spec=(), filter=None, acquired_object_dict=None, **kw):
      """
        Returns all acquired category values
      """
      #LOG("Get Acquired Category List", 0, "%s %s" % (base_category, context.getRelativeUrl()))
      result = []
      extend = result.extend
      if base_category is None:
        base_category_list = context._categories # XXX incompatible with ERP5Type per portal categories
      elif isinstance(base_category, str):
        base_category_list = [base_category]
      else:
        base_category_list = base_category
      #LOG('CT.getAcquiredCategoryMembershipList base_category_list',0,base_category_list)
      getSingleCategoryAcquiredMembershipList = self.getSingleCategoryAcquiredMembershipList
      for base_category in base_category_list:
        extend(getSingleCategoryAcquiredMembershipList(context, base_category, base=base,
                                    spec=spec, filter=filter, acquired_object_dict=acquired_object_dict, **kw ))
        #LOG('CT.getAcquiredCategoryMembershipList new result',0,result)
      return result

    security.declareProtected( Permissions.AccessContentsInformation, 'isMemberOf' )
    def isMemberOf(self, context, category, **kw):
      """
        Tests if an object if member of a given category
        Category is a string here. It could be more than a string (ex. an object)

        Keywords parameters :
         - strict_membership:  if we want strict membership checking
         - strict : alias for strict_membership (deprecated but still here for
                    skins backward compatibility. )

        XXX - there should be 2 different methods, one which acuiqred
        and the other which does not. A complete review of
        the use of isMemberOf is required
      """
      strict_membership = kw.get('strict_membership', kw.get('strict', 0))
      if getattr(aq_base(context), 'isCategory', 0) :
        if context.isMemberOf(category, strict_membership = strict_membership) == 1 :
          return 1
      base_category = category.split('/')[0] # Extract base_category for optimisation
      if strict_membership:
        for c in self.getAcquiredCategoryMembershipList(context, base_category = base_category):
          if c == category:
            return 1
      else:
        for c in self.getAcquiredCategoryMembershipList(context, base_category = base_category):
          if c.find(category) == 0:
            # The names begin with the same string
            c_right_split = c.split(category)[1]
            if (len(c_right_split) > 0):
              # Be sure that we have a sub category, and not name like this: 'europe1' in 'europe10'
              if c_right_split[0] == '/':
                return 1
            else:
              # Same category
              return 1
      return 0

    security.declareProtected( Permissions.AccessContentsInformation, 'isAcquiredMemberOf' )
    def isAcquiredMemberOf(self, context, category, strict=0):
      """
        Tests if an object if member of a given category
        Category is a string here. It could be more than a string (ex. an object)
      """
      if getattr(aq_base(context), 'isCategory', 0):
        return context.isAcquiredMemberOf(category)
      if strict:
        for c in self._getAcquiredCategoryList(context):
          if c == category:
            return 1
      else:
        for c in self._getAcquiredCategoryList(context):
          if c.find(category) >= 0:
            return 1
      return 0

    security.declareProtected( Permissions.AccessContentsInformation, 'isAcquiredMemberOf' )
    def isAcquiredMemberOf(self, context, category):
      """
        Tests if an object if member of a given category
        Category is a string here. It could be more than a string (ex. an object)

        XXX Should include acquisition ?
      """
      if getattr(aq_base(context), 'isCategory', 0):
        return context.isAcquiredMemberOf(category)
      for c in self._getAcquiredCategoryList(context):
        if c.find(category) >= 0:
          return 1
      return 0

    security.declareProtected( Permissions.AccessContentsInformation, 'isAcquiredMemberOf' )
    def isAcquiredMemberOf(self, context, category):
      """
        Tests if an object if member of a given category
        Category is a string here. It could be more than a string (ex. an object)

        XXX Should include acquisition ?
      """
      if getattr(aq_base(context), 'isCategory', 0):
        return context.isAcquiredMemberOf(category)
      for c in self._getAcquiredCategoryList(context):
        if c.find(category) >= 0:
          return 1
      return 0

    security.declareProtected( Permissions.AccessContentsInformation, 'getCategoryList' )
    def getCategoryList(self, context):
      self._cleanupCategories(context)
      return self._getCategoryList(context)

    security.declareProtected( Permissions.AccessContentsInformation, '_getCategoryList' )
    def _getCategoryList(self, context):
      if getattr(aq_base(context), 'categories', _marker) is not _marker:
        if isinstance(context.categories, tuple):
          result = list(context.categories)
        elif isinstance(context.categories, list):
          result = context.categories
        else:
          result = []
      elif isinstance(context, dict):
        result = list(context.get('categories', []))
      else:
        result = []
      if getattr(context, 'isCategory', 0):
        category_url = context.getRelativeUrl()
        if category_url not in result:
          result.append(context.getRelativeUrl()) # Pure category is member of itself
      return result

    security.declareProtected( Permissions.ModifyPortalContent, '_setCategoryList' )
    def _setCategoryList(self, context, value):
       context.categories = tuple(value)

    security.declareProtected( Permissions.AccessContentsInformation, 'getAcquiredCategoryList' )
    def getAcquiredCategoryList(self, context):
      """
        Returns the list of acquired categories
      """
      self._cleanupCategories(context)
      return self._getAcquiredCategoryList(context)

    security.declareProtected( Permissions.AccessContentsInformation, '_getAcquiredCategoryList' )
    def _getAcquiredCategoryList(self, context):
      result = self.getAcquiredCategoryMembershipList(context,
                     base_category = self.getBaseCategoryList(context=context))
      append = result.append
      non_acquired = self._getCategoryList(context)
      for c in non_acquired:
        # Make sure all local categories are considered
        if c not in result:
          append(c)
      if getattr(context, 'isCategory', 0):
        append(context.getRelativeUrl()) # Pure category is member of itself
      return result

    security.declareProtected( Permissions.ModifyPortalContent, '_cleanupCategories' )
    def _cleanupCategories(self, context):
      # Make sure _cleanupCategories does not modify objects each time it is called
      # or we get many conflicts
      requires_update = 0
      categories = []
      append = categories.append
      if getattr(context, 'categories', _marker) is not _marker:
        for cat in self._getCategoryList(context):
          if isinstance(cat, str):
            append(cat)
          else:
            requires_update = 1
      if requires_update: self._setCategoryList(context, tuple(categories))

    # Catalog related methods
    def updateRelatedCategory(self, category, previous_category_url, new_category_url):
      new_category = re.sub('^%s$' %
            previous_category_url,'%s' % new_category_url,category)
      new_category = re.sub('^%s/(?P<stop>.*)' %
            previous_category_url,'%s/\g<stop>' % new_category_url,new_category)
      new_category = re.sub('(?P<start>.*)/%s/(?P<stop>.*)' %
            previous_category_url,'\g<start>/%s/\g<stop>' % new_category_url,new_category)
      new_category = re.sub('(?P<start>.*)/%s$' %
            previous_category_url,'\g<start>/%s' % new_category_url, new_category)
      return new_category

    def updateRelatedContent(self, context,
                             previous_category_url, new_category_url):
      """Updates related object when an object have moved.

          o context: the moved object
          o previous_category_url: the related url of this object before
            the move
          o new_category_url: the related url of the object after the move

      TODO: make this method resist to very large updates (ie. long transaction)
      """
      for brain in self.Base_zSearchRelatedObjectsByCategory(
                                              category_uid = context.getUid()):
        o = brain.getObject()
        if o is not None:
          category_list = []
          for category in self.getCategoryList(o):
            new_category = self.updateRelatedCategory(category,
                                                      previous_category_url,
                                                      new_category_url)
            category_list.append(new_category)
          self._setCategoryList(o, category_list)

          if getattr(aq_base(o),
                    'notifyAfterUpdateRelatedContent', None) is not None:
            o.notifyAfterUpdateRelatedContent(previous_category_url,
                                              new_category_url)

        else:
          LOG('CMFCategory', PROBLEM,
              'updateRelatedContent: %s does not exist' % brain.path)

      aq_context = aq_base(context)
      # Update related recursively if required
      if getattr(aq_context, 'listFolderContents', None) is not None:
        for o in context.listFolderContents():
          new_o_category_url = o.getRelativeUrl()
          # Relative Url is based on parent new_category_url so we must
          # replace new_category_url with previous_category_url to find
          # the new category_url for the subobject
          previous_o_category_url = self.updateRelatedCategory(
                                                   new_o_category_url,
                                                   new_category_url,
                                                   previous_category_url)

          self.updateRelatedContent(o, previous_o_category_url,
                                    new_o_category_url)

    security.declareProtected( Permissions.AccessContentsInformation,
                               'getRelatedValueList' )
    def getRelatedValueList(self, context, base_category_list=None,
                            spec=(), filter=None, base=1, 
                            checked_permission=None, **kw):
      """
        This methods returns the list of objects related to the context
        with the given base_category_list.
      """
      strict_membership = kw.get('strict_membership', kw.get('strict', 0))
      portal_type = kw.get('portal_type')

      if isinstance(portal_type, str):
        portal_type = [portal_type]
      if spec is (): 
        # We do not want to care about spec
        spec = None

      # Base Category may not be related, besides sub categories
      if context.getPortalType() == 'Base Category':
        category_list = [context.getRelativeUrl()]
      else:
        if isinstance(base_category_list, str):
          base_category_list = [base_category_list]
        elif base_category_list is () or base_category_list is None:
          base_category_list = self.getBaseCategoryList()
        category_list = []
        for base_category in base_category_list:
          category_list.append("%s/%s" % (base_category, context.getRelativeUrl()))

      brain_result = self.Base_zSearchRelatedObjectsByCategoryList(
                           category_list=category_list,
                           portal_type=portal_type,
                           strict_membership=strict_membership)

      result = []
      if checked_permission is None:
        # No permission to check
        for b in brain_result:
          o = b.getObject()
          if o is not None:
            result.append(o)
      else:
        # Check permissions on object
        if isinstance(checked_permission, str):
          checked_permission = (checked_permission, )
          checkPermission = self.portal_membership.checkPermission
          for b in brain_result:
            obj = b.getObject()
            if obj is not None:
              for permission in checked_permission:
                if not checkPermission(permission, obj):
                  break
                result.append(obj)

      return result
      # XXX missing filter and **kw stuff
      #return self.search_category(category_list=category_list,
      #                            portal_type=spec)
      # future implementation with brains, much more efficient

    security.declareProtected( Permissions.AccessContentsInformation,
                               'getRelatedPropertyList' )
    def getRelatedPropertyList(self, context, base_category_list=None,
                               property_name=None, spec=(), 
                               filter=None, base=1, 
                               checked_permission=None, **kw):
      """
        This methods returns the list of property_name on  objects
        related to the context with the given base_category_list.
      """
      result = []
      for o in self.getRelatedValueList(
                          context=context,
                          base_category_list=base_category_list, spec=spec,
                          filter=filter, base=base, 
                          checked_permission=checked_permission, **kw):
        result.append(o.getProperty(property_name, None))
      return result

    # SQL Expression Building
    security.declareProtected(Permissions.AccessContentsInformation, 'buildSQLSelector')
    def buildSQLSelector(self, category_list, query_table='category'):
      """
        Returns an SQL selector expression from a list of categories
        We make here a simple method wich simply checks membership
        This is like an OR. More complex selections (AND of OR) will require
        to generate a much more complex where_expression with table aliases

        List of lists
      """
      if isinstance(category_list, str):
        category_list = [category_list]
      sql_expr = []
      for category in category_list:
        if category is None:
          pass
        elif isinstance(category, str):
          if category:
            category_uid = self.getCategoryUid(category)
            base_category_uid = self.getBaseCategoryUid(category)
            expression = ''
            if category_uid is None:
              expression += '%s.category_uid is NULL' % query_table
            else:
              expression += '%s.category_uid = %s' % (query_table,category_uid)
            if base_category_uid is None:
              expression += ' AND %s.base_category_uid is NULL' % query_table
            else:
              expression += ' AND %s.base_category_uid = %s' % (query_table,base_category_uid)
            sql_expr += ["(%s)" % expression]
        else:
          single_sql_expr = []
          for single_category in category:
            if single_sql_expr != '':
              category_uid = self.getCategoryUid(single_category)
              base_category_uid = self.getBaseCategoryUid(single_category)
              if category_uid is None:
                expression += '%s.category_uid is NULL' % query_table
              else:
                expression += '%s.category_uid = %s' % (query_table,category_uid)
              if base_category_uid is None:
                expression += ' AND %s.base_category_uid is NULL' % query_table
              else:
                expression += ' AND %s.base_category_uid = %s' % (query_table,base_category_uid)
              single_sql_expr += ["(%s)" % expression]
          if len(single_sql_expr) > 0:
            sql_expr += "( %s )" % ' OR '.join(single_sql_expr)
      if len(sql_expr) > 0:
        sql_expr = ' OR '.join(sql_expr)
      return sql_expr

    security.declareProtected( Permissions.AccessContentsInformation, 'getCategoryMemberValueList' )
    def getCategoryMemberValueList(self, context, base_category = None,
                                         spec = (), filter=None, portal_type=(), **kw):
      """
      This returns a catalog_search resource with can then be used by getCategoryMemberItemList
      """
      if base_category is None:
        if context.getPortalType() in ( "Base Category", "Category") :
          base_category = context.getBaseCategoryId()
        else:
          raise CategoryError('getCategoryMemberValueList must know the base category')
      strict_membership = kw.get('strict_membership', kw.get('strict', 0))

      domain_dict = {base_category: ('portal_categories', context.getRelativeUrl())}
      if strict_membership:
        catalog_search = self.portal_catalog(portal_type = portal_type,
                           selection_report = domain_dict)
      else:
        catalog_search = self.portal_catalog(portal_type = portal_type,
                           selection_domain = domain_dict)

      return catalog_search

    security.declareProtected( Permissions.AccessContentsInformation, 'getCategoryMemberItemList' )
    def getCategoryMemberItemList(self, context, **kw):
      """
      This returns a list of items belonging to a category.
      The following parameters are accepted :
        portal_type       : returns only objects from the given portal_type
        strict_membership : returns only object belonging to this category, not
                            objects belonging to child categories.
        strict            : a deprecated alias for strict_membership
      """
      k = {}
      for v in ('portal_type', 'spec', 'strict', 'strict_membership'):
        if v in kw:
          k[v] = kw[v]
      catalog_search = self.getCategoryMemberValueList(context, **k)
      return Renderer(**kw).render(catalog_search)

    security.declareProtected( Permissions.AccessContentsInformation,
                                                                'getCategoryMemberTitleItemList' )
    def getCategoryMemberTitleItemList(self, context, base_category = None,
                                      spec = (), filter=None, portal_type=(), strict_membership = 0,
                                      strict="DEPRECATED"):
      """
      This returns a title list of items belonging to a category

      """
      return self.getCategoryMemberItemList(self, context, base_category = base_category,
                                spec = spec, filter=filter, portal_type=portal_type,
                                strict_membership = strict_membership, strict = strict,
                                display_id = 'getTitle')


    security.declarePublic('resolveCategory')
    def resolveCategory(self, relative_url):
        """
          Finds an object from a relative_url
          Method is public since we use restrictedTraverse
        """
        cache = getReadOnlyTransactionCache(self)
        if cache is not None:
          key = ('resolveCategory', relative_url)
          try:
            return cache[key]
          except KeyError:
            pass

        try:
          obj = self.restrictedTraverse(relative_url)
          if obj is None:
            REQUEST = self.REQUEST
            url = '%s/%s' % ('/'.join(self.getPhysicalPath()), relative_url)
            #LOG("CMFCategory:",0,"Trying url %s" % url )
            obj = self.portal_catalog.resolve_url(url, REQUEST)
          #LOG('Obj type', 0, str(obj.getUid()))
          value = obj
        except (KeyError, AttributeError) :
          LOG("CMFCategory WARNING",0,"Could not access object relative_url %s" % relative_url )
          value = None

        if cache is not None:
          cache[key] = value

        return value

InitializeClass( CategoryTool )

# Psyco
from Products.ERP5Type.PsycoWrapper import psyco
psyco.bind(CategoryTool)
