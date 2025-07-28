# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2020 Nexedi SA and Contributors. All Rights Reserved.
#                    Klaus Wölfel <klaus@nexedi.com>
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
