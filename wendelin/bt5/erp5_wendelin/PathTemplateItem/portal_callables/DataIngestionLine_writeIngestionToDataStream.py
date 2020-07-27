"""
  This script is used during fluentd ingestion.
  It will append data sent from fluentd to Wendelin 'as it is' to respective "Data Stream".
  By default data will be encoded in MsgPack format.
"""

out_stream["Data Stream"].appendData(data_chunk)
