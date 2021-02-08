import numpy as np
import pandas as pd

out_array_list = out_array

in_data_array = in_array["Data Array"]
progress_indicator = in_array["Progress Indicator"]

in_zbigarray = in_data_array.getArray()
if in_zbigarray is None:
  return

if in_zbigarray.shape[0] == 0:
  return

# first fill array with lowest resolution
default_data_array = out_array_list[0]["Data Array"]
default_resolution = out_array_list[0]["resolution"]
default_frequency = pd.to_timedelta(default_resolution)
default_zbigarray = default_data_array.getArray()

index = progress_indicator.getIntOffsetIndex()

# convert data to DataFrame
df = pd.DataFrame.from_records(in_zbigarray[index:].copy(), index='date')

# ignore data before start date of output array
if default_zbigarray is not None:
  if default_zbigarray.shape[0] != 0:
    df = df.loc[str(default_zbigarray[0]['date']):]

if len(df) == 0:
  return

# resample
df = df.resample(default_resolution).agg(['min','mean','max']).fillna(0)

# rename columns from tuples like ('x', 'min') to names like 'x_min'
df.columns = ['%s%s' % (a, '_%s' % b if b else '') for a, b in df.columns]

context.log("df.columns = ", df.columns)

# save date vector for later
date_vector = df.index.values.copy()

context.log("date_vector = ", date_vector)

# convert data back to ndarray
default_data = df.to_records(convert_datetime64=False)
# view as structured array

# set date to zero where all values are 0
mask_zero = (df==0).all(axis=1)
default_data['date'][mask_zero] = 0

if default_zbigarray is None:
  default_zbigarray = default_data_array.initArray(shape=(0,), dtype=default_data.dtype.fields)

if default_zbigarray.shape[0] == 0:
  default_zbigarray.append(default_data)

else:
 # calculate start and stop index of new data in output array
  default_start_index = int((date_vector[0] - default_zbigarray[0]['date']) / default_frequency)
  default_stop_index = int((date_vector[-1] - default_zbigarray[0]['date']) / default_frequency + 1)

 # make sure data fits in
  if default_stop_index > default_zbigarray.shape[0]:
    default_zbigarray.resize((default_stop_index,))

 # fill holes in new data with values from old data
  old_data = default_zbigarray[default_start_index:default_stop_index]
  default_data[mask_zero ] = old_data[mask_zero]

 # write new_data to zbigarray
  default_zbigarray[default_start_index:default_stop_index] = default_data


# now use data in first resolution array for all other arrays
for out_array in out_array_list[1:]:
  out_data_array = out_array["Data Array"]
  out_array_resolution = out_array["resolution"]
  out_zbigarray = out_data_array.getArray()
  if out_zbigarray is None:
    out_zbigarray = out_data_array.initArray(shape=(0,), dtype=default_data.dtype.fields)

  if out_zbigarray.shape[0] == 0:
    start_index = 0
  else:
    out_array_frequency = pd.to_timedelta(out_array_resolution)

    new_stop_date = default_zbigarray[0]['date'] + default_zbigarray.shape[0] * default_frequency
    old_stop_date = out_zbigarray[0]['date'] + out_zbigarray.shape[0] * out_array_frequency

    start_date = old_stop_date - out_array_frequency
    if old_stop_date >= new_stop_date:
      continue

 # find row index in in_array from where to start resampling
    start_index = int(max((start_date - default_zbigarray[0]['date']) / default_frequency, 0))
 # if we got data which has been already resampled, then we resample again and overwrite
    start_index = min(start_index, default_start_index)

  data = default_zbigarray[start_index:].copy()

 # convert data to DataFrame and resample
  df = pd.DataFrame.from_records(data, index='date')

 # set our own date range index so that we can resample and keep 0-dates
  resampling_start_date = default_zbigarray[0]['date'] + start_index * default_frequency
  df.index = pd.date_range(start=resampling_start_date,
 periods=data.shape[0],
 freq=default_frequency)
  df.index.name = 'date'

 # resample each column with appropriate aggregation method
  aggregation_dict = {c: c.split('_')[-1] for c in df.columns}
  df = df.resample(out_array_resolution).agg(aggregation_dict).fillna(0)

 # save date vector for later
  date_vector = df.index.values.copy()

 # convert data back to ndarray
  new_data = df.to_records(convert_datetime64=False)

 # set date to zero where all values are 0
  new_data['date'][(df==0).all(axis=1)] = 0

  if out_zbigarray.shape[0] == 0:
    out_zbigarray.append(new_data)
  else:
 # calculate start and stop index of new data in output array
    start_index = int((date_vector[0] - out_zbigarray[0]['date']) / out_array_frequency)
    stop_index = int((date_vector[-1] - out_zbigarray[0]['date']) / out_array_frequency + 1)

progress_indicator.setIntOffsetIndex(in_zbigarray.shape[0])
