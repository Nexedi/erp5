""" 
  Read entire stream using activities either in a sequence or in a oarallel mode.
  Pass stream's data to handler script  who can transform it.
  Parameters:
    * transform_script_id - the script which will transform data
    * chunk_length - the length of a chunk
    * data_array_reference - the reference of the output Data Array
    * parallelize - try to transform in parallel or not, in this case
      developer must carefully choose chunk_length to match record (s) size
"""
start = 0
end  = chunk_length
if not parallelize:
  # sequential case
  context.activate().DataStream_readChunkListAndTransform( \
    start, \
    end, \
    chunk_length, \
    transform_script_id, \
    data_array_reference,\
    recursive =1, \
    **kw)
else:
  # parallel case
  total_size =  context.getSize()
  while total_size > start:
    start += chunk_length + 1
    end += chunk_length +1
    if end > total_size:
      end = total_size
      
    # call transformation in an activity
    context.activate(activity='SQLQueue').DataStream_readChunkListAndTransform( \
      start, \
      end, \
      chunk_length, \
      transform_script_id, \
      data_array_reference,\
      recursive = 0, \
      **kw)
