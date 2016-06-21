"""
  Handle appended data chunks.
"""
data_stream = state_change['object']
argument_list = state_change['kwargs']['workflow_method_args']

# call you own script to handle newly appended data which 
# is not processed yet, pass data stream start end offset only
end_offset = data_stream.getSize()
packet_size = len(argument_list[0])
start_offset = end_offset - packet_size
data_stream.activate().DataStream_transformTail(start_offset, end_offset)
