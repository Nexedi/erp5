import pandas as pd
import numpy as np

# Function to remove non-ASCII characters from a string, because I can not be bothered to make to_records with utf8 right now
def remove_non_ascii(text):
    return ''.join(char for char in str(text) if ord(char) < 128)



progress_indicator = in_stream["Progress Indicator"]
in_data_stream = in_stream["Data Bucket Stream"]
out_data_array = out_array["Data Array"]

keys = in_data_stream.getKeyList()

end = progress_indicator.getStringOffsetIndex()
if end is None:
  end = ""

if len(keys) == 0:
  context.log("No Keys found")
  return 


dtype= {'timestamp (ms)': '<f8',
'latitude ()': '<f8',
'longitude ()': '<f8',
'AMSL (m)': '<f8',
'rel altitude (m)': '<f8',
'yaw ()': '<f8',
'ground speed (m/s)': '<f8',
'climb rate (m/s)': '<f8'}

if len([x for x in keys if x not in end]) == 0:
  context.log("No new keys found")
  return

new_end = ""
for key in [x for x in keys if x not in end]:
  try:
    log = in_data_stream.getBucketByKey(key)
    df = pd.read_csv(log, sep=';', dtype=dtype)

    if df.shape[0] == 0:
      return
    
    # Remove non-ASCII characters from DataFrame values
    df = df.applymap(remove_non_ascii)
    # Remove non-ASCII characters from column names (headers)
    df.columns = df.columns.map(remove_non_ascii)
    non_numeric_columns = df.select_dtypes(exclude=[np.number]).columns
    df[non_numeric_columns] = df[non_numeric_columns].apply(pd.to_numeric, errors='coerce')

    ndarray = df.to_records(index = False) #column_dtypes does not work here for some reasone, even if it is an actuall parameter

    zbigarray = out_data_array.getArray()
    
    if zbigarray is None:
      zbigarray = out_data_array.initArray(shape=(0,), dtype=ndarray.dtype.fields)
    start_array = zbigarray.shape[0]
    zbigarray.append(ndarray)

    try:
      data_array_line = out_array.get(key)
      if data_array_line is None:
        data_array_line = out_data_array.newContent(id=key,
                                             portal_type="Data Array Line")
      data_array_line.edit(reference=key,
           index_expression="%s:%s" %(start_array, zbigarray.shape[0])
        )
    except:
      context.log("Can not create Data Array Line")
  except:
    context.log("File "+str(key)+ " is not well formated")
  new_end = new_end + str(key)


progress_indicator.setStringOffsetIndex(end + new_end)
