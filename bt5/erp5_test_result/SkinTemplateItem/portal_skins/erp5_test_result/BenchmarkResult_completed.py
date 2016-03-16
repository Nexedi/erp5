error_counter = 0
for benchmark_result_line in context.contentValues(portal_type='Benchmark Result Line'):
  error_counter += benchmark_result_line.getProperty('error_counter')

context.edit(error_counter=error_counter,
             error_message_list=error_message_list,
             string_index='FAIL')

context.stop()
context.setProperty('string_index', result)
