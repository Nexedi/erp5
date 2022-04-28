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
from erp5.component.document.DataArray import DataArray
from numpy import dtype
from numpy.lib.recfunctions import merge_arrays
from wendelin.lib.calc import mul
import sys

class MergedArray(object):

  def __init__(self, array_list):
    self.array_list = array_list

  def __getitem__(self, idx):
    if not(isinstance, idx, slice):
      raise TypeError("Only slice index is supported.")
    if idx.start == 0 and idx.stop == sys.maxint:
      raise ValueError("Only partial slice is supported")
    return merge_arrays([a[0:len(self)][idx] for a in self.array_list], flatten=True)

  # ~~~ ndarray-like attributes
  @property
  def data(self):
    raise TypeError("Direct access to data for BigArray is forbidden")
  @property
  def strides(self):
    return (self.itemsize,)
  @property
  def dtype(self):
    return dtype(reduce(lambda x, y: [(n, x.dtype.fields[n][0]) for n in x.dtype.names] +  [(n, y.dtype.fields[n][0]) for n in y.dtype.names], self.array_list))
  @property
  def shape(self):
    return (min((len(a) for a in self.array_list)),)
  @property
  def size(self):
    return mul(self.shape)
  def __len__(self):
    # lengths of the major axis
    return self.shape[0]
  @property
  def itemsize(self):
    return self.dtype.itemsize
  @property
  def nbytes(self):
    return self.itemsize * self.size
  @property
  def ndim(self):
    return len(self.shape)

class DataArrayView(DataArray):
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
    Get numpy view of views defined in Data Array View Lines.
    """
    line_list = [(l.getIntIndex(), l.getArray()) for l in self.objectValues(portal_type="Data Array View Line")]
    if not line_list:
      return None
    return MergedArray([l[1] for l in sorted(line_list)])