"""
This script is used during the ingestion of ORS eNB log files through fluentd.
It assumes data comes encoded in the following format: MsgPack(timestamp, data).
It will first unpack the MsgPack, then remove the first item of the tuple (timestamp),
get the actual data stored under the 'log' key and append the corresponding string to "Data Stream".
"""
unpacked_data = '\n'.join([c[1]["log"] for c in context.unpack(data_chunk)])
if unpacked_data == '':
  return

out_stream["Data Stream"].appendData((unpacked_data + '\n').encode('utf-8'))
