from builtins import zip
for result_line, stdout in zip(result_line_list, stdout_list):
  context.newContent(portal_type='Benchmark Result Line',
                     title='%s repeat with %s concurrent users' % (repeat, concurrent_user),
                     concurrent_user=concurrent_user,
                     username=username,
                     repeat=repeat,
                     benchmark_suite_list=benchmark_suite_list,
                     result_header_list=result_header_list,
                     result_list=result_line,
                     error_counter=len([result for result in result_line if result == 0]),
                     stdout=stdout)
