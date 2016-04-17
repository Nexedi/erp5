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


from Products.ERP5Type.mixin.constraint import ConstraintMixin
translateString = lambda msg: msg  # just to extract messages

class DataArrayLineExistenceConstraint(ConstraintMixin):
  """
    Checks if data array line with defined reference exists.

    This constraint supports fixing consistency.
  """

  def _checkConsistency(self, obj, fixit = 0):
    """
      Implement here the consistency checker
    """

    error_list = []

    name = self.getReference()
    index_expression = self.getIndexExpression()
    dtype = self.getDtype()
    if name not in obj:
      message = "Data Array Line ${reference} does not exist"
      if fixit:
        obj.newContent(
          name,
          portal_type = "Data Array Line",
          reference = name,
          index_expression = index_expression,
          dtype = dtype
        )
        message = "%s (Fixed)" %message
      error_list.append(
        self._generateError(
          obj,
          message,
          mapping = {"reference" : name}
        )
      )

    return error_list
