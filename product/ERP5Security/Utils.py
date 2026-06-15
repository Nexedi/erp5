##############################################################################
#
# Copyright (c) 2026 Nexedi SA and Contributors. All Rights Reserved.
#                    Rafael Monnerat <rafael@nexedi.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################

from DateTime import DateTime
from Products.ERP5Type.Cache import CachingMethod, transactional_cached

def getValidAssignmentList(user, return_bool=False, checked_permission=None):
  """Returns list of valid assignments."""
  valid_assignment_list = []
  # check dates if exist
  kw = {
    "portal_type": "Assignment"
  }
  if checked_permission:
    kw["checked_permission"] = checked_permission

  now = DateTime()
  for assignment in user.contentValues(**kw):
    if assignment.getValidationState() == "open" and (
      not assignment.hasStartDate() or assignment.getStartDate() <= now
    ) and (
      not assignment.hasStopDate() or assignment.getStopDate() >= now
    ):
      valid_assignment_list.append(assignment)
      if return_bool:
        return True

  if return_bool:
    return False
  return valid_assignment_list

@transactional_cached(lambda *args: args)
def getCachedValidAssignmentList(user):
  """ Returns list of valid assignments for a given user
    Only calculated once per transaction """
  return getValidAssignmentList(user=user)

