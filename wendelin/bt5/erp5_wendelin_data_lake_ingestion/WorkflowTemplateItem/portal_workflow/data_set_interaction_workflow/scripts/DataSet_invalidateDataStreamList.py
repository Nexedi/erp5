"""
  Publish all Data Streams for a Data Set.
"""
data_set = state_change['object']
for data_stream in data_set.DataSet_getDataStreamList():
  data_stream.activate().invalidate()
