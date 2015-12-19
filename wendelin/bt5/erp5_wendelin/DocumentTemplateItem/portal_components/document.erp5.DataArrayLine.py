# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2015 Nexedi SA and Contributors. All Rights Reserved.
#                    Ivan Tyagov <ivan@nexedi.com>
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
from Products.ERP5Type.Base import TempBase
from erp5.component.document.DataArray import DataArray
from Products.ERP5Type.Utils import createExpressionContext, \
  evaluateExpressionFromString

class GetIndex(TempBase):
  def __getitem__(self, idx):
    return idx

class DataArrayLine(DataArray):
  """
  A view on parent data array
  """

  def initArray(self, shape, dtype):
    """
    Not Implemented.
    """
    raise NotImplementedError

  def getArray(self, default=None):
    """
    Get numpy view of Parent Data Array according to index.
    """
    getindex = GetIndex("getindex")
    expression_context = createExpressionContext(None, portal=getindex)
    index = evaluateExpressionFromString(
      expression_context,
      "python: portal[%s]" %self.getIndexExpression()
    )
    array_view = self.getParentValue().getArray()[index]
    dtype = self.getDtype()
    if dtype is not None:
      return array_view.view(dtype=dtype)
    else:
      return array_view
