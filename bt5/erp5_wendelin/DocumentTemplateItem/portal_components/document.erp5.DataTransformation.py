# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2020 Nexedi SA and Contributors. All Rights Reserved.
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
from erp5.component.document.Amount import Amount
from erp5.component.document.Transformation import Transformation


class DataTransformation(Transformation):
  """
  Contains a list of transformed data operations and the data operation used
  """
  meta_type = 'ERP5 Data Transformation'
  portal_type = 'Data Transformation'

  # Use Amount implementation of *VariationCategoryList
  # instead of the one VariatedMixin used by Transformation so that we can set Variation
  # on Initial Product
  getVariationBaseCategoryList = Amount.getVariationBaseCategoryList
  getVariationBaseCategoryItemList = Amount.getVariationBaseCategoryItemList
  getVariationCategoryList = Amount.getVariationCategoryList
  getVariationCategoryItemList = Amount.getVariationCategoryItemList
  getVariationRangeBaseCategoryList = Amount.getVariationRangeBaseCategoryList
  getVariationRangeCategoryList = Amount.getVariationRangeCategoryList
  getVariationRangeCategoryItemList = Amount.getVariationRangeCategoryItemList
  setVariationBaseCategoryList = Amount.setVariationBaseCategoryList
  setVariationCategoryList = Amount.setVariationCategoryList
  _setVariationCategoryList = Amount._setVariationCategoryList
