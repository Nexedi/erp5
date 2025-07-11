"""
This script is used during fluentd ingestion. 
It assumes data comes in msgpack encoded in the following format: mspack(timestamp, data). 
It will first unpack the msgpack, then remove the first item of the tuple (timestamp) and 
append str(data) to "Data Stream".

Note that what is saved to Data Stream might be different from what fluentd was reading 
initially, depending on fluentd plugin configuration. For example fluentd might convert 
json to msgpack, then what is saved in Data Stream might be str(python_dict) and not json.
"""

unpacked_data = ''.join([str(c[1]) for c in context.unpack(data_chunk)])
out_stream["Data Stream"].appendData(unpacked_data.encode('utf-8'))
