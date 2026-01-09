import json
import re
import numpy as np

MAX_PREV_CHUNK_SIZE = 1024 * 1024 # bytes
MAX_NEW_CHUNK_SIZE = 1024 * 1024 # bytes
HISTORY_LINE_COUNT = 64

in_data_stream = in_stream['Data Stream']
progress_indicator = in_stream['Progress Indicator']
offset_index = progress_indicator.getIntOffsetIndex()
start = max(0, offset_index - MAX_PREV_CHUNK_SIZE)
end = min(in_data_stream.getSize(), offset_index + MAX_NEW_CHUNK_SIZE)

frontend_log_data_array = None
if isinstance(out_array, dict):
  out_array = [out_array]

for array in out_array:
  if array['variation'] == 'frontend_log':
    frontend_log_data_array = array['Data Array']

# No new data to process
if offset_index >= end:
  return

previous_log_data = ''.join(
  [x.decode('utf-8') if isinstance(x, bytes) else x for x in in_data_stream.readChunkList(start, offset_index)]
)
new_log_data = ''.join([x.decode('utf-8') for x in in_data_stream.readChunkList(offset_index, end)])

previous_log_data_line_list = previous_log_data.splitlines()
new_log_data_line_list = new_log_data.splitlines()

# First previous log line may not be valid JSON due to MAX_PREV_CHUNK_SIZE:
# Simply discard it
previous_log_data_line_list = previous_log_data_line_list[1:]


# Last new log line may not be valid JSON due to MAX_NEW_CHUNK_SIZE:
last_new_log_data_line = new_log_data_line_list[-1]

match_dict = context.Base_parseFrontendLogLine(last_new_log_data_line)
if not match_dict:
  end -= len(last_new_log_data_line)
  new_log_data_line_list = new_log_data_line_list[:-1]

log_data_line_list = previous_log_data_line_list + new_log_data_line_list

parsed_data_list = context.Base_parseFrontendLogLineList(log_data_line_list)

frontend_log_data_dtype = np.dtype([
  ('utc', 'float'),
  ('bytes', 'float64'),
  ('status_code', 'float64'),
  ('request_time', 'float64')
])

frontend_log_array = frontend_log_data_array.getArray()
if not frontend_log_array:
  frontend_log_array = frontend_log_data_array.initArray(shape=(0,), dtype=frontend_log_data_dtype)
frontend_log_data = []

for log_entry in parsed_data_list:
  frontend_log_data.append((
    float(DateTime(log_entry['date_time'])),
    float(log_entry['bytes']),
    float(log_entry['status_code']),
    float(log_entry['request_time'])
  ))

if frontend_log_data:
  frontend_log_data = np.ndarray((len(frontend_log_data),), frontend_log_data_dtype, np.array(frontend_log_data))
  frontend_log_array.append(frontend_log_data)

progress_indicator.setIntOffsetIndex(end)
return
