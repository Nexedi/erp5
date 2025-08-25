import json
import numpy as np
import pandas as pd

QCI_COUNT = 256
# The maximum number of points to show on a KPI graph
RESAMPLE_SIZE = 1000
# Values with which to replace NaNs for each data field
NA_VALUES_REPLACEMENTS = {
  'vInitialEPSBEstabSR_lo': 0.,
  'vInitialEPSBEstabSR_hi': 100.,
  'vAddedEPSBEstabSR_lo': 0.,
  'vAddedEPSBEstabSR_hi': 100.,
  'dl_lo': 0.,
  'dl_hi': 0.,
  'ul_lo': 0.,
  'ul_hi': 0.
}

def compute_positive_delta(nparray):
  '''
     Computes the positive delta (increase) between consecutive elements in an
     array. Negative differences are set to zero (In case).
  '''
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
  return data_frame

def get_e_utran_ip_throughput_kpi(data_array, data_array_dtype, time_start=None, time_end=None):
  '''
    Return the requested KPI data in the response as a JSON object
    with the data arrays keyed to their respective data fields.
    Several optimizations are made:
    - If required, the data will be resampled to at most RESAMPLE_SIZE data points.
    - For the E-UTRAN IP Throughput KPI, only fetch and send data for "active" QCIs,
    which is typically only 1 out of all 256 for an ORS.
  '''

  evt = []
  active_qci = []
  dl_lo = []
  dl_hi = []
  ul_lo = []
  ul_hi = []

  for data_array_line in data_array.contentValues(portal_type='Data Array Line'):
    line_id_split = data_array_line.getId().split('_')
    if not (len(line_id_split) == 3 \
      and line_id_split[0] == 'active' \
      and line_id_split[1] == 'qci'):
      continue

    qci = int(line_id_split[2])
    active_qci.append(qci)

    qci_data_zarray = data_array_line.getArray()[:]
    time_field = data_array_line.getArrayDtypeNames()[0]
    qci_data_zarray, time_start, time_end = get_data_zarray_in_time_range(
      qci_data_zarray, time_field, time_start, time_end
    )

    resampled_qci_data_dict = resample_data_zarray(
      qci_data_zarray,
      time_field,
      time_start,
      time_end,
      RESAMPLE_SIZE
    ).to_dict(orient='list')
    evt = resampled_qci_data_dict['evt']
    qci_dl_lo = resampled_qci_data_dict['dl_lo']
    qci_dl_hi = resampled_qci_data_dict['dl_hi']
    qci_ul_lo = resampled_qci_data_dict['ul_lo']
    qci_ul_hi = resampled_qci_data_dict['ul_hi']

    dl_lo.append(qci_dl_lo)
    dl_hi.append(qci_dl_hi)
    ul_lo.append(qci_ul_lo)
    ul_hi.append(qci_ul_hi)

  response_dict = dict(
    evt=evt,
    active_qci=active_qci,
    dl_lo=dl_lo,
    dl_hi=dl_hi,
    ul_lo=ul_lo,
    ul_hi=ul_hi
  )
  return json.dumps(response_dict)

def get_ue_count_per_cell(data_array, data_array_dtype, time_start, time_end):
  data_zarray = data_array.getArray()[:]
  time_field = data_array_dtype[0]
  data_zarray, time_start, time_end = get_data_zarray_in_time_range(
    data_zarray, time_field, time_start, time_end
  )

  data_frame = pd.DataFrame.from_records(data_zarray)
  data_frame[time_field] = pd.to_datetime(data_frame[time_field], unit='s')
  data_frame = data_frame.sort_values(by=time_field)

  # Resample data if array is too large
  if len(data_zarray) > RESAMPLE_SIZE:
    resample_period = '%ss' % int((time_end - time_start) / RESAMPLE_SIZE)
    data_frame = data_frame.set_index(time_field)

     # Get numeric columns and remove cell_id_field explicitly
    value_columns = data_frame.select_dtypes(include=[np.number]).columns.tolist()
    value_columns = [col for col in value_columns if col != 'cell_id']

    # Group by cell_id_field and resample
    data_frame = (
        data_frame
        .groupby('cell_id')
        .resample(resample_period)
        [value_columns]
        .mean()
        .reset_index()
    )

    data_frame = data_frame.fillna(value=NA_VALUES_REPLACEMENTS)

  data_frame = data_frame.reset_index()
  data_frame[time_field] = data_frame[time_field].map(pd.Timestamp.timestamp)

  response_dict = {
     cell: group.reset_index(drop=True).to_dict(orient='list') \
       for cell, group in data_frame.groupby('cell_id')
  }

  base_resampled_data_array = data_frame.groupby(time_field).agg({
    'ue_count_max': 'max',
    # XXX Not sure if this is properly defined.
    'ue_count_min': 'min',
    'ue_count_avg': 'mean'}).reset_index()

  base_resampled_data_dict = base_resampled_data_array.to_dict(orient='list')
  response_dict['base'] = {
      'utc': base_resampled_data_dict['utc'],
      'ue_count_max': base_resampled_data_dict['ue_count_max'],
      'ue_count_min': base_resampled_data_dict['ue_count_min'],
      'ue_count_avg': base_resampled_data_dict['ue_count_avg']
  }

  return response_dict

