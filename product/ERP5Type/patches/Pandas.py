##############################################################################
#
# Copyright (c) 2023 Nexedi SARL and Contributors. All Rights Reserved.
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

try:
  import pandas as pd
except ImportError:
  pass
else:
  # This monkey-patch reverts https://github.com/pandas-dev/pandas/commit/25dcff59
  #
  # We're often using unicode strings in DataFrame column names,
  # which makes it impossible to unpickle np arrays. With python3
  # this isn't a problem anymore, so we should remove this once ERP5
  # is fully migrated to Python3 only support.
  pd_DataFrame_to_records = pd.DataFrame.to_records
  def DataFrame_to_records(*args, **kwargs):
    record = pd_DataFrame_to_records(*args, **kwargs)
    record.dtype = np.dtype([(str(k), v) for k, v in record.dtype.descr])
    return record
  pd.DataFrame.to_records = DataFrame_to_records
