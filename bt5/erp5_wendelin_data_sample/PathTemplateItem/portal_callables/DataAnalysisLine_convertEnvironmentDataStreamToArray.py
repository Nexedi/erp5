import pandas as pd

progress_indicator = in_stream["Progress Indicator"]
in_data_stream = in_stream["Data Stream"]
out_data_array = out_array["Data Array"]

chunk_size = 20 * 10**6
start = progress_indicator.getIntOffsetIndex()
end = min(start+chunk_size, in_data_stream.getSize())

unpacked, end = in_data_stream.readMsgpackChunkList(start, end)
f = in_data_stream.extractDateTime
df = pd.DataFrame((dict(**o[1]) for o in unpacked), dtype="float64", index=(f(o[0]) for o in unpacked))

if df.shape[0] == 0:
  return

df.index.name="date"

ndarray = df.to_records(convert_datetime64=False)

zbigarray = out_data_array.getArray()
if zbigarray is None:
  zbigarray = out_data_array.initArray(shape=(0,), dtype=ndarray.dtype.fields)

zbigarray.append(ndarray)

if end > start:
  progress_indicator.setIntOffsetIndex(end)

# tell caller to create new activity after processing if we did not reach end of stream
if end < in_data_stream.getSize():
  return 1
