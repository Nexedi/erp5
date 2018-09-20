# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2018 Nexedi SA and Contributors. All Rights Reserved.
#                    Klaus Wölfel <klaus@nexedi.com>
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
import numpy as np
from erp5.component.document.DataArray import DataArray
from Products.ERP5Type.Base import TempBase
from Products.ERP5Type.Utils import createExpressionContext, \
  evaluateExpressionFromString

class GetIndex(TempBase):
  def __getitem__(self, idx):
    return idx

class DataArrayViewLine(DataArray):
  """
  Data Array like view on one or multiple Data Arrays
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
    index = evaluateExpressionFromString(
      createExpressionContext(None, portal=getindex),
      "python: portal[%s]" %self.getIndexExpression()
    )
    zbigarray = self.getPredecessorValue().getArray()
    try:
      array_view = zbigarray[index]
    except TypeError:
      array = zbigarray[:]
      new_dtype = np.dtype({name:array.dtype.fields[name] for name in index})
      array_view = np.ndarray(array.shape, new_dtype, array, 0, array.strides)
    name_list = self.getNameList()
    dtype_expression = self.getDtypeExpression()
    if dtype_expression is not None or name_list:
      if dtype_expression is None:
        dtype = np.dtype(array_view.dtype)
      else:
        dtype = evaluateExpressionFromString(
        createExpressionContext(None, portal=getindex),
        dtype_expression)
      dtype.names = name_list
      return array_view.view(dtype=dtype)
    return array_view
