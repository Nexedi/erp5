"""
  This script is a general ingestion script which can be used with fluentd or with other http based ingestion tools.
  It will append data sent to Wendelin 'as it is' to respective "Data Stream".

  Note that by default fluentd data is encoded in msgpack format, this script will not unpack it.
"""

out_stream["Data Stream"].appendData(data_chunk)
