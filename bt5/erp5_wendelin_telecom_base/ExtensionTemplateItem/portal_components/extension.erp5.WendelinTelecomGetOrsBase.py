import json
import numpy as np
import pandas as pd

# Why now?

# The maximum number of points to show on a KPI graph
RESAMPLE_SIZE = 1000
# Values with which to replace NaNs for each data field
NA_VALUES_REPLACEMENTS = {}

def compute_positive_delta(nparray):
  nparray = np.asarray(nparray, dtype=float)
  # Compute the difference between current and previous elements
  computed_delta = np.diff(nparray, prepend=nparray[0])
  computed_delta[computed_delta < 0] = 0
  computed_delta[0] = 0

  return computed_delta

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

  # Resample data if array is too large
  if len(np_data_zarray) > resample_size:
    resample_period = '%ss' % int((time_end - time_start) / resample_size)
    data_frame = data_frame.resample(resample_period, on=time_field).mean()
    data_frame = data_frame.fillna(value=NA_VALUES_REPLACEMENTS)

  data_frame = data_frame.reset_index()
  data_frame[time_field] = data_frame[time_field].map(pd.Timestamp.timestamp)
  return data_frame.to_dict(orient='list')

def getOrsEnbUeCount(
  self, data_array_url, kpi_type,
  time_start=None, time_end=None, REQUEST=None, RESPONSE=None
):
  '''
     If this still here, rafael forgot to write it.
  '''
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

  data_zarray = data_array.getArray()[:]
  time_field = data_array_dtype[0]
  data_zarray, time_start, time_end = get_data_zarray_in_time_range(
    data_zarray, time_field, time_start, time_end
  )

  resampled_data_dict = resample_data_zarray(
    data_zarray,
    time_field,
    time_start,
    time_end,
    RESAMPLE_SIZE
  )
  if kpi_type == 'ue_count':
    response_dict = dict(
      utc=resampled_data_dict['utc'],
      ue_count_max=resampled_data_dict['ue_count_max'],
      ue_count_min=resampled_data_dict['ue_count_min'],
      ue_count_avg=resampled_data_dict['ue_count_avg']
    )
    return json.dumps(response_dict)

  if kpi_type == 'rrc_connection_request':
    response_dict = dict(
      utc=resampled_data_dict['utc'],
      rrc_con_req=compute_positive_delta(resampled_data_dict['rrc_con_req']).tolist()
    )
    return json.dumps(response_dict)

  if kpi_type == 'ue_rrc':
    response_dict = dict(
      utc=resampled_data_dict['utc'],
      ue_count_max=resampled_data_dict['ue_count_max'],
      ue_count_min=resampled_data_dict['ue_count_min'],
      ue_count_avg=resampled_data_dict['ue_count_avg'],
      rrc_con_req=compute_positive_delta(resampled_data_dict['rrc_con_req']).tolist()
    )
    return json.dumps(response_dict)

  if kpi_type == 'rrc_paging':
    utc = resampled_data_dict['utc']
    rrc_paging_delta = compute_positive_delta(resampled_data_dict['rrc_paging'])

    response_dict = dict(
      utc=utc,
      rrc_paging=rrc_paging_delta.tolist()
    )

    # Remove extreme values using IQR (Interquartile Range)
    #q1, q3 = np.percentile(rrc_paging_delta, [25, 75])
    #iqr = q3 - q1
    #lower_bound = q1 - 1.5 * iqr
    #upper_bound = q3 + 1.5 * iqr

    #filtered_utc = []
    #filtered_rrc_paging_delta = []

    #for i in range(len(rrc_paging_delta)):
    #  if lower_bound <= rrc_paging_delta[i] <= upper_bound:
    #    filtered_utc.append(utc[i])
    #    filtered_rrc_paging_delta.append(rrc_paging_delta[i])

    #response_dict = dict(
    #  utc=filtered_utc,
    #  rrc_paging=filtered_rrc_paging_delta
    #)

    return json.dumps(response_dict)

  if kpi_type == 'unsuccessful_rrc_con_att':
    rrc_con_req=compute_positive_delta(resampled_data_dict['rrc_con_req'])
    rrc_recon_com=compute_positive_delta(resampled_data_dict['rrc_recon_com'])
    with np.errstate(divide='ignore', invalid='ignore'):
      unsucessful_rrc_recon = np.where(
        rrc_con_req > 0,
        ((rrc_con_req - rrc_recon_com)/rrc_con_req)*100,
        0
      )
    response_dict = dict(
      utc=resampled_data_dict['utc'],
      unsucessful_rrc_recon=unsucessful_rrc_recon.tolist()
    )
    return json.dumps(response_dict)


  if kpi_type == 'failure_rrc_security_mode':
    rrc_sec_command=compute_positive_delta(resampled_data_dict['rrc_sec_command'])
    rrc_sec_complete=compute_positive_delta(resampled_data_dict['rrc_sec_complete'])
    with np.errstate(divide='ignore', invalid='ignore'):
      failure_rate_rrc_sec = np.where(
        rrc_sec_command > 0,
        ((rrc_sec_command - rrc_sec_complete)/rrc_sec_command)*100,
        0
      )
    response_dict = dict(
      utc=resampled_data_dict['utc'],
      failure_rate_rrc_sec=failure_rate_rrc_sec.tolist()
    )
    return json.dumps(response_dict)

