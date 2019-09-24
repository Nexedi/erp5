# -*- coding: utf-8 -*-
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
from collections import deque
import re
from BTrees.OOBTree import OOTreeSet
from Products.ERP5Type.Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo
from AccessControl import Unauthorized, getSecurityManager
from Acquisition import aq_base, aq_inner
from Products.ERP5Type import Permissions
from Products.ERP5Type.Core.Folder import OFS_HANDLER
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type.Cache import getReadOnlyTransactionCache
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable
from Products.CMFCategory import _dtmldir
from Products.CMFCore.PortalFolder import ContentFilter
from Products.CMFCategory.Renderer import Renderer
from Products.CMFCategory.Category import Category, BaseCategory
from OFS.Traversable import NotFound
from zLOG import LOG, PROBLEM, WARNING, ERROR

_marker = object()

class CategoryError( Exception ):
    pass


class RelatedIndex(): # persistent.Persistent can be added
                      # without breaking compatibility

  def __repr__(self):
    try:
      contents = ', '.join('%s=%r' % (k, list(v))
                           for (k, v) in self.__dict__.iteritems())
    except Exception:
      contents = '...'
    return '<%s(%s) at 0x%x>' % (self.__class__.__name__, contents, id(self))

  def __nonzero__(self):
    return any(self.__dict__.itervalues())

  def add(self, base, relative_url):
    try:
      getattr(self, base).add(relative_url)
    except AttributeError:
      setattr(self, base, OOTreeSet((relative_url,)))

  def remove(self, base, relative_url):
    try:
      getattr(self, base).remove(relative_url)
    except (AttributeError, KeyError):
      pass


