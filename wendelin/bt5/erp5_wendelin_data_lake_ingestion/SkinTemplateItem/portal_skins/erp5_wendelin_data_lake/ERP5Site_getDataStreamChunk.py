try:
  start_offset = int(float(start_offset))
  end_offset = int(float(end_offset))
  data_stream = context.restrictedTraverse(id)
  data_stream_chunk = ''.join(data_stream.readChunkList(start_offset, end_offset))
  return data_stream_chunk
except Exception as e:
  context.logEntry("Exception getting Data Stream (id '%s') content: %s." % (id, str(e)))
  raise e
