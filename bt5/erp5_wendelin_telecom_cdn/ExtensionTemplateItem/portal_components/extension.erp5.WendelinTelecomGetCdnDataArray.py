import json
import numpy as np
import pandas as pd

RESAMPLE_SIZE = 1000
# Values with which to replace NaNs for each data field
NA_VALUES_REPLACEMENTS = {
  'bytes': 0.
}

def resample_data_zarray(
  np_data_zarray, time_field,
  time_start, time_end, resample_size
):
  '''
    Resample the provided numpy data array to the provided new size
    by averaging values in regular time intervals, if it is large enough to be downsized.
    Return a dictionary with the data arrays keyed to their respective data fields.
  '''
  data_frame = pd.DataFrame.from_records(np_data_zarray)
  data_frame[time_field] = pd.to_datetime(data_frame[time_field], unit='s')
  data_frame = data_frame.sort_values(by=time_field)

  data_frame['requests'] = 1
  # Resample data if array is too large
  if len(np_data_zarray) > resample_size:
    resample_period = int((time_end - time_start) / resample_size)
    if not resample_period:
      resample_period = 1
    data_frame = data_frame.resample(
      '%ss' % resample_period,
      on=time_field).sum()
    data_frame = data_frame.fillna(value=NA_VALUES_REPLACEMENTS)

  data_frame = data_frame.reset_index()
  data_frame[time_field] = data_frame[time_field].map(pd.Timestamp.timestamp)
  return data_frame


def get_cdn_throughput(data_array, data_array_dtype, time_start, time_end):
  data_zarray = data_array.getArray()[:]
  time_field = data_array_dtype[0]
  data_zarray, time_start, time_end = get_data_zarray_in_time_range(
    data_zarray, time_field, time_start, time_end
  )

  data_frame = resample_data_zarray(
    data_zarray,
    time_field,
    time_start,
    time_end,
    RESAMPLE_SIZE
  )

  data_frame['utc'] = data_frame[time_field].astype(int)
  data_frame = data_frame.groupby('utc').agg({
    'bytes': 'sum',
    'requests': 'sum'}).reset_index()
  base_resampled_data_dict = data_frame.to_dict(orient='list')
  response_dict = {
    'bytes': {
      'utc': base_resampled_data_dict['utc'],
      'bytes': base_resampled_data_dict['bytes']
    },
    'rps' : {
      'utc': base_resampled_data_dict['utc'],
      'rps': base_resampled_data_dict['requests']
    }
  }
  return response_dict

def get_data_zarray_in_time_range(np_data_zarray, time_field, time_start, time_end):
  '''
    Return a view of the provided numpy data array restricted to the provided time range,
    along with the time range bounds converted to timestamps from the data array.
  '''
  # Array may be out of order: get min and max timestamps
  np_data_time_zarray = np_data_zarray[time_field]
  if time_start is None or time_start == 'NaN':
    time_start = np.min(np_data_time_zarray)
  else:
    time_start = float(time_start)
  if time_end is None or time_end == 'NaN':
    time_end = np.max(np_data_time_zarray)
  else:
    time_end = float(time_end)
  time_mask = (np_data_time_zarray >= time_start) \
    & (np_data_time_zarray <= time_end)

  return np_data_zarray[time_mask], time_start, time_end

def getDataArrayForDataTypeAsJSON(self, data_array_url, data_type,
  time_start=None, time_end=None, REQUEST=None, RESPONSE=None):
  """
  """
  portal = self.getPortalObject()

  try:
    data_array = portal.restrictedTraverse(data_array_url)
  except KeyError:
    # Data Array does not exist
    RESPONSE.setStatus(404)
    return
  # Data Array is empty
  data_array_shape = data_array.getArrayShape()
  data_array_dtype = data_array.getArrayDtypeNames()
  if data_array_shape is None \
    or data_array_dtype is None \
    or data_array_shape in [(), (0,)]:
    return json.dumps(dict())

  RESPONSE.setHeader("Content-Type", "application/json")

  if data_type == 'bytes':
    return json.dumps(get_cdn_throughput(
      data_array, data_array_dtype, time_start, time_end))