def get_rrc_per_cell(data_array, data_array_dtype, time_start, time_end, column_list):
  data_zarray = data_array.getArray()[:]
  time_field = data_array_dtype[0]
  data_zarray, time_start, time_end = get_data_zarray_in_time_range(
    data_zarray, time_field, time_start, time_end
  )

  data_frame = pd.DataFrame.from_records(data_zarray)
  data_frame[time_field] = pd.to_datetime(data_frame[time_field], unit='s')
  data_frame = data_frame.sort_values(by=time_field)

  # Resample data if array is too large
  if len(data_zarray) > RESAMPLE_SIZE:
    resample_period = '%ss' % int((time_end - time_start) / RESAMPLE_SIZE)
    data_frame = data_frame.set_index(time_field)
    # Get numeric columns and remove cell_id_field explicitly
    value_columns = data_frame.select_dtypes(include=[np.number]).columns.tolist()
    value_columns = [col for col in value_columns if col != 'cell_id']

    # Group by cell_id_field and resample
    data_frame = (
        data_frame
        .groupby('cell_id')
        .resample(resample_period)
        [value_columns]
        .mean()
        .reset_index()
    )

    data_frame = data_frame.fillna(value=NA_VALUES_REPLACEMENTS)

  data_frame = data_frame.reset_index()
  data_frame[time_field] = data_frame[time_field].map(pd.Timestamp.timestamp)

  # Transform absolute to delta:
  for column in column_list:
    data_frame[column] = data_frame.sort_values(by=['cell_id', time_field]).groupby('cell_id')[column].transform(compute_positive_delta)

  _group_column_list = [time_field]
  _group_column_list.extend(column_list)
  response_dict = {
     cell: group[_group_column_list].reset_index(drop=True).to_dict(orient='list') \
       for cell, group in data_frame.groupby('cell_id')
  }

  base_resampled_data_dict = (
    data_frame
    .groupby(time_field)
    .agg({i: 'sum' for i in column_list})
    .reset_index()
    .to_dict(orient='list')
  )

  response_dict['base'] = {
      'utc': base_resampled_data_dict['utc']
  }

  for column in column_list:
    response_dict['base'][column] = base_resampled_data_dict[column]

  return response_dict

def get_rrc_paging(data_array, data_array_dtype, time_start, time_end, column):
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

  # Transform absolute to delta:
  data_frame = data_frame.groupby(time_field).agg({
    column: 'max'}).reset_index()

  # Compute positive delta
  data_frame[column] = compute_positive_delta(data_frame[column])

  q1 = data_frame[column].quantile(0.25)
  q3 = data_frame[column].quantile(0.75)
  iqr = q3 - q1

  lower_bound = q1 - 1.5 * iqr
  upper_bound = q3 + 1.5 * iqr

  # Remove what is out of the interval
  data_frame = data_frame[
      (data_frame[column] >= lower_bound) & (data_frame[column] <= upper_bound)
  ]

  base_resampled_data_dict = data_frame.to_dict(orient='list')
  response_dict = {
    'base': {
      'utc': base_resampled_data_dict['utc'],
      column: base_resampled_data_dict[column]
    }
  }
  return response_dict

