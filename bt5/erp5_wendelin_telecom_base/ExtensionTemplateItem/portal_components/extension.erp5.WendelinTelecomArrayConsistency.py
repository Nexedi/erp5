##############################################################################
#
# Copyright (c) 2025 Nexedi SA and Contributors. All Rights Reserved.
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

import pandas as pd

def checkDuplicatedEntryConsistency(self, fixit=False, debug=False):
  data_array_dtype = self.getArrayDtypeNames()
  data_array_shape = self.getArrayShape()
  if data_array_shape is None \
    or data_array_dtype is None \
    or data_array_shape in [(), (0,)]:
    # empty arrays are always consistent
    return []

  time_field = data_array_dtype[0]
  cell_id_field = data_array_dtype[1]

  if time_field != 'utc' and cell_id_field != 'cell_id':
    # This Data Array isn't ORS UE/RRC/RMS type, so skip check:
    return []

  subset_columns = [time_field, cell_id_field]
  if data_array_dtype[2] == 'antenna':
    # RMS RX use case
    subset_columns.append(data_array_dtype[2])

  # XXX Is it ok to load entire array like this?
  data_zarray = self.getArray()[:]
  data_frame = pd.DataFrame.from_records(data_zarray)

  duplication = data_frame.duplicated(subset=subset_columns, keep=False)
  if duplication.any():
    if debug:
      return data_frame[duplication].to_dict(orient='list')
    return ['This Data Array constains an unexpected duplication.']
  return []




