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

def getOrsEnbKpi(
  self, data_array_url, kpi_type,
  time_start=None, time_end=None, REQUEST=None, RESPONSE=None
):
  '''
    Return the requested KPI data in the response as a JSON object
    with the data arrays keyed to their respective data fields.
    Several optimizations are made:
    - If required, the data will be resampled to at most RESAMPLE_SIZE data points.
    - For the E-UTRAN IP Throughput KPI, only fetch and send data for "active" QCIs,
    which is typically only 1 out of all 256 for an ORS.
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

  if kpi_type == 'e_rab_accessibility':
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
    response_dict = dict(
      vt=resampled_data_dict['vt'],
      v_initial_epsb_estab_sr_lo=resampled_data_dict['vInitialEPSBEstabSR_lo'],
      v_initial_epsb_estab_sr_hi=resampled_data_dict['vInitialEPSBEstabSR_hi'],
      v_added_epsb_estab_sr_lo=resampled_data_dict['vAddedEPSBEstabSR_lo'],
      v_added_epsb_estab_sr_hi=resampled_data_dict['vAddedEPSBEstabSR_hi']
    )
    return json.dumps(response_dict)

  elif kpi_type == 'e_utran_ip_throughput':
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
      )
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