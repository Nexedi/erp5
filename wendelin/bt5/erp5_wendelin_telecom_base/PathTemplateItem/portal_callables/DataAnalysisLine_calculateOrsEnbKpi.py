import json
import numpy as np

MAX_PREV_CHUNK_SIZE = 1024 * 1024 # bytes
MAX_NEW_CHUNK_SIZE = 1024 * 1024 # bytes
HISTORY_LINE_COUNT = 64
T_PERIOD = 30 # seconds
QCI_COUNT = 256

in_data_stream = in_stream['Data Stream']
progress_indicator = in_stream['Progress Indicator']
offset_index = progress_indicator.getIntOffsetIndex()
start = max(0, offset_index - MAX_PREV_CHUNK_SIZE)
end = min(in_data_stream.getSize(), offset_index + MAX_NEW_CHUNK_SIZE)

e_rab_data_array = None
e_utran_data_array = None
for array in out_array:
  if array['variation'] == 'e_rab':
    e_rab_data_array = array['Data Array']
  if array['variation'] == 'e_utran':
    e_utran_data_array = array['Data Array']

# Queue active QCI updating in all cases
e_utran_data_array.activate().DataArray_updateActiveQciLines()

# No new data to process
if offset_index >= end:
  return

previous_log_data = ''.join(in_data_stream.readChunkList(start, offset_index))
new_log_data = ''.join(in_data_stream.readChunkList(offset_index, end))

previous_log_data_line_list = previous_log_data.splitlines()
new_log_data_line_list = new_log_data.splitlines()

# First previous log line may not be valid JSON due to MAX_PREV_CHUNK_SIZE:
# Simply discard it
previous_log_data_line_list = previous_log_data_line_list[1:]

# Last new log line may not be valid JSON due to MAX_NEW_CHUNK_SIZE:
# In that case, leave it to the next KPI calculation
last_new_log_data_line = new_log_data_line_list[-1]
try:
  json.loads(last_new_log_data_line)
except ValueError:
  end -= len(last_new_log_data_line)
  new_log_data_line_list = new_log_data_line_list[:-1]

log_data_line_list = previous_log_data_line_list + new_log_data_line_list

# Remove duplicate log lines
seen_hash_list = []
for i, log_line in enumerate(log_data_line_list):
  log_line_hash = hash(log_line)
  if log_line_hash in seen_hash_list:
    del log_data_line_list[i]
  else:
    seen_hash_list.append(log_line_hash)

# Sort data lines by UTC timestamp
def get_log_line_timestamp(log_line):
  try:
    log_line_json = json.loads(log_line)
  except ValueError:
    # Invalid JSON
    return 0.0
  if 'meta' in log_line_json:
    if 'srv_utc' in log_line_json['meta']:
      return float(log_line_json['meta']['srv_utc'])
    else:
      return float(log_line_json['meta']['time'])
  else:
    return float(log_line_json.get('utc', 0.0))
log_data_line_list.sort(key=get_log_line_timestamp)

# Find the index of the earliest timestamp in the new data
new_log_data_line_first_index = min([
  log_data_line_list.index(new_log_line) for new_log_line in new_log_data_line_list
])

# Use partial history of previous logs starting from the earliest timestamp of the new data
# This also gives some tolerance to log errors
history_start_index = max(0, new_log_data_line_first_index - HISTORY_LINE_COUNT)

log_data = '\n'.join(log_data_line_list[history_start_index:])
log_data = log_data.decode('utf8')

# Calculate the KPI data
kpi_data_dict = context.Base_calcEnbKpi(log_data, T_PERIOD)
vt, v_initial_epsb_estab_sr, v_added_epsb_estab_sr = kpi_data_dict['e_rab_accessibility']
evt, v_ip_throughput_qci = kpi_data_dict['e_utran_ip_throughput']

e_rab_dtype = np.dtype([
  ('vt', 'float'),
  ('vInitialEPSBEstabSR_lo', 'float64'),
  ('vInitialEPSBEstabSR_hi', 'float64'),
  ('vAddedEPSBEstabSR_lo', 'float64'),
  ('vAddedEPSBEstabSR_hi', 'float64'),
])
e_utran_dtype = np.dtype([
  ('evt', 'float'),
  ('dl_lo', 'float64'),
  ('dl_hi', 'float64'),
  ('ul_lo', 'float64'),
  ('ul_hi', 'float64'),
])

e_rab_array = e_rab_data_array.getArray()
if not e_rab_array:
  e_rab_array = e_rab_data_array.initArray(shape=(0,), dtype=e_rab_dtype)
e_rab_array_data = []

e_utran_array = e_utran_data_array.getArray()
if not e_utran_array:
  e_utran_array = e_utran_data_array.initArray(shape=(0,), dtype=e_utran_dtype)
e_utran_array_data = []

# Don't duplicate KPI data:
# search and start inserting new timestamps from the first one
vt_column = e_rab_array[:]['vt']
first_new_row_vt = 0
while (first_new_row_vt < len(vt) and vt[first_new_row_vt] in vt_column):
  first_new_row_vt += 1

for i in range(first_new_row_vt, len(vt)):
  if vt[i] not in vt_column:
    e_rab_array_data.append((
      vt[i],
      v_initial_epsb_estab_sr[i][0],
      v_initial_epsb_estab_sr[i][1],
      v_added_epsb_estab_sr[i][0],
      v_added_epsb_estab_sr[i][1]
    ))

evt_column = e_utran_array[::QCI_COUNT]['evt']
first_new_row_evt = 0
while (first_new_row_evt < len(evt) and evt[first_new_row_evt] in evt_column):
  first_new_row_evt += 1

for i in range(first_new_row_evt, len(evt)):
  if evt[i] not in evt_column:
    for qci_data in v_ip_throughput_qci[i]:
      e_utran_array_data.append((evt[i], qci_data[0], qci_data[1], qci_data[2], qci_data[3]))

if e_rab_array_data:
  e_rab_array_data = np.ndarray((len(e_rab_array_data),), e_rab_dtype, np.array(e_rab_array_data))
  e_rab_array.append(e_rab_array_data)

if e_utran_array_data:
  e_utran_array_data = np.ndarray((len(e_utran_array_data),), e_utran_dtype, np.array(e_utran_array_data))
  e_utran_array.append(e_utran_array_data)

progress_indicator.setIntOffsetIndex(end)
return
