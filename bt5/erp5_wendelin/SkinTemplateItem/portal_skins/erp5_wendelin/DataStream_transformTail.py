"""
  Read tail of a Data Stream and aplly needed transformations.
  This script is called every time we appendData to a Stream
  using data_stream_interaction_workflow.
  
  The idea is to provide close to real time data transformations.
  As transformation is quite specific we leave this script empty so developers
  can hook in and add needed transformations.
"""
assert start_offset < end_offset