class CategoryTool(BaseTool):
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

    _folder_handler = OFS_HANDLER # BBB

    # Declarative Security
    security = ClassSecurityInfo()

    security.declareProtected( Permissions.ManagePortal
                             , 'manage_overview' )
    manage_overview = DTMLFile( 'explainCategoryTool', _dtmldir )


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
      return ContentFilter(**self._buildFilter(spec, filter, kw))

    # Category accessors
    security.declareProtected(Permissions.AccessContentsInformation, 'getBaseCategoryList')
    def getBaseCategoryList(self, context=None, sort=False):
      """
        Returns the ids of base categories of the portal_categories tool
        if no context is provided, otherwise, returns the base categories
        defined for the class

        Two alias are provided :

        getBaseCategoryIds -- backward compatibility with early ERP5 versions

        baseCategoryIds -- for zope users conveniance
      """
      if context is None:
        result = self.objectIds()
      else:
        # XXX Incompatible with ERP5Type per portal type categories
        result = context._categories
      return (sorted if sort else list)(result)

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
      cache = getReadOnlyTransactionCache()
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
        relative_url = \
        self._removeDuplicateBaseCategoryIdInCategoryPath(base_category,
                                                                 relative_url)
        value = self.unrestrictedTraverse(relative_url)
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

        relative_url -- a single relative url or a list of relative urls

        strict       -- if set to 1, only return uids of parents, not
                        relative_url
      """
      uid_set = set()
      if isinstance(relative_url, str):
        relative_url = (relative_url,)
      for path in relative_url:
        try:
          o = self.getCategoryValue(path, base_category=base_category)
          if o is not None:
            if base_category is None:
              my_base_category = self.getBaseCategoryId(path)
            else:
              my_base_category = base_category
            bo_uid = self[my_base_category].getUid()
            uid_set.add((o.getUid(), bo_uid, 1)) # Strict Membership
            if not strict:
              while o.portal_type == 'Category':
                # This goes up in the category tree
                # XXX we should also go up in some other cases....
                # ie. when some documents act as categories
                o = o.aq_parent # We want acquisition here without aq_inner
                o_uid = o.getUid()
                if o_uid == bo_uid:
                  break
                uid_set.add((o_uid, bo_uid, 0)) # Non Strict Membership
        except (KeyError, AttributeError):
          LOG('WARNING: CategoriesTool',0, 'Unable to find uid for %s' % path)
      return list(uid_set) # cast to list for <dtml-in>

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
    def getCategoryChildTitleItemList(self, base_category=None, *args, **kw):
      """
      Returns a list of tuples by parsing recursively all categories in a
      given list of base categories. Uses getTitle as default method
      """
      return self.getCategoryChildItemList(base_category, 'title', *args, **kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getCategoryChildIdItemList')
    def getCategoryChildIdItemList(self, base_category=None, *args, **kw):
      """
      Returns a list of tuples by parsing recursively all categories in a
      given list of base categories. Uses getId as default method
      """
      return self.getCategoryChildItemList(base_category, 'id', *args, **kw)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getCategoryChildItemList')
    def getCategoryChildItemList(self, base_category=None, display_id = None,
          recursive=1, base=0, display_none_category=1, **kw):
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
          result += category.getCategoryChildItemList(
                               base=base,
                               recursive=recursive,
                               display_id=display_id,
                               display_none_category=0,
                               **kw)
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
      if isinstance(spec, str):
        spec = (spec,)
      elif isinstance(spec, list):
        spec = tuple(spec)
      spec_len = len(spec)
      for path in self._getCategoryList(context):
        # LOG('getCategoryMembershipList',0,str(path))
        my_base_category = path.split('/', 1)[0]
        for my_category in category_list:
          if isinstance(my_category, str):
            category = my_category
          else:
            category = my_category.getRelativeUrl()
          if my_base_category == category:
            path = self._removeDuplicateBaseCategoryIdInCategoryPath(my_base_category, path)
            if spec_len == 0:
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
        parent = context.aq_inner.aq_parent # aq_inner is required to make sure we use containment
                                            # just as in ERP5Type.Base.getParentValue
        # Handle parent base category is a special way
        membership.append(parent)
      return membership

    security.declareProtected( Permissions.AccessContentsInformation, 'setCategoryMembership' )
    def setCategoryMembership(self, context, *args, **kw):
      self._setCategoryMembership(context, *args, **kw)
      context.reindexObject()

    def _setCategoryMembership(self, context, base_category_list,
                               category_list, base=0, keep_default=1,
                               spec=(), filter=None, checked_permission=None,
                               **kw):
      """
        Sets the membership of the context on the specified base_category
        list and for the specified portal_type spec

        context            --    the context on which we are looking for categories

        base_category_list --    a single base category (string) or a list of base categories
                                 or a single base category object or a list of base category objects

        category_list      --    a single category (string) or a list of categories

        spec               --    a list or a tuple of portal types

        checked_permission        --    a string which defined the permission
                                        to filter the object on

      """
#       LOG("CategoryTool, setCategoryMembership", 0 ,
#           'category_list: %s' % str(category_list))
      # XXX We must use filters in the future
      # where_expression = self._buildQuery(spec, filter, kw)
      if spec is ():
        portal_type = kw.get('portal_type', ())
        if isinstance(portal_type, str):
          portal_type = (portal_type,)
        spec = portal_type

      if isinstance(category_list, str):
        category_list = (category_list, )
      elif category_list is None:
        category_list = ()
      # Seems never called, category_list seems to always contain a list of string
      elif isinstance(category_list, (tuple, list, set, frozenset)):
        if any([c is not None and not isinstance(c, str) for c in category_list]):
          raise TypeError('CategoryTool.setCategoryMembership only takes string(s) as value', base_category_list, category_list)
      else:
        raise TypeError('CategoryTool.setCategoryMembership only takes string(s) as value', base_category_list, category_list)


      if isinstance(base_category_list, str):
        base_category_list = (base_category_list, )

      if checked_permission is not None:
        checkPermission = self.portal_membership.checkPermission

      new_category_list = deque()
      default_base_category_set = set()
      default_category_set = set()
      for path in self._getCategoryList(context):
        my_base_id = self.getBaseCategoryId(path)
        if my_base_id in base_category_list:
          if spec or checked_permission is not None:
            obj = self.unrestrictedTraverse(path, None)
            if obj is not None:
              # If spec is (), then we should keep nothing
              # Everything will be replaced
              # If spec is not (), Only keep this if not in our spec
              if (spec and obj.portal_type not in spec) or not (
                  checked_permission is None or
                  checkPermission(checked_permission, obj)):
                new_category_list.append(path)
                continue
          # We must remember the default value for each replaced category
          if keep_default and my_base_id not in default_base_category_set:
            default_base_category_set.add(my_base_id)
            default_category_set.add(path)
        else:
          # Keep each membership which is not in the
          # specified list of base_category ids
          new_category_list.append(path)
      # Before we append new category values (except default values)
      # We must make sure however that multiple links are possible
      base = '' if base or len(base_category_list) > 1 \
        else base_category_list[0] + '/'
      for path in category_list:
        if path not in ('', None):
          if base:
            path = base + path
          elif self.getBaseCategoryId(path) not in base_category_list:
            continue
          if path in default_category_set:
            default_category_set.remove(path)
            new_category_list.appendleft(path)
          else:
            new_category_list.append(path)
      self._setCategoryList(context, new_category_list)


    security.declareProtected( Permissions.AccessContentsInformation, 'setDefaultCategoryMembership' )
    def setDefaultCategoryMembership(self, context, base_category, default_category,
                                              spec=(), filter=None,
                                              portal_type=(), base=0,
                                              checked_permission=None ):
      """
        Sets the membership of the context on the specified base_category
        list and for the specified portal_type spec

        context            --    the context on which we are looking for categories

        base_category_list --    a single base category (string) or a list of base categories
                                 or a single base category object or a list of base category objects

        category_list      --    a single category (string) or a list of categories

        spec               --    a list or a tuple of portal types

        checked_permission        --    a string which defined the permission
                                        to filter the object on

      """
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

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getSingleCategoryMembershipList')
    def getSingleCategoryMembershipList(self, context, base_category, base=0,
                                         spec=(), filter=None,
                                         checked_permission=None, **kw):
      """
        Returns the local membership of the context for a single base category
        represented as a list of relative URLs

        context       --    the context on which we are looking for categories

        base_category --    a single base category (string)

        spec          --    a list or a tuple of portal types

        base          --    if set to 1, returns relative URLs to portal_categories
                            if set to 0, returns relative URLs to the base category

        checked_permission        --    a string which defined the permission
                                        to filter the object on
      """
      # XXX We must use filters in the future
      # where_expression = self._buildQuery(spec, filter, kw)
      if spec is ():
        spec = kw.get('portal_type', ())

      # Build the ckecked_permission filter
      if checked_permission is not None:
        checkPermission = self.getPortalObject().portal_membership.checkPermission
        def permissionFilter(category):
          object = self.unrestrictedTraverse(category) # XXX Why unrestrictedTraverse and not resolveCategory ?
          if object is not None and checkPermission(checked_permission, object):
            return category
          else:
            return None

      # We must treat parent in a different way
      #LOG('getSingleCategoryMembershipList', 0, 'base_category = %s, spec = %s, base = %s, context = %s, context.aq_inner.aq_parent = %s' % (repr(base_category), repr(spec), repr(base), repr(context), repr(context.aq_inner.aq_parent)))
      if base_category == 'parent':
        parent = context.aq_inner.aq_parent # aq_inner is required to make sure we use containment
                                            # just as in Base.getParentValue
        if parent.portal_type in spec:
          parent_relative_url = parent.getRelativeUrl()
          if (checked_permission is None) or \
            (permissionFilter(parent_relative_url) is not None):
            # We do not take into account base here
            # because URL categories tend to fail
            # if temp objects are used and generated through
            # traversal (see WebSite and WebSection in ERP5)
            return [parent] # A hack to be able to handle temp objects
            # Previous code bellow for information
            if base:
              return ['parent/%s' % parent_relative_url] # This will fail if temp objects are used
            else:
              return [parent_relative_url] # This will fail if temp objects are used
        #LOG('getSingleCategoryMembershipList', 0, 'not in spec: parent.portal_type = %s, spec = %s' % (repr(parent.portal_type), repr(spec)))
        return []

      # XXX We must use filters in the future
      # where_expression = self._buildQuery(spec, filter, kw)
      result = []
      append = result.append
      # Make sure spec is a list or tuple
      if isinstance(spec, str):
        spec = (spec,)
      elif isinstance(spec, list):
        spec = tuple(spec)
      spec_len = len(spec)
      # Filter categories
      if getattr(aq_base(context), 'categories', _marker) is not _marker:

        for category_url in self._getCategoryList(context):
          my_base_category = category_url.split('/', 1)[0]
          if my_base_category == base_category:
            category_url = self._removeDuplicateBaseCategoryIdInCategoryPath(my_base_category, category_url)
            #LOG("getSingleCategoryMembershipList",0,"%s %s %s %s" % (context.getRelativeUrl(),
            #                  my_base_category, base_category, category_url))
            if (checked_permission is None) or \
                (permissionFilter(category_url) is not None):
              if spec_len == 0:
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
                                         spec=(), filter=None, _acquired_object_set=None, **kw ):
      # XXX: This cache is rarely useful, and the overhead quite important.
      #      It would certainly become counter-productive if any significative
      #      improvement was done to the cached methods.
      cache = getReadOnlyTransactionCache()
      if cache is not None:
        key = ('getSingleCategoryAcquiredMembershipList', context,
               base_category, base, spec, filter, repr(kw))
        try:
          return cache[key]
        except KeyError:
          pass

      result = self._getSingleCategoryAcquiredMembershipList(context, base_category, base=base,
                                                             spec=spec, filter=filter,
                                                             _acquired_object_set=_acquired_object_set,
                                                             **kw)
      if cache is not None:
        cache[key] = result

      return result

    def _filterCategoryListByPermission(self, base_category, base, category_list, permission):
      """This method returns a category list filtered by a permission.
      If the permission is None, returns a passed list as it is.
      """
      if permission is None:
        return category_list
      checkPermission = self.getPortalObject().portal_membership.checkPermission
      resolveCategory = self.resolveCategory
      new_category_list = []
      append = new_category_list.append
      for category in category_list:
        try:
          if base:
            category_path = category
          else:
            category_path = '%s/%s' % (base_category, category)
          value = resolveCategory(category_path)
          if checkPermission(permission, value):
            append(category)
        except Unauthorized:
          pass
      return new_category_list

    def _getSingleCategoryAcquiredMembershipList(self, context, base_category,
                                         base = 0, spec = (), filter = None,
                                         acquired_portal_type = (),
                                         checked_permission = None,
                                         _acquired_object_set=None,
                                         **kw ):
      """
        Returns the acquired membership of the context for a single base category
        represented as a list of relative URLs

        context       --    the context on which we are looking for categories

        base_category --    a single base category (string)

        spec          --    a list or a tuple of portal types

        base          --    if set to 1, returns relative URLs to portal_categories
                            if set to 0, returns relative URLs to the base category

        checked_permission        --    a string which defined the permission
                                        to filter the object on

        alt_base_category         --    an alternative base category if the first one fails

        acquisition_copy_value    --    if set to 1, the looked up value will be copied
                            as an attribute of self

        acquisition_mask_value    --    if set to 1, the value of the category of self
                            has priority on the looked up value

        _acquired_object_set is a special, internal parameter to deal with
        recursive calls on the same object.

      """
      #LOG("Get Acquired Category ",0,str((base_category, context,)))
      #LOG("Get Acquired Category acquired_object_dict: ",0,str(acquired_object_dict))
      # XXX We must use filters in the future
      # where_expression = self._buildQuery(spec, filter, kw)
      portal_type = kw.get('portal_type', ())
      if spec is ():
        spec = portal_type # This is bad XXX - JPS - spec is for meta_type, not for portal_type - be consistent !
      if isinstance(spec, str):
        spec = (spec,)
      elif isinstance(spec, list):
        spec = tuple(spec)

      if isinstance(acquired_portal_type, str):
        acquired_portal_type = [acquired_portal_type]

      if _acquired_object_set is None:
        _acquired_object_set = set()
      else:
        uid = context.getUid()
        key = (uid, base_category, tuple(spec))
        if key in _acquired_object_set:
          return []
        _acquired_object_set = _acquired_object_set.copy()
        _acquired_object_set.add(key)

      result = self.getSingleCategoryMembershipList( context, base_category, base=base,
                            spec=spec, filter=filter, **kw ) # Not acquired because this is the first try
                                                             # to get a local defined category

      base_category_value = self.get(base_category)
      #LOG("result", 0, str(result))
      if base_category_value is not None:
        # If we do not mask or append, return now if not empty
        if result \
                and base_category_value.getAcquisitionMaskValue() \
                and not base_category_value.getAcquisitionAppendValue():
          # If acquisition masks and we do not append values, then we must return now
          return self._filterCategoryListByPermission(base_category, base, result, checked_permission)
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
                  base_category, spec=spec, filter=filter, portal_type=portal_type, base=base, _acquired_object_set=_acquired_object_set)
            else:
              new_result = []
            #if base_category_value.acquisition_mask_value:
            #  # If acquisition masks, then we must return now
            #  return new_result
            if base_category_value.getAcquisitionAppendValue():
              # If acquisition appends, then we must append to the result
              result.extend(new_result)
            elif new_result:
              return self._filterCategoryListByPermission(base_category, base, new_result, checked_permission) # Found enough information to return
        # Next we look at references
        #LOG("Get Acquired BC", 0, base_category_value.getAcquisitionBaseCategoryList())
        acquisition_base_category_list = base_category_value.getAcquisitionBaseCategoryList()
        alt_base_category_list = base_category_value.getFallbackBaseCategoryList()
        all_acquisition_base_category_list = acquisition_base_category_list + alt_base_category_list
        acquisition_pt = base_category_value.getAcquisitionPortalTypeList()
        for my_base_category in acquisition_base_category_list:
          # We implement here special keywords
          if my_base_category == 'parent':
            parent = context.aq_inner.aq_parent # aq_inner is required to make sure we use containment
            parent_portal_type = getattr(aq_base(parent), 'portal_type',
                                         _marker)
            if parent_portal_type is _marker:
              my_acquisition_object_list = []
            else:
              #LOG("Parent Object List ",0,str(parent.getRelativeUrl()))
              #LOG("Parent Object List ",0,str(parent.portal_type))
              #LOG("Parent Object List ",0,str(acquisition_pt))
              #my_acquisition_object_path = parent.getPhysicalPath()
              #if my_acquisition_object_path in acquired_object_dict:
              if len(acquisition_pt) == 0 \
                      or parent_portal_type in acquisition_pt:
                my_acquisition_object_list = [parent]
              else:
                my_acquisition_object_list = []
          else:
            #LOG('getAcquiredCategoryMembershipList', 0, 'my_acquisition_object = %s, acquired_object_dict = %s' % (str(context), str(acquired_object_dict)))
            my_acquisition_list = self.getSingleCategoryAcquiredMembershipList(context,
                        my_base_category,
                        portal_type=tuple(acquisition_pt),
                        _acquired_object_set=_acquired_object_set)
            my_acquisition_object_list = []
            if my_acquisition_list:
              resolveCategory = self.resolveCategory
              append = my_acquisition_object_list.append
              for c in my_acquisition_list:
                o = resolveCategory(c)
                if o is not None:
                  append(o)
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
                #LOG('my_acquisition_object',0, str(getattr(my_acquisition_object, '_categories', ())))
                #LOG('my_acquisition_object',0, str(base_category))

                # We should only consider objects which define that category
                if base_category in getattr(my_acquisition_object, '_categories', ()) or base_category_value.getFallbackBaseCategoryList():
                  if (not acquired_portal_type) or my_acquisition_object.portal_type in acquired_portal_type:
                    #LOG("Recursive call ",0,str((spec, my_acquisition_object.portal_type)))
                    new_result = self.getSingleCategoryAcquiredMembershipList(my_acquisition_object,
                        base_category, spec=spec, filter=filter, portal_type=portal_type, base=base,
                        acquired_portal_type=acquired_portal_type,
                        _acquired_object_set=_acquired_object_set)
                  else:
                    #LOG("No recursive call ",0,str((spec, my_acquisition_object.portal_type)))
                    new_result = []
                  if base_category_value.getAcquisitionAppendValue():
                    # If acquisition appends, then we must append to the result
                    result.extend(new_result)
                  elif len(new_result) > 0:
                    #LOG("new_result ",0,str(new_result))
                    if len(original_result) == 0 \
                            and base_category_value.getAcquisitionCopyValue():
                      # If copy is set and result was empty, then copy it once
                      # If sync is set, then copy it again
                      self.setCategoryMembership( context, base_category, new_result,
                                    spec=spec, filter=filter, portal_type=portal_type, base=base )
                    # We found it, we can return
                    return self._filterCategoryListByPermission(base_category, base, new_result, checked_permission)


          if len(result) > 0 \
                  and base_category_value.getAcquisitionCopyValue():
            # If copy is set and result was empty, then copy it once
            # If sync is set, then copy it again
            self.setCategoryMembership( context, base_category, result,
                                         spec=spec, filter=filter,
                                         portal_type=portal_type, base=base )
        fallback_base_category_list \
                = base_category_value.getFallbackBaseCategoryList()
        if len(result) == 0 and len(fallback_base_category_list) > 0:
          # We must then try to use the alt base category
          getSingleCategoryAcquiredMembershipList \
                  = self.getSingleCategoryAcquiredMembershipList
          resolveCategory = self.resolveCategory
          append = result.append
          for base_category in fallback_base_category_list:
            # First get the category list
            category_list = getSingleCategoryAcquiredMembershipList( context, base_category, base=1,
                                 spec=spec, filter=filter, _acquired_object_set=_acquired_object_set, **kw )
            # Then convert it into value
            category_value_list = [resolveCategory(x) for x in category_list]
            # Then build the alternate category
            if base:
              base_category_id = base_category_value.getId()
              for category_value in category_value_list:
                if category_value is None :
                  message = "category does not exists for %s (%s)"%(
                                       context.getPath(), category_list)
                  LOG('CMFCategory', ERROR, message)
                  raise CategoryError (message)
                else :
                  append('%s/%s' % (base_category_id, category_value.getRelativeUrl()))
            else :
              for category_value in category_value_list:
                if category_value is None :
                  message = "category does not exists for %s (%s)"%(
                                       context.getPath(), category_list)
                  LOG('CMFCategory', ERROR, message)
                  raise CategoryError (message)
                else :
                  append(category_value.getRelativeUrl())
      # WE MUST IMPLEMENT HERE THE REST OF THE SEMANTICS
      #LOG("Get Acquired Category Result ",0,str(result))
      return self._filterCategoryListByPermission(base_category, base, result, checked_permission)

    security.declareProtected( Permissions.AccessContentsInformation,
                                               'getAcquiredCategoryMembershipList' )
    def getAcquiredCategoryMembershipList(self, context, base_category = None, base=1,
                                          spec=(), filter=None, _acquired_object_set=None, **kw):
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
                                    spec=spec, filter=filter, _acquired_object_set=_acquired_object_set, **kw ))
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
      if getattr(aq_base(context), 'isCategory', 0):
        if context.isMemberOf(category, strict_membership=strict_membership):
          return 1
      base_category = category.split('/', 1)[0] # Extract base_category for optimisation
      if strict_membership:
        for c in self.getAcquiredCategoryMembershipList(context, base_category=base_category):
          if c == category:
            return 1
      else:
        for c in self.getAcquiredCategoryMembershipList(context, base_category=base_category):
          if c == category or c.startswith(category + '/'):
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
      for c in self.getAcquiredCategoryList(context):
        if c.find(category) >= 0:
          return 1
      return 0

    security.declareProtected( Permissions.AccessContentsInformation, 'getCategoryList' )
    def getCategoryList(self, context):
      result = getattr(aq_base(context), 'categories', None)
      if result is not None:
        result = list(result)
      elif isinstance(context, dict):
        return list(context.get('categories', ()))
      else:
        result = []
      if getattr(context, 'isCategory', 0):
        category_url = context.getRelativeUrl()
        if category_url not in result:
          result.append(category_url) # Pure category is member of itself
      return result

    _getCategoryList = getCategoryList

    security.declareProtected( Permissions.ModifyPortalContent, 'setCategoryList' )
    def setCategoryList(self, context, value):
       self._setCategoryList(context, value)
       context.reindexObject()

    security.declareProtected( Permissions.ModifyPortalContent, '_setCategoryList' )
    def _setCategoryList(self, context, value):
      old = set(getattr(aq_base(context), 'categories', ()))
      relative_url = context.getRelativeUrl()

      # Pure category are member of itself, but we don't store this membership
      # (because of issues when the category is renamed/moved or cloned)
      if getattr(context, 'isCategory', 0) and relative_url in value:
        # note that we don't want to cast as set at this point to keep ordering (and duplicates).
        value = [x for x in tuple(value) if x != relative_url]

      context.categories = value = tuple(value)
      if context.isTempDocument():
        return

      value = set(value)
      for edit, value in ("remove", old - value), ("add", value - old):
        for path in value:
          base = self.getBaseCategoryId(path)
          try:
            if self[base].isRelatedLocallyIndexed():
              path = self._removeDuplicateBaseCategoryIdInCategoryPath(base, path)
              ob = aq_base(self.unrestrictedTraverse(path))
              try:
                related = ob._related_index
              except AttributeError:
                if edit is "remove":
                  continue
                related = ob._related_index = RelatedIndex()
              getattr(related, edit)(base, relative_url)
          except KeyError:
            pass

    security.declareProtected( Permissions.AccessContentsInformation, 'getAcquiredCategoryList' )
    def getAcquiredCategoryList(self, context):
      result = self.getAcquiredCategoryMembershipList(context,
                     base_category = self.getBaseCategoryList(context=context))
      for c in self._getCategoryList(context):
        # Make sure all local categories are considered
        if c not in result:
          result.append(c)
      return result

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
          self.setCategoryList(o, category_list)

          if getattr(aq_base(o),
                    'notifyAfterUpdateRelatedContent', None) is not None:
            o.notifyAfterUpdateRelatedContent(previous_category_url,
                                              new_category_url) # XXX - wrong programming Approach
                                                                # for ERP5 - either use interaction
                                                                # workflows or interactors rather
                                                                # than creating notifyWhateverMethod

        else:
          LOG('CMFCategory', PROBLEM,
              'updateRelatedContent: %s does not exist' % brain.path)

      for brain in self.Base_zSearchRelatedObjectsByPredicate(
                                              category_uid = context.getUid()):
        o = brain.getObject()
        if o is not None:
          category_list = []
          for category in o.getMembershipCriterionCategoryList():
            new_category = self.updateRelatedCategory(category,
                                                      previous_category_url,
                                                      new_category_url)
            category_list.append(new_category)
          o._setMembershipCriterionCategoryList(category_list)

          if getattr(aq_base(o),
                    'notifyAfterUpdateRelatedContent', None) is not None:
            o.notifyAfterUpdateRelatedContent(previous_category_url,
                                              new_category_url) # XXX - wrong programming Approach
                                                                # for ERP5 - either use interaction
                                                                # workflows or interactors rather
                                                                # than creating notifyWhateverMethod

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
                            checked_permission=None, **kw):
      """
        This methods returns the list of objects related to the context
        with the given base_category_list.
      """
      strict_membership = kw.get('strict_membership', kw.get('strict', 0))
      portal_type = kw.get('portal_type')

      if isinstance(portal_type, str):
        portal_type = portal_type,

      # Base Category may not be related, besides sub categories
      relative_url = context.getRelativeUrl()
      local_index_dict = {}
      is_any_base_category = False
      if isinstance(context, BaseCategory):
        category_list = relative_url,
      else:
        category_list = []
        if isinstance(base_category_list, str):
          base_category_list = base_category_list,
        elif base_category_list is () or base_category_list is None:
          base_category_list = self.getBaseCategoryList()
          is_any_base_category = True
        for base_category in base_category_list:
          if self[base_category].isRelatedLocallyIndexed():
            category = base_category + '/'
            local_index_dict[base_category] = '' \
              if relative_url.startswith(category) else category
          elif not is_any_base_category:
            # If base_category_list contains all base categories, and the
            # relation is not locally indexed, then just do not apply any
            # relational condition. This assumes relation membership
            # conditions would not exclude any document, iow there are no
            # indexed relation which has a non-existing base category.
            category_list.append("%s/%s" % (base_category, relative_url))

      portal_catalog = context.getPortalObject().portal_catalog
      def search(category_list, portal_type, strict_membership):
        inner_join_list = []
        catalog_kw = {
          'query': portal_catalog.getCategoryParameterDict(
            category_list=category_list,
            strict_membership=strict_membership,
            onJoin=inner_join_list.append,
          ),
        }
        if portal_type is not None:
          catalog_kw['portal_type'] = portal_type
        return portal_catalog.unrestrictedSearchResults(
          select_list=['relative_url', 'portal_type'],
          inner_join_list=inner_join_list,
          **catalog_kw
        )
      result_dict = {}
      if local_index_dict:
        # For some base categories, lookup indexes in ZODB.
        recurse = isinstance(context, Category) and not strict_membership
        def check_local():
          r = set(getattr(related, base_category, ()))
          r.difference_update(result_dict)
          for r in r:
            try:
              ob = self.unrestrictedTraverse(r)
              if category in aq_base(ob).categories:
                result_dict[r] = ob
                continue
              # Do not add 'r' to result_dict, because 'ob' may be linked in
              # another way.
            except (AttributeError, KeyError):
              result_dict[r] = None
            related.remove(base_category, r)
        tv = getTransactionalVariable().setdefault(
          'CategoriesTool.getRelatedValueList', {})
        try:
          related = aq_base(context)._related_index
        except AttributeError:
          related = RelatedIndex()
        include_self = False
        for base_category, category in local_index_dict.iteritems():
          if not category:
            # Categories are member of themselves.
            include_self = True
            result_dict[relative_url] = context
          category += relative_url
          if tv.get(category, -1) < recurse:
            # Update local index with results from catalog for backward
            # compatibility. But no need to do it several times in the same
            # transaction.
            for r in search(category_list=[category],
                            portal_type=None,
                            strict_membership=strict_membership):
              r = r.relative_url
              # relative_url is empty if object is deleted (but not yet
              # unindexed). Nothing specific to do in such case because
              # category tool won't match.
              try:
                ob = self.unrestrictedTraverse(r)
                categories = aq_base(ob).categories
              except (AttributeError, KeyError):
                result_dict[r] = None
                continue
              if category in categories:
                related.add(base_category, r)
                result_dict[r] = ob
              elif recurse:
                for p in categories:
                  if p.startswith(category + '/'):
                    try:
                      o = self.unrestrictedTraverse(p)
                      p = aq_base(o)._related_index
                    except KeyError:
                      continue
                    except AttributeError:
                      p = o._related_index = RelatedIndex()
                    result_dict[r] = ob
                    p.add(base_category, r)
            tv[category] = recurse
          # Get and check all objects referenced by local index for the base
          # category that is currently considered.
          check_local()
        # Modify context only if it's worth it.
        if related and not hasattr(aq_base(context), '_related_index'):
          context._related_index = related
        # In case of non-strict membership search, include all objects that
        # are linked to a subobject of context.
        if recurse:
          r = [context]
          while r:
            for ob in r.pop().objectValues():
              r.append(ob)
              relative_url = ob.getRelativeUrl()
              if include_self:
                result_dict[relative_url] = ob
              try:
                related = aq_base(ob)._related_index
              except AttributeError:
                continue
              for base_category, category in local_index_dict.iteritems():
                category += relative_url
                check_local()
        # Filter out objects that are not of requested portal type.
        result = [ob for ob in result_dict.itervalues() if ob is not None and (
          not portal_type or ob.getPortalType() in portal_type)]
        # Finish with base categories that are only indexed in catalog,
        # making sure we don't return duplicate values.
      else:
        # Catalog-only search.
        result = []
      if category_list or is_any_base_category:
        if is_any_base_category:
          catalog_kw = {
            ('strict__' if strict_membership else '') +
            'any__uid': context.getUid(),
          }
          if portal_type is not None:
            catalog_kw['portal_type'] = portal_type
          from_catalog_result_list = portal_catalog.unrestrictedSearchResults(
            select_list=['relative_url', 'portal_type'],
            **catalog_kw
          )
        else:
          from_catalog_result_list = search(category_list=category_list,
                        portal_type=portal_type,
                        strict_membership=strict_membership)
        for r in from_catalog_result_list:
          if r.relative_url not in result_dict:
            try:
              result.append(self.unrestrictedTraverse(r.path))
            except KeyError:
              pass

      if checked_permission is None:
        return result

      # Check permissions on object
      if isinstance(checked_permission, str):
        checked_permission = checked_permission,
      checkPermission = self.portal_membership.checkPermission
      def check(ob):
        for permission in checked_permission:
          if checkPermission(permission, ob):
            return True
      return filter(check, result)

    security.declareProtected( Permissions.AccessContentsInformation,
                               'getRelatedPropertyList' )
    def getRelatedPropertyList(self, context, base_category_list=None,
                               property_name=None,
                               checked_permission=None, **kw):
      """
        This methods returns the list of property_name on  objects
        related to the context with the given base_category_list.
      """
      result = []
      for o in self.getRelatedValueList(
                          context=context,
                          base_category_list=base_category_list,
                          checked_permission=checked_permission, **kw):
        result.append(o.getProperty(property_name, None))
      return result

    security.declareProtected( Permissions.AccessContentsInformation, 'getCategoryMemberValueList' )
    def getCategoryMemberValueList(self, context, base_category=None,
                                         portal_type=(), strict_membership=False, strict=False, **kw):
      """
      This returns a catalog_search resource with can then be used by getCategoryMemberItemList
      """
      if base_category is None:
        base_category = context.getBaseCategoryId()
      if context.portal_type == 'Base Category' and context.getId() == base_category:
        # Looking for all documents which are member of context a
        # (Base Category) via a relationship of its own type: assume this means
        # caller wants to retrieve documents having any document related via a
        # relationship of the type of context.
        # XXX: ignoring "strict*" argument. It does not have much meaning in
        # this case anyway.
        key = 'category.base_category_uid'
      else:
        key = (
          'strict_'
          if strict_membership or strict else
          'default_'
        ) + base_category + '_uid'
      sql_kw = {
        key: context.getUid(),
      }
      if portal_type:
        sql_kw['portal_type'] = portal_type
      return self.getPortalObject().portal_catalog(**sql_kw)

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
      return Renderer(**kw).render(self.getCategoryMemberValueList(
        context,
        portal_type=kw.get('portal_type'),
        strict_membership=kw.get('strict_membership'),
        strict=kw.get('strict'),
      ))

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
                                display_id = 'title')

    security.declarePublic('resolveCategory')
    def resolveCategory(self, relative_url):
        """
          Finds an object from a relative_url
          Method is public since we use restrictedTraverse
        """
        return self._resolveCategory(relative_url, True)

    def _resolveCategory(self, relative_url, restricted=False):
        if not isinstance(relative_url, str):
          # Handle parent base category is a special way
          return relative_url
        cache = getReadOnlyTransactionCache()
        if cache is not None:
          cache_key = ('resolveCategory', relative_url)
          try:
            return cache[cache_key]
          except KeyError:
            pass

        # This below is complicated, because we want to avoid acquisitions
        # in most cases, but we still need to restrict the access.
        # For instance, if the relative url is source/person_module/yo,
        # only person_module should be acquired. This becomes very critical,
        # for example, with source/sale_order_module/1/1/1, because
        # we do not want to acquire a Sale Order when a Line or a Cell is
        # not present.
        #
        # I describe my own idea about the categorisation system in ERP5
        # here, because I think it is important to understand why
        # resolveCategory is implemented in this way.
        #
        # The goal of resolveCategory is to provide either a conceptual
        # element or a concrete element from a certain viewpoint. There
        # are 5 different actors in this system:
        #
        #   - Categorisation Utility (= Category Tool)
        #   - Abstract concept (= Base Category)
        #   - Certain view (= Category)
        #   - Classification of documents (= Module or Tool)
        #   - Document (= Document)
        #
        # Categories are conceptually a tree structure with the root
        # of Category Tool. The next level is always Base Categories,
        # to represent abstract concepts. The deeper going down in a tree,
        # the more concrete a viewpoint is.
        #
        # Base Categories may contain other Base Categories, because an
        # abstract concept can be a part of another abstract concept,
        # simply representing a multi-level concept. Base Categories may
        # contain Categories, because an abstract concept gets more concrete.
        # This is the same for Modules and Tools.
        #
        # Categories may contain Categories only in a way that views
        # are more concrete downwards. Thus a category may not acquire
        # a Base Category or a upper-level category. Also, Categories
        # may not contain Modules or Tools, because they don't narrow
        # views.
        #
        # In a sense, Modules and Tools are similar to Categories,
        # as they do narrow things down, but they are fundamentally
        # different from Categories, because their purpose is to
        # classify data processed based on business or system procedures,
        # while Categories provide a backbone of supporting such
        # procedures by more abstract viewpoints. The difference between
        # Modules and Tools are about whether procedures are business
        # oriented or system oriented.
        #
        # Documents may contain Documents, but only to a downward direction.
        # Otherwise, things get more abstract in a tree.
        #
        # According to those ideas, the current implementation may not
        # always behave correctly, because you can resolve a category
        # which violates the rules. For example, you can resolve
        # 'base_category/portal_categories'. This is an artifact,
        # and can be considered as a bug. In the future, Tools and Modules
        # should be clarified if they should behave as Category-like
        # objects, so that the resolver can detect violations.
        if isinstance(relative_url, basestring):
          stack = relative_url.split('/')
        else:
          stack = list(relative_url)
        stack.reverse()
        __traceback_info__ = relative_url

        if restricted:
          validate = getSecurityManager().validate
          def getOb(container):
            obj = container._getOb(key, None)
            if obj is None or validate(container, container, key, obj):
              return obj
            raise Unauthorized('unauthorized access to element %s' % key)
        else:
          def getOb(container):
            return container._getOb(key, None)

        # XXX Currently, resolveCategory accepts that a category might
        # not start with a Base Category, but with a Module. This is
        # probably wrong. For compatibility, this behavior is retained.
        # JPS: I confirm that category should always start with a base
        # category
        obj = self
        if stack:
          portal = aq_inner(self.getPortalObject())
          key = stack.pop()
          obj = getOb(self)
          if obj is None:
            obj = getOb(portal)
            if obj is not None:
              obj = obj.__of__(self)
          else:
            while stack:
              container = obj
              key = stack.pop()
              obj = getOb(container)
              if obj is not None:
                break
              obj = getOb(self)
              if obj is None:
                obj = getOb(portal)
                if obj is not None:
                  obj = obj.__of__(container)
                break

          while obj is not None and stack:
            key = stack.pop()
            obj = getOb(obj)

        if obj is None:
          LOG('CMFCategory', WARNING,
              'Could not get object %s' % relative_url)

        if cache is not None:
          cache[cache_key] = obj

        return obj

    def _removeDuplicateBaseCategoryIdInCategoryPath(self, base_category_id,
                                                     path):
      """Specific Handling to remove duplicated base_categories in path
      values like in following example: 'region/region/europe/west'.
      """
      splitted_path = path.split('/', 2)
      if len(splitted_path) >= 2 and base_category_id == splitted_path[1]:
        # Duplicate found, strip len(base_category_id + '/') in path
        path = path[len(base_category_id)+1:]
      return path


InitializeClass( CategoryTool )

# Psyco
from Products.ERP5Type.PsycoWrapper import psyco
psyco.bind(CategoryTool)
