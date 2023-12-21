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
from collections import defaultdict
from itertools import product
import six
from DateTime import DateTime

_STOP_RECURSION_PORTAL_TYPE_SET = ('Base Category', 'ERP5 Site')

def getSecurityCategoryValueFromAssignment(self, rule_dict):
  """
  This function returns a list of dictionaries which represent
  the security groups the user represented by self is member of,
  based on the applicable Assignment objects it contains.

  rule_dict (dict)
    Keys: tuples listings base category names set on the Assignment
      and which represent security groups assigned to the user.
    Values: tuples describing which combinations of the base categories
      whose parent categories the user is also member of.

  Example call to illustrate argument and return value structures:
  getSecurityCategoryValueFromAssignment(
    rule_dict={
      ('function', ): ((), ('function', )),
      ('group', ): ((), ),
      ('function', 'group'): ((), ('function', )),
    }
  )
  [
    {
      'function': (
        (<Category function/accountant/chief>, False),
        (<Category function/accountant/chief>, True),
        (<Category function/accountant>, True),
      ),
    }
    {
      'group': ((<Category group/nexedi>, False), ),
    },
    {
      'function': (
        (<Category function/accountant/chief>, False),
        (<Category function/accountant/chief>, True),
        (<Category function/accountant>, True),
      ),
      'group': ((<Category group/nexedi>, False), ),
    },
  ]
  """
  base_category_set = set(sum((tuple(x) for x in rule_dict), ()))
  recursive_base_category_set = set(sum((sum((tuple(y) for y in x), ()) for x in six.itervalues(rule_dict)), ()))
  category_value_set_dict = defaultdict(set)
  parent_category_value_dict = {}
  assignment_membership_dict_list = []
  now = DateTime()
  for assignment_value in self.objectValues(portal_type='Assignment'):
    if assignment_value.getValidationState() == 'open' and (
      not assignment_value.hasStartDate() or assignment_value.getStartDate() <= now
    ) and (
      not assignment_value.hasStopDate() or assignment_value.getStopDate() >= now
    ):
      assignment_membership_dict = {}
      for base_category in base_category_set:
        category_value_list = assignment_value.getAcquiredValueList(base_category)
        if category_value_list:
          assignment_membership_dict[base_category] = tuple(set(category_value_list))
          category_value_set_dict[base_category].update(category_value_list)
          if base_category in recursive_base_category_set:
            for category_value in category_value_list:
              while True:
                parent_category_value = category_value.getParentValue()
                if (
                  parent_category_value in parent_category_value_dict or
                  parent_category_value.getPortalType() in _STOP_RECURSION_PORTAL_TYPE_SET
                ):
                  break
                parent_category_value_dict[category_value] = parent_category_value
                category_value = parent_category_value
      if assignment_membership_dict:
        assignment_membership_dict_list.append(assignment_membership_dict)
  result = []
  for base_category_list, recursion_list in six.iteritems(rule_dict):
    result_entry = set()
    for assignment_membership_dict in assignment_membership_dict_list:
      assignment_category_list = []
      for base_category in base_category_list:
        category_set = set()
        for category_value in assignment_membership_dict.get(base_category, ()):
          for recursion_base_category_set in recursion_list:
            if base_category in recursion_base_category_set:
              while True:
                category_set.add((category_value, True))
                try:
                  category_value = parent_category_value_dict[category_value]
                except KeyError:
                  break
            else:
              category_set.add((category_value, False))
        assignment_category_list.append((base_category, tuple(category_set)))
      if assignment_category_list:
        result_entry.add(tuple(assignment_category_list))
    for result_item in result_entry:
      result.append(dict(result_item))
  return result

