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
ERP5 portal_categories tool.
"""

from Products.CMFCategory.CategoryTool import CategoryTool as CMFCategoryTool
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass, DTMLFile, PersistentMapping
from OFS.Folder import Folder as OFS_Folder
from Products.ERP5Type import Permissions
from Products.ERP5Type.CopySupport import CopyContainer
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type.Document import newTempBase
from Products.ERP5Type.Cache import CachingMethod

from zLOG import LOG

class CategoryTool(CopyContainer, CMFCategoryTool, BaseTool):
    """
      The CategoryTool object is the placeholder for all methods
      and algorithms related to categories and relations in ERP5.
    """

    id              = 'portal_categories'
    meta_type       = 'ERP5 Categories'
    portal_type     = 'Category Tool'
    allowed_types   = ( 'ERP5 Base Category',)

    # Declarative Security
    security = ClassSecurityInfo()

    # Filter content (ZMI))
    def filtered_meta_types(self, user=None):
        # Filters the list of available meta types.
        #all = CMFCategoryTool.inheritedAttribute('filtered_meta_types')(self)
        meta_types = []
        for meta_type in self.all_meta_types():
            if meta_type['name'] in self.allowed_types:
                meta_types.append(meta_type)
        return meta_types

    # patch, so that we are able to add the BaseCategory
    allowedContentTypes = BaseTool.allowedContentTypes
    getVisibleAllowedContentTypeList = BaseTool.getVisibleAllowedContentTypeList

    # Override this method to resolve an inheritance problem.
    def _verifyObjectPaste(self, *args, **kw):
      return BaseTool._verifyObjectPaste(self, *args, **kw)

    all_meta_types = BaseTool.all_meta_types

    security.declareProtected(Permissions.View, 'hasContent')
    def hasContent(self,id):
      return id in self.objectIds()

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
      if type(relative_url) is type('a'): relative_url = (relative_url,)
      for path in relative_url:
        try:
          o = self.getCategoryValue(path, base_category=base_category)
          if o is not None:
            if base_category is None:
              my_base_category = self.getBaseCategoryId(path)
            else:
              my_base_category = base_category
            bo = getattr(self, my_base_category, None)
            if bo is not None:
              bo_uid = bo.getUid()
              uid_dict[(o.getUid(), bo_uid, 1)] = 1 # Strict membership
              if o.meta_type == 'ERP5 Category' or o.meta_type == 'ERP5 Base Category' or \
                o.meta_type == 'CMF Category' or o.meta_type == 'CMF Base Category':
                # This goes up in the category tree
                # XXX we should also go up in some other cases....
                # ie. when some documents act as categories
                if not strict:
                  while o.meta_type == 'ERP5 Category' or o.meta_type == 'CMF Category':
                    o = o.aq_parent # We want acquisition here without aq_inner
                    uid_dict[(o.getUid(), bo_uid, 0)] = 1 # Non strict
        except (TypeError, KeyError):
          LOG('WARNING: CategoriesTool',0, 'Unable to find uid for %s' % path)
      return uid_dict.keys()

    security.declareProtected(Permissions.AccessContentsInformation, 'getUids')
    getUids = getCategoryParentUidList

    def getBaseCategoryDict(self):
      """
        Cached method to which resturns a dict with category names as keys, and None as values.
        This allows to search for an element existence in the list faster.
        ie: if x in self.getPortalObject().portal_categories.getBaseCategoryDict()
      """
      def getBaseCategoryDict(self):
        return dict.fromkeys(self.getBaseCategoryList(), None)
      return CachingMethod(getBaseCategoryDict, 'portal_categories.getBaseCategoryDict', cache_factory='erp5_content_long')(self)

    def updateRelatedContent(self, context,
                             previous_category_url, new_category_url):
      """See CMFCategory.CategoryTool.updateRelatedContent

      This method also update all predicates membership
      """
      CMFCategoryTool.updateRelatedContent(self,
                                           context,previous_category_url,
                                           new_category_url)

      # We also need to udpate all predicates membership
      domain_tool = getToolByName(context, 'portal_domains')
      portal_catalog = getToolByName(context, 'portal_catalog')
      kw = {}
      kw['predicate_category.category_uid'] = context.getUid()
      object_list = portal_catalog(**kw)
      for predicate in [x.getObject() for x in object_list]:
        membership_list = []
        for category in predicate.getMembershipCriterionCategoryList():
          new_category = self.updateRelatedCategory(category,
                                                    previous_category_url,
                                                    new_category_url)
          membership_list.append(new_category)
        predicate.setMembershipCriterionCategoryList(membership_list)
      # We do not need to to things recursively since
      # updateRelatedContent is already recursive.

InitializeClass( CategoryTool )

