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

from copy import deepcopy
from OFS.Folder import Folder
from Products.CMFCore.utils import UniqueObject
from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from Products.ERP5Type import Permissions
from Products.ERP5Type.Base import Base
from Products.CMFCategory import _dtmldir
from Products.CMFCore.PortalFolder import ContentFilter
from Products.CMFCategory.Renderer import Renderer

import string, re

from zLOG import LOG

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
      three colors (eg : color1, color2, color3 which are used in the top, belt and in
      the bottom) and if a particular variation of that swim suit has two of the three colors        the same (eg black, blue, black) then the category membership list from the color point        of view is::

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
        return context._categories

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
        return map(lambda x:self[x], context._categories)

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
      try:
        relative_url = str(relative_url)
        if base_category is not None:
          relative_url = '%s/%s' % (base_category, relative_url)
        node = self.unrestrictedTraverse(relative_url)
        return node
      except:
        return None

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
        return relative_url.split('/')[0]
      except:
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
      except:
        return None

    security.declareProtected(Permissions.AccessContentsInformation, 'getCategoryParentUidList')
    def getCategoryParentUidList(self, relative_url, base_category = None, strict=0):
      """
        Returns the uids of all categories provided in categories

        relative_url -- a single relative url of a list of
                        relative urls

        strict       -- if set to 1, only return uids of parents, not
                        relative_url
      """
      uid_dict = {}
      if type(relative_url) is type('a'): relative_url = (relative_url,)
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
                    o = o.aq_parent
                    uid_dict[(int(o.uid), bo_uid, 0)] = 1 # Non Strict Membership
        except:
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
      elif type(base_category) == type('a'):
        base_category_list = [base_category]
      else:
        base_category_list = base_category
      result = []
      for base_category in base_category_list:
        category = self[base_category]
        if category is not None:
          result += category.getCategoryChildRelativeUrlList(base=base,recursive=recursive)
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
      return self.getCategoryChildItemList(recursive = recursive,base=base,
       display_none_category=display_none_category,display_id='getTitle', sort_id=sort_id)

    security.declareProtected(Permissions.AccessContentsInformation,
                                                      'getCategoryChildIdItemList')
    def getCategoryChildIdItemList(self, base_category=None,
              recursive=1, base=0, display_none_category=0, sort_id=None):
      """
      Returns a list of tuples by parsing recursively all categories in a
      given list of base categories. Uses getId as default method
      """
      return self.getCategoryChildItemList(recursive = recursive,base=base,
         display_none_category=display_none_category,display_id='getId', sort_id=sort_id)

    security.declareProtected(Permissions.AccessContentsInformation,
                                                      'getCategoryChildItemList')
    def getCategoryChildItemList(self, base_category=None, display_id = None,
            recursive=1, base=0, display_none_category=1, sort_id=None):
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
      """
      if type(base_category) == type('a'):
        base_category_list = [base_category]
      elif base_category is None:
        base_category_list = self.getBaseCategoryList()
      else:
        base_category_list = base_category
      #LOG('getCategoryChildItemList', 0, str(base_category_list))
      if display_none_category:
        result = [('', '')]
      else:
        result = []
      for base_category in base_category_list:
        category = self[base_category]
        if category is not None:
          result += category.getCategoryChildItemList(base=base,recursive=recursive,
                                                            display_id=display_id)
      #if sort_id is not None:
      #  result.sort()

      return result

    security.declareProtected(Permissions.AccessContentsInformation, 'getBaseItemList')
    getBaseItemList = getCategoryChildItemList

    # Category to Tuple Conversion
    security.declareProtected(Permissions.View, 'asItemList')
    def asItemList(self, relative_url, base_category=None,
            display_id = None, base = 0, sort_id=None):
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
      result = []
      if display_id is None:
        for c in relative_url:
          result += [(c, c)]
      else:
        for c in relative_url:
          o = self.getCategoryValue(c, base_category=base_category)
          if o is not None:
            try:
              v = getattr(o, display_id)()
              result = result + [(c,v)]
            except:
              LOG('WARNING: CategoriesTool',0, 'Unable to call %s on %s' %
                  (method, c))
          else:
            LOG('WARNING: CategoriesTool',0, 'Unable to find category %s' % c)

      #if sort_id is not None:
      #  result.sort()

      return result

    security.declareProtected(Permissions.View, 'getItemList')
    getItemList = asItemList

    # Convert a list of membership to path
    security.declareProtected(Permissions.View, 'asPathList')
    def asPathList(self, base_category, category_list):
      if type(category_list) == type('a'):
        category_list = [category_list]
      if category_list == None:
        category_list = []
      new_list = []
      for v in category_list:
        new_list += ['%s/%s' % (base_category,v)]
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
      if type(base_category) not in (type(()), type([])):
        category_list = [base_category]
      else:
        category_list = base_category
      if type(spec) is not type([]) and type(spec) is not type(()):
        spec = [spec]
      for path in self._getCategoryList(context):
        # LOG('getCategoryMembershipList',0,str(path))
        my_base_category = path.split('/')[0]
        for my_category in category_list:
          if type(my_category) is type('a'):
            category = my_category
          else:
            category = my_category.getRelativeUrl()
          if my_base_category == category:
            if spec is ():
              if base:
                membership += [path]
              else:
                membership += [path[len(category)+1:]]
            else:
              try:
               o = self.unrestrictedTraverse(path)
               # LOG('getCategoryMembershipList',0,str(o.portal_type))
               if o.portal_type in spec:
                if base:
                  membership += [path]
                else:
                  membership += [path[len(category)+1:]]
              except:
                LOG('WARNING: CategoriesTool',0, 'Unable to find object for path %s' % path)
      # We must include parent if specified explicitely
      if 'parent' in category_list:
        parent = context.aq_parent
        if parent.portal_type in spec:
          if base:
            membership += ['parent/' + parent.getRelativeUrl()]
          else:
            membership += [parent.getRelativeUrl()]
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
      if spec is (): spec = portal_type
      #LOG("set Category",0,str(category_list))

      default_dict = {}
      self._cleanupCategories(context)
      if type(category_list) is type('a'):
        category_list = (category_list,)
      elif category_list is None:
        category_list = ()
      if type(base_category_list) is type('a'):
        base_category_list = [base_category_list]
      new_category_list = []
      for path in self._getCategoryList(context):
        my_base_id = self.getBaseCategoryId(path)
        if not my_base_id in base_category_list:
          # Keep each membership which is not in the
          # specified list of base_category ids
          new_category_list += [path]
        else:
          if spec is ():
            # If spec is (), then we should keep nothing
            # Everything will be replaced
            keep_it = 0
          else:
            # Only keep this if not in our spec
            try:
              my_type = self.unrestrictedTraverse(path).portal_type
              keep_it = 1
              for spec_type in spec:
                if spec_type == my_type:
                  keep_it = 0
            except:
              keep_it = 0
          if keep_it:
            new_category_list += [path]
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
            default_new_category_list += [path]
        else:
          if path[len(base_category_list[0])+1:] in category_list:
            default_new_category_list += [path]
      # Before we append new category values (except default values)
      # We must make sure however that multiple links are possible
      default_path_found = {}
      for path in category_list:
        if path is not '':
          if base or len(base_category_list) > 1:
            # Only keep path which are member of base_category_list
            if self.getBaseCategoryId(path) in base_category_list:
              if path not in default_new_category_list or default_path_found.has_key(path):
                default_path_found[path] = 1
                new_category_list += [path]
          else:
            new_path = base_category_list[0] + '/' + path
            if new_path not in default_new_category_list:
              new_category_list += [new_path]
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
      if type(default_category) is type([]) or type(default_category) is type(()):
        default_category = default_category[0]
      category_list = self.getCategoryMembershipList(context, base_category,
                           spec=spec, filter=filter, portal_type=portal_type, base=base)
      new_category_list = [default_category]
      found_one = 0
      # We will keep from the current category_list
      # everything except the first occurence of category
      # this allows to have multiple occurences of the same category
      for category in category_list:
        if category != default_category or found_one:
          new_category_list += [category]
          found_one = 1
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
      #LOG('getSingleCategoryMembershipList', 0, 'base_category = %s, spec = %s, base = %s, context = %s, context.aq_parent = %s' % (repr(base_category), repr(spec), repr(base), repr(context), repr(context.aq_parent)))
      if base_category == 'parent':
        parent = context.aq_parent # aq_inner ?
        if parent.portal_type in spec:
          if base:
            return ['parent/' + parent.getRelativeUrl()]
          else:
            return [parent.getRelativeUrl()]
        #LOG('getSingleCategoryMembershipList', 0, 'not in spec: parent.portal_type = %s, spec = %s' % (repr(parent.portal_type), repr(spec)))
        return []

      result = []
      # XXX We must use filters in the future
      # where_expression = self._buildQuery(spec, filter, kw)
      spec = kw.get('portal_type', ())
      # Make sure spec is a list or tuple
      if type(spec) is type('a'):
        spec = [spec]
      # Filter categories
      if hasattr(context, 'categories'):
        for category_url in self._getCategoryList(context):
          my_base_category = category_url.split('/')[0]
          if my_base_category == base_category:
            #LOG("getSingleCategoryMembershipList",0,"%s %s %s %s" % (context.getRelativeUrl(),
            #                  my_base_category, base_category, category_url))
            if spec is ():
              if base:
                result += [category_url]
              else:
                result += [category_url[len(my_base_category)+1:]]
            else:
              try:
                my_reference = self.unrestrictedTraverse(category_url)
              except KeyError:
                # object does not exist
                my_reference = None
              if my_reference is not None:
                if my_reference.portal_type in spec:
                  if base:
                    result += [category_url]
                  else:
                    result += [category_url[len(my_base_category)+1:]]
      return result


    security.declareProtected( Permissions.AccessContentsInformation,
                                      'getSingleCategoryAcquiredMembershipList' )
    def getSingleCategoryAcquiredMembershipList(self, context, base_category, base=0,
                                         spec=(), filter=None, acquired_object_dict = None, **kw ):
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
      # LOG("Get Acquired Category ",0,str((base_category, context)))
      # XXX We must use filters in the future
      # where_expression = self._buildQuery(spec, filter, kw)

      portal_type = kw.get('portal_type', ())
      if spec is (): spec = portal_type # This is bad XXX - JPS - spec is for meta_type, not for portal_type - be consistent !

      if type(spec) is type('a'):
        spec = [spec]

      if acquired_object_dict is None:
        acquired_object_dict = {} # Initial call may include filter, etc. - do not keep
      else:
        context_base_key = (tuple(context.getPhysicalPath()), base_category)
        if context_base_key in acquired_object_dict:
          acquired_object_dict = deepcopy(acquired_object_dict)
          type_dict = acquired_object_dict[context_base_key]
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
        else:
          type_dict = {}
          if spec is ():
            type_dict[()] = 1
          else:
            for pt in spec:
              type_dict[pt] = 1
          acquired_object_dict = deepcopy(acquired_object_dict)
          acquired_object_dict[context_base_key] = type_dict

      result = self.getSingleCategoryMembershipList( context, base_category, base=base,
                            spec=spec, filter=filter, **kw )

      base_category_value = self.getCategoryValue(base_category)
      # LOG("base_category_value",0,str(base_category_value))
      # LOG("result",0,str(result))
      if base_category_value is not None:
        # If we do not mask or append, return now if not empty
        if base_category_value.getAcquisitionMaskValue() and \
                not base_category_value.getAcquisitionAppendValue() and \
                len(result) > 0:
          # If acquisition masks and we do not append values, then we must return now
          return result
        # First we look at local ids
        for object_id in base_category_value.getAcquisitionObjectIdList():
          my_acquisition_object = context.get(object_id)
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
            if base_category_value.acquisition_append_value:
              # If acquisition appends, then we must append to the result
              result += new_result
            elif len(new_result) > 0:
              return new_result # Found enough information to return
        # Next we look at references
        #LOG("Get Acquired BC",0,base_category_value.getAcquisitionBaseCategoryList())
        acquisition_base_category_list = base_category_value.getAcquisitionPortalTypeList()
        alt_base_category_list = base_category_value.getAcquisitionAltBaseCategoryList()
        all_acquisition_base_category_list = acquisition_base_category_list + alt_base_category_list
        acquisition_pt = base_category_value.getAcquisitionPortalTypeList(())
        for my_base_category in base_category_value.getAcquisitionBaseCategoryList():
        #for my_base_category in all_acquisition_base_category_list:
          # We implement here special keywords
          if my_base_category == 'parent':
            parent = context.aq_parent
            if parent is self.getPortalObject():
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
              #else:
              #  my_acquisition_object_list = []
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
              if hasattr(my_acquisition_object, '_categories'):
                # We should only consider objects which define that category
                if base_category in my_acquisition_object._categories:
                  if spec is () or my_acquisition_object.portal_type in spec:
                    #LOG("Recursive call ",0,str(spec))
                    new_result = self.getSingleCategoryAcquiredMembershipList(my_acquisition_object,
                        base_category, spec=spec, filter=filter, portal_type=portal_type, base=base,
                        acquired_object_dict=acquired_object_dict)
                  else:
                    #LOG("No recursive call ",0,str(spec))
                    new_result = []
                  if base_category_value.acquisition_append_value:
                    # If acquisition appends, then we must append to the result
                    result += new_result
                  elif len(new_result) > 0:
                    #LOG("new_result ",0,str(new_result))
                    if (base_category_value.acquisition_copy_value and len(original_result) == 0) \
                                                    or base_category_value.acquisition_sync_value:
                      # If copy is set and result was empty, then copy it once
                      # If sync is set, then copy it again
                      self.setCategoryMembership( context, base_category, new_result,
                                    spec=spec, filter=filter, portal_type=portal_type, base=base )
                    # We found it, we can return
                    return new_result


          if (base_category_value.acquisition_copy_value or base_category_value.acquisition_sync_value)\
                                                         and len(result) > 0:
            # If copy is set and result was empty, then copy it once
            # If sync is set, then copy it again
            self.setCategoryMembership( context, base_category, result,
                                         spec=spec, filter=filter, portal_type=portal_type, base=base )
        if len(result)==0 and len(base_category_value.getAcquisitionAltBaseCategoryList())>0:
          # We must then try to use the alt base category
          for base_category in base_category_value.getAcquisitionAltBaseCategoryList():
            result += self.getSingleCategoryAcquiredMembershipList( context, base_category, base=base,
                                       spec=spec, filter=filter, acquired_object_dict=acquired_object_dict, **kw )
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
      #LOG("Get Acquired Category", 0, "%s %s" % (base_category, context.getRelativeUrl()))
      result = []
      if base_category is None:
        base_category_list = context._categories
      elif type(base_category) is type('a'):
        base_category_list = [base_category]
      else:
        base_category_list = base_category
      #LOG('CT.getAcquiredCategoryMembershipList result',0,result)
      for base_category in base_category_list:
        result += self.getSingleCategoryAcquiredMembershipList(context, base_category, base=base,
                                    spec=spec, filter=filter, acquired_object_dict=acquired_object_dict, **kw )
        #LOG('CT.getAcquiredCategoryMembershipList new result',0,result)
      return result

    security.declareProtected( Permissions.AccessContentsInformation, 'isMemberOf' )
    def isMemberOf(self, context, category, strict=0):
      """
        Tests if an object if member of a given category
        Category is a string here. It could be more than a string (ex. an object)

        XXX - there should be 2 different methods, one which acuiqred
        and the other which does not. A complete review of
        the use of isMemberOf is required
      """
      if getattr(aq_base(context), 'isCategory', 0):
        return context.isMemberOf(category, strict=strict)
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
      if hasattr(context, 'categories'):
        if type(context.categories) == type((1,)):
          result = context.categories
        elif type(context.categories) == type([]):
          result = context.categories
        else:
          result = []
      elif type(context) is type({}):
        result = context.get('categories', {})
      else:
        result = []
      if getattr(context, 'isCategory', 0):
        result = tuple(list(result) + [context.getRelativeUrl()]) # Pure category is member of itself
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
      non_acquired = self._getCategoryList(context)
      for c in non_acquired:
        # Make sure all local categories are considered
        if c not in result:
          result.append(c)
      if getattr(context, 'isCategory', 0):
        result = tuple(list(result) + [context.getRelativeUrl()]) # Pure category is member of itself
      return result

    security.declareProtected( Permissions.ModifyPortalContent, '_cleanupCategories' )
    def _cleanupCategories(self, context):
      # Make sure _cleanupCategories does not modify objects each time it is called
      # or we get many conflicts
      requires_update = 0
      categories = []
      if hasattr(context, 'categories'):
        for cat in self._getCategoryList(context):
          if type(cat) == type('a'):
            categories += [cat]
          else:
            requires_update = 1
      if requires_update: self._setCategoryList(context, tuple(categories))

    # Catalog related methods
    def updateRelatedCategory(self, category, previous_category_url, new_category_url):
      new_category = re.sub('(?P<start>.*)/%s/(?P<stop>.*)' %
            previous_category_url,'\g<start>/%s/\g<stop>' % new_category_url,category)
      new_category = re.sub('(?P<start>.*)/%s$' %
            previous_category_url,'\g<start>/%s' % new_category_url, new_category)
      return new_category

    def updateRelatedContent(self, context, previous_category_url, new_category_url):
      """
        TODO: make this method resist to very large updates (ie. long transaction)
      """
      for brain in self.Base_zSearchRelatedObjectsByCategory(category_uid = context.getUid()):
        o = brain.getObject()
        if o is not None:
          category_list = []
          for category in self.getCategoryList(o):
            new_category = re.sub('(?P<start>.*)/%s/(?P<stop>.*)' %
                 previous_category_url,'\g<start>/%s/\g<stop>' % new_category_url,category)
            new_category = re.sub('(?P<start>.*)/%s$' %
                 previous_category_url,'\g<start>/%s' % new_category_url, new_category)
            category_list += [new_category]
          #LOG('updateRelatedContent of %s' % o.getRelativeUrl(), 0, str(category_list))
          self._setCategoryList(o, category_list)
          if hasattr(aq_base(o), 'notifyAfterUpdateRelatedContent'):
            o.notifyAfterUpdateRelatedContent(previous_category_url, new_category_url)
        else:
          LOG('WARNING updateRelatedContent',0,'%s does not exist' % brain.path)
      aq_context = aq_base(context)
      # Update related recursively if required
      if hasattr(aq_context, 'listFolderContents'):
        for o in context.listFolderContents():
          new_o_category_url = o.getRelativeUrl() # Relative Url is based on parent new_category_url
                             # so we must replace new_category_url with previous_category_url to find
          # the previous category_url for a
          previous_o_category_url = re.sub('(?P<start>.*)/%s$' %
               new_category_url,'\g<start>/%s' % previous_category_url, new_o_category_url)
          self.updateRelatedContent(o, previous_o_category_url, new_o_category_url)

    security.declareProtected( Permissions.AccessContentsInformation, 'getRelatedValueList' )
    def getRelatedValueList(self, context, base_category_list=None,
                                       spec=(), filter=None, base=1, **kw):
      #LOG('getRelatedValueList',0,'base_category_list: %s, filter: %s, kw: %s' %
      #        (str(base_category_list),str(filter),str(kw)))
      portal_type = kw.get('portal_type')

      if type(portal_type) is type('a'):
        portal_type = [portal_type]
      if spec is (): spec = None # We do not want to care about spec

      if type(base_category_list) is type('a'):
        base_category_list = [base_category_list]
      elif base_category_list is () or base_category_list is None:
        base_category_list = self.getBaseCategoryList()
      category_list = []
      #LOG('getRelatedValueList',0,'base_category_list: %s' % str(base_category_list))
      for base_category in base_category_list:
        category_list += ["%s/%s" % (base_category, context.getRelativeUrl())]

      brain_result = self.Base_zSearchRelatedObjectsByCategoryList(category_list = category_list,
                                                                   portal_type = portal_type )

      result = []
      for b in brain_result:
        o = b.getObject()
        if o is not None:
          result.append(o)

      return result
                                  # XXX missing filter and **kw stuff
      #return self.search_category(category_list = category_list, portal_type = spec)
      # future implementation with brains, much more efficient

    # SQL Expression Building
    security.declareProtected(Permissions.AccessContentsInformation, 'buildSQLSelector')
    def buildSQLSelector(self, category_list):
      """
        Returns an SQL selector expression from a list of categories
        We make here a simple method wich simply checks membership
        This is like an OR. More complex selections (AND of OR) will require
        to generate a much more complex where_expression with table aliases

        List of lists
      """
      if type(category_list) == type('a'):
        category_list = [category_list]
      sql_expr = []
      for category in category_list:
        if category is None:
          pass
        elif type(category) == type('a'):
          if category != '':
            category_uid = self.getCategoryUid(category)
            base_category_uid = self.getBaseCategoryUid(category)
            if category_uid is None: category_uid = 'NULL'
            if base_category_uid is None: base_category_uid = 'NULL'
            sql_expr += ['category.category_uid = %s AND category.base_category_uid = %s' %
                      (category_uid, base_category_uid)]
        else:
          single_sql_expr = []
          for single_category in category:
            if single_sql_expr != '':
              category_uid = self.getCategoryUid(single_category)
              base_category_uid = self.getBaseCategoryUid(single_category)
              if category_uid is None: category_uid = 'NULL'
              if base_category_uid is None: base_category_uid = 'NULL'
              single_sql_expr += \
                ['category.category_uid = %s AND category.base_category_uid = %s' %
                 (category_uid, base_category_uid)]
          if len(single_sql_expr) > 0:
            sql_expr += "( %s )" % string.join(single_sql_expr, ' OR ')
      if len(sql_expr) > 0:
        sql_expr = string.join(sql_expr, ' OR ')
      return sql_expr

    security.declareProtected( Permissions.AccessContentsInformation, 'getCategoryMemberValueList' )
    def getCategoryMemberValueList(self, context, base_category = None,
                                         spec = (), filter=None, portal_type=(), strict = 0):
      """
      This returns a catalog_search resource with can then be used by getCategoryMemberItemList

      """
      from Products.ERP5Form.Selection import DomainSelection
      if base_category is None: base_category = 'related'
      if spec is ():
        catalog_search = self.portal_catalog(selection_domain = DomainSelection(domain_dict = {base_category:context}))
      else:
        catalog_search = self.portal_catalog(portal_type = portal_type,
                      selection_domain = DomainSelection(domain_dict = {base_category:context}))

      return catalog_search

    security.declareProtected( Permissions.AccessContentsInformation, 'getCategoryMemberItemList' )
    def getCategoryMemberItemList(self, context, strict = 0, **kw):
      """
      This returns a list of items belonging to a category

      """
      k = {}
      for v in ('portal_type', 'spec'):
        if v in kw:
          k[v] = kw[v]
      catalog_search = self.getCategoryMemberValueList(context, **k)
      return Renderer(**kw).render(catalog_search)

    security.declareProtected( Permissions.AccessContentsInformation,
                                                                'getCategoryMemberTitleItemList' )
    def getCategoryMemberTitleItemList(self, context, base_category = None,
                                      spec = (), filter=None, portal_type=(), strict = 0):
      """
      This returns a title list of items belonging to a category

      """
      getCategoryMemberItemList(self, context, base_category = base_category,
        spec = spec, filter=filter, portal_type=portal_type, strict = strict, display_id = 'getTitle')


    security.declarePublic('resolveCategory')
    def resolveCategory(self, relative_url):
        """
          Finds an object from a relative_url
          Method is public since we use restrictedTraverse
        """
        try:
          obj = self.restrictedTraverse(relative_url)
          if obj is None:
            REQUEST = self.REQUEST
            url = '%s/%s' % ('/'.join(self.getPhysicalPath()), relative_url)
            #LOG("CMFCategory:",0,"Trying url %s" % url )
            obj = self.portal_catalog.resolve_url(url, REQUEST)
          #LOG('Obj type', 0, str(obj.getUid()))
          return obj
        except:
          LOG("CMFCategory WARNING",0,"Could not access object relative_url %s" % relative_url )
          return None

InitializeClass( CategoryTool )

# Psyco
import psyco
psyco.bind(CategoryTool)
