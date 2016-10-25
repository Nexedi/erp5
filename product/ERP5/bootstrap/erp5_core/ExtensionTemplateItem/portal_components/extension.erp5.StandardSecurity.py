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

from Products.ERP5Security.ERP5GroupManager import ConsistencyError
from Products.ZSQLCatalog.SQLCatalog import SimpleQuery

def getSecurityCategoryFromAssignment(self, base_category_list, user_name, object, portal_type,
                                      child_category_list=[]):
  """
  This script returns a list of dictionaries which represent
  the security groups which a person is member of. It extracts
  the categories from the current user assignment.
  It is useful in the following cases:

  - associate a document (ex. an accounting transaction)
    to the division which the user was assigned to
    at the time it was created

  - calculate security membership of a user

  The parameters are

    base_category_list -- list of category values we need to retrieve
    user_name          -- string obtained from getSecurityManager().getUser().getId()
    object             -- object which we want to assign roles to
    portal_type        -- portal type of object
  """
  context = self

  category_list = []

  user_list = [
    x for x in self.acl_users.searchUsers(
      id=user_name,
      exact_match=True,
    ) if 'path' in x
  ]
  if not user_list:
    # if a person_object was not found in the module, we do nothing more
    # this happens for example when a manager with no associated person object
    # creates a person_object for a new user
    return []
  user, = user_list
  person_object = self.getPortalObject().unrestrictedTraverse(user['path'])

  # We look for every valid assignments of this user
  for assignment in person_object.contentValues(filter={'portal_type': 'Assignment'}):
    if assignment.getValidationState() == 'open':
      category_dict = {}
      for base_category in base_category_list:
        category_value_list = assignment.getAcquiredValueList(base_category)
        if category_value_list:
          for category_value in category_value_list:
            if base_category in child_category_list:
              if category_value.getPortalType() not in ('Base Category', 'ERP5 Site'):
                while category_value.getPortalType() not in ('Base Category', 'ERP5 Site'):
                  category_dict.setdefault(base_category, []).append('%s*' % category_value.getRelativeUrl())
                  category_value = category_value.getParentValue()
              else:
                category_dict.setdefault(base_category, []).append(category_value.getRelativeUrl())
            else:
              category_dict.setdefault(base_category, []).append(category_value.getRelativeUrl())
      category_list.append(category_dict)

  return category_list


def getSecurityCategoryFromAssignmentParent(self, base_category_list,
                                       user_name, object, portal_type):
  return getSecurityCategoryFromAssignment(self, base_category_list,
                                       user_name, object, portal_type, child_category_list=base_category_list)

def getSecurityCategoryFromAssignmentParentGroup(self, base_category_list,
                                       user_name, object, portal_type):
  return getSecurityCategoryFromAssignment(self, base_category_list,
                                       user_name, object, portal_type, child_category_list=('group',))

def getSecurityCategoryFromAssignmentParentFunction(self, base_category_list,
                                       user_name, object, portal_type):
  return getSecurityCategoryFromAssignment(self, base_category_list,
                                       user_name, object, portal_type, child_category_list=('function',))

def getSecurityCategoryFromAssignmentParentFunctionParentGroup(self, base_category_list,
                                       user_name, object, portal_type):
  return getSecurityCategoryFromAssignment(self, base_category_list,
                                       user_name, object, portal_type, child_category_list=('function', 'group'))
