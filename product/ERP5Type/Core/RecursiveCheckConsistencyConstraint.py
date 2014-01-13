##############################################################################
#
# Copyright (c) 2014 Nexedi SARL and Contributors. All Rights Reserved.
#   Gabriel Monnerat <gabriel@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
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

from Products.ERP5Type.mixin.constraint import ConstraintMixin

class RecursiveCheckConsistencyConstraint(ConstraintMixin):
  """
  """
  meta_type = 'ERP5 Recursive Check Consistency Constraint'
  portal_type = 'Recursive Check Consistency Constraint'

  def _checkConsistency(self, obj, fixit=0, filter=None):
    """Calls checkConsistency on obj subdocuments"""
    error_list = []
    for subdocument in obj.objectValues():
      error_list.extend(subdocument.checkConsistency(fixit=fixit, filter=filter))
    return error_list
