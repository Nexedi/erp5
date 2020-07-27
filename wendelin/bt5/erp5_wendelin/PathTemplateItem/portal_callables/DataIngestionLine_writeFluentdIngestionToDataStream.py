"""
  This script is used during fluentd ingestion.
  It will write data sent from fluentd by unpacking it first and then appending
  as a string to respective "Data Stream".
"""

out_stream["Data Stream"].appendData(''.join([str(c[1]) for c in context.unpack(data_chunk)]))
