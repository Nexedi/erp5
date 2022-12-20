##############################################################################
#
# Copyright (c) 2002-2007 Nexedi SA and Contributors. All Rights Reserved.
#
# This program is free software: you can Use, Study, Modify and Redistribute
# it under the terms of the GNU General Public License version 3, or (at your
# option) any later version, as published by the Free Software Foundation.
#
# You can also Link and Combine this program with other software covered by
# the terms of any of the Free Software licenses or any of the Open Source
# Initiative approved licenses and Convey the resulting work. Corresponding
# source of such a combination shall include the source code for all other
# software used.
#
# This program is distributed WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See COPYING file for full licensing terms.
# See https://www.nexedi.com/licensing for rationale and options.
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