def getMergedDataArrayForDataTypeAsJSON(self, first_data_array_url,
  second_data_array_url, data_type, time_start=None, time_end=None,
  REQUEST=None, RESPONSE=None):
  """
  """
  portal = self.getPortalObject()

  try:
    first_data_array = portal.restrictedTraverse(first_data_array_url)
  except KeyError:
    # Data Array does not exist
    RESPONSE.setStatus(404)
    return

  try:
    second_data_array = portal.restrictedTraverse(second_data_array_url)
  except KeyError:
    # Data Array does not exist
    RESPONSE.setStatus(404)
    return

  first_data_array_shape = first_data_array.getArrayShape()
  first_data_array_dtype = first_data_array.getArrayDtypeNames()

  # Data Array is empty
  if first_data_array_shape is None \
    or first_data_array_dtype is None \
    or first_data_array_shape in [(), (0,)]:
    return json.dumps(dict())

  second_data_array_shape = second_data_array.getArrayShape()
  second_data_array_dtype = second_data_array.getArrayDtypeNames()

  # Data Array is empty
  if second_data_array_shape is None \
    or second_data_array_dtype is None \
    or second_data_array_shape in [(), (0,)]:
    return json.dumps(dict())

  RESPONSE.setHeader("Content-Type", "application/json")

  if data_type == 'ue_rrc':
    # This probably quite non-optimal, but this seems "fast enough" considering
    # data considerations. This does some optimistic take since considering that
    # both array have the same origin, so times and utc will match for sure.

    response_dict = get_ue_count_per_cell(
      first_data_array, first_data_array_dtype, time_start, time_end)

    rrc_dict = get_rrc_per_cell(
      second_data_array, second_data_array_dtype,
      time_start, time_end, ['rrc_con_req'])

    for cell_id in response_dict:
      response_dict[cell_id]['rrc_con_req'] = rrc_dict[cell_id]['rrc_con_req']
    return json.dumps(response_dict)


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

  if data_type == 'e_utran_ip_throughput':
    return get_e_utran_ip_throughput_kpi(
      data_array, data_array_dtype, time_start, time_end)


  if data_type == 'e_rab_accessibility':
    # Return the requested KPI data in the response as a JSON object
    # with the data arrays keyed to their respective data fields.
    # Several optimizations are made:
    # - If required, the data will be resampled to at most RESAMPLE_SIZE data points.
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
    ).to_dict(orient='list')

    return json.dumps(
      dict(
        vt=resampled_data_dict['vt'],
        v_initial_epsb_estab_sr_lo=resampled_data_dict['vInitialEPSBEstabSR_lo'],
        v_initial_epsb_estab_sr_hi=resampled_data_dict['vInitialEPSBEstabSR_hi'],
        v_added_epsb_estab_sr_lo=resampled_data_dict['vAddedEPSBEstabSR_lo'],
        v_added_epsb_estab_sr_hi=resampled_data_dict['vAddedEPSBEstabSR_hi']
     ))

  if data_type == 'ue_count':
    return json.dumps(get_ue_count_per_cell(
      data_array, data_array_dtype, time_start, time_end))

  if data_type == 'rrc_connection_request':
    return json.dumps(get_rrc_per_cell(
      data_array, data_array_dtype, time_start, time_end, ['rrc_con_req']))

  if data_type == 'rrc_paging':
    return json.dumps(get_rrc_paging(
      data_array, data_array_dtype, time_start, time_end, 'rrc_paging'))

  if data_type == 'unsuccessful_rrc_con_att':
    resampled_data_dict = get_rrc_per_cell(
      data_array, data_array_dtype,
      time_start, time_end, ['rrc_con_req', 'rrc_recon_com'])

    response_dict = {}
    for cell_id in resampled_data_dict:
      rrc_con_req = np.asarray(resampled_data_dict[cell_id]['rrc_con_req'], dtype=float)
      rrc_recon_com = np.asarray(resampled_data_dict[cell_id]['rrc_recon_com'], dtype=float)

      with np.errstate(divide='ignore', invalid='ignore'):
        delta_rate = ((rrc_con_req - rrc_recon_com) / rrc_con_req) * 100
        # Clamp between 0 and 100
        delta_clipped = np.clip(delta_rate, 0, 100)
        unsucessful_rrc_recon = np.where(rrc_con_req > 0, delta_clipped, 0)

      response_dict[cell_id] = dict(
        utc=resampled_data_dict[cell_id]['utc'],
        unsucessful_rrc_recon=unsucessful_rrc_recon.tolist()
      )

    return json.dumps(response_dict)

  if data_type == 'failure_rrc_security_mode':
    resampled_data_dict = get_rrc_per_cell(
      data_array, data_array_dtype,
      time_start, time_end, ['rrc_sec_command', 'rrc_sec_complete'])

    response_dict = {}
    for cell_id in resampled_data_dict:
      rrc_sec_command = np.asarray(resampled_data_dict[cell_id]['rrc_sec_command'], dtype=float)
      rrc_sec_complete = np.asarray(resampled_data_dict[cell_id]['rrc_sec_complete'], dtype=float)

      with np.errstate(divide='ignore', invalid='ignore'):
        delta_rate = ((rrc_sec_command - rrc_sec_complete) / rrc_sec_command) * 100
        # Clamp between 0 and 100
        delta_clipped = np.clip(delta_rate, 0, 100)
        failure_rate_rrc_sec = np.where(rrc_sec_command > 0, delta_clipped, 0)

      response_dict[cell_id] = dict(
        utc=resampled_data_dict[cell_id]['utc'],
        failure_rate_rrc_sec=failure_rate_rrc_sec.tolist()
      )

    return json.dumps(response_dict)