def asSecurityGroupIdSet(category_dict, key_sort=sorted):
  """
  The script takes the following parameters:

  category_dict (dict)
    keys: base category names.
    values: list of categories composing the security groups the document is member of.
  key_sort ((dict) -> key vector)
    Function receiving the value of category_dict and returning the list of keys to
    use to construct security group names, in the order in which these group names
    will be used.
    May return keys which are not part of category_dict.
    Defaults to a lexicographic sort of all keys.
    The External Method pointing at this implementation should be overridden (and
    called using skinSuper) in order to provide this argument with a custom value.

  Example call:
    context.ERP5Type_asSecurityGroupIdSet(
      category_dict={
        'site': [(<Category france/lille>, False)],
        'group': [(<Category nexedi>, False)],
        'function': [(<Category accounting/accountant>, True)],
      }
    )

  This will generate a string like 'ACT*_NXD_LIL' where "LIL", "NXD" and "ACT" are
  the codification of respecively "france/lille", "nexedi" and "accounting/accountant"
  categories.

  If the category points to a document portal type (ex. trade condition, project, etc.),
  and if no codification property is defined for this type of object,
  the security ID group is generated by considering the object reference or
  the object ID.

  ERP5Type_asSecurityGroupIdSet can also return a list of users whenever a
  category points to a Person instance. This is useful to implement user based local
  role assignments instead of abstract security based local roles.
  """
  list_of_list = []
  user_list = []
  associative_list = []
  for base_category_id in key_sort(category_dict):
    try:
      category_list = category_dict[base_category_id]
    except KeyError:
      continue
    for category_value, is_child_category in category_list:
      if category_value.getPortalType() == 'Person':
        user_name = category_value.Person_getUserId()
        if user_name is not None:
          user_list.append(user_name)
          associative_list = []
      elif not user_list:
        associative_list.append(
          (
            category_value.getProperty('codification') or
            category_value.getProperty('reference') or
            category_value.getId()
          ) + ('*' if is_child_category else ''),
        )
    if associative_list:
      list_of_list.append(associative_list)
      associative_list = []
  if user_list:
    return user_list
  return ['_'.join(x) for x in product(*list_of_list) if x]

def getSecurityCategoryFromAssignment(
  self,
  base_category_list,
  user_name,
  object,  # pylint: disable=redefined-builtin
  portal_type,
  child_category_list=None
):
  """
  DEPRECATED: use getSecurityCategoryValueFromAssignment for better performance.

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
  category_list = []
  if child_category_list is None:
    child_category_list = []

  user_path_set = {
    x['path'] for x in self.acl_users.searchUsers(
      id=user_name,
      exact_match=True,
    ) if 'path' in x
  }
  if not user_path_set:
    # if a person_object was not found in the module, we do nothing more
    # this happens for example when a manager with no associated person object
    # creates a person_object for a new user
    return []
  user_path, = user_path_set
  person_object = self.getPortalObject().unrestrictedTraverse(user_path)
  now = DateTime()

  # We look for every valid assignments of this user
  for assignment in person_object.contentValues(filter={'portal_type': 'Assignment'}):
    if assignment.getValidationState() == "open" and (
      not assignment.hasStartDate() or assignment.getStartDate() <= now
    ) and (
      not assignment.hasStopDate() or assignment.getStopDate() >= now
    ):
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


def getSecurityCategoryFromAssignmentParent(self, base_category_list, user_name,
                                            object, # pylint: disable=redefined-builtin
                                            portal_type):
  return getSecurityCategoryFromAssignment(self, base_category_list, user_name,
                                           object, # pylint: disable=redefined-builtin
                                           portal_type, child_category_list=base_category_list)

def getSecurityCategoryFromAssignmentParentGroup(self, base_category_list, user_name,
                                                 object, # pylint: disable=redefined-builtin
                                                 portal_type):
  return getSecurityCategoryFromAssignment(self, base_category_list, user_name,
                                           object, # pylint: disable=redefined-builtin
                                           portal_type, child_category_list=('group',))

def getSecurityCategoryFromAssignmentParentFunction(self, base_category_list, user_name,
                                                    object, # pylint: disable=redefined-builtin
                                                    portal_type):
  return getSecurityCategoryFromAssignment(self, base_category_list, user_name,
                                           object, # pylint: disable=redefined-builtin
                                           portal_type, child_category_list=('function',))

def getSecurityCategoryFromAssignmentParentFunctionParentGroup(self, base_category_list, user_name,
                                                               object, # pylint: disable=redefined-builtin
                                                               portal_type):
  return getSecurityCategoryFromAssignment(self, base_category_list, user_name,
                                           object, # pylint: disable=redefined-builtin
                                           portal_type, child_category_list=('function', 'group'))

