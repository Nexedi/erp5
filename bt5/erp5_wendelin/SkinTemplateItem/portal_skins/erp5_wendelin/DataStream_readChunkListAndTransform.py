"""
  Simply a wrapper to real method.
"""

total_stream_length = context.getSize()

if start > total_stream_length:
  # end reached
  return

data_stream_chunk_list = context.readChunkList(start, end)

# do call transformation script
if transform_script_id is not None:
  transform_script = getattr(context, transform_script_id, None)
  if transform_script is not None:
    start, end = transform_script(context, data_stream_chunk_list, \
                                  start, \
                                  end, \
                                  data_array_reference, \
                                  **kw)
  else:
    # transformation script can not be found thus raise loudly
    raise ValueError("Transformation script: %s can not be found." \
                        %transform_script_id)

# [warning] store current position offset in Data Stream, this can cause easily 
# ConflictErrors and it spawns re-index activities on DataStream. Thus 
# disable for now.
#context.setIntOffsetIndex(end)

# start another read in another activity
start += chunk_length
end += chunk_length

if end > total_stream_length:
  # no read beyond end of stream
  end = total_stream_length

if recursive:
  # some bytes left ...
  context.activate().DataStream_readChunkListAndTransform( \
    start, \
    end, \
    chunk_length, \
    transform_script_id,\
    data_array_reference,\
    recursive = recursive, \
    **kw)
