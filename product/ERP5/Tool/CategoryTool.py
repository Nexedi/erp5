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

"""\
ERP portal_categories tool.
"""

from Products.CMFCategory.CategoryTool import *

from zLOG import LOG

class CategoryTool( CategoryTool ):
    """
      The CategoryTool object is the placeholder for all methods
      and algorithms related to categories and relations in ERP5.
    """

    id              = 'portal_categories'
    meta_type       = 'ERP5 Categories'
    allowed_types   = ( 'ERP5 Base Category',)

    # Declarative Security
    security = ClassSecurityInfo()

    # Filter content (ZMI))
    def filtered_meta_types(self, user=None):
        # Filters the list of available meta types.
        all = CategoryTool.inheritedAttribute('filtered_meta_types')(self)
        meta_types = []
        for meta_type in self.all_meta_types():
            if meta_type['name'] in self.allowed_types:
                meta_types.append(meta_type)
        return meta_types

    security.declareProtected(Permissions.AccessContentsInformation, 'getCategoryParentUidList')
    def getCategoryParentUidList(self, relative_url, base_category = None, strict=0):
      """
        Returns the uids of all categories provided in categories

        relative_url -- a single relative url of a list of
                        relative urls

        strict       -- if set to 1, only return uids of parents, not
                        relative_url
      """
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
            if base_category is None:
              base_category = self.getBaseCategoryId(path)
            else:
              base_category = base_category
            bo = getattr(self, base_category, None)
            if bo is not None:
              bo_uid = int(bo.getUid())
              uid_dict[(int(o.uid), bo_uid, 1)] = 1 # Strict membership
              if o.meta_type == 'ERP5 Category' or o.meta_type == 'ERP5 Base Category' or \
                o.meta_type == 'CMF Category' or o.meta_type == 'CMF Base Category':
                # This goes up in the category tree
                # XXX we should also go up in some other cases....
                # ie. when some documents act as categories
                if not strict:
                  while o.meta_type == 'ERP5 Category' or o.meta_type == 'CMF Category':
                    o = o.aq_parent
                    uid_dict[(int(o.uid), bo_uid, 0)] = 1 # Non strict
        except:
          LOG('WARNING: CategoriesTool',0, 'Unable to find uid for %s' % path)
      return uid_dict.keys()

    security.declareProtected(Permissions.AccessContentsInformation, 'getUids')
    getUids = getCategoryParentUidList

InitializeClass( CategoryTool )
