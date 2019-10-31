"""
Profile all threads from current process.

Spawns an extra thread (which is ignored in the profiling) to periodically take snapshots of all threads' call stacks.
The source code line of each innermost stack entry gets one hit, and all its callers are remembered as such.
Returns result and sets some response headers.

duration (number):
  How long to sample for.
  Larger values will produce more detailed results.
  Smaller values will produce more noisy results.
base_name (None, str):
  Value to include in the name of result file, to help categorise your own results.
  When None, produced file names are of the format: {cachegrind.out.|statistical_}YYYYmmddHHMMSS{|.zip}
  Otherwise, produced file names are of the format: {cachegrind.out.|statistical_}${base_name}_YYYYmmddHHMMSS{|.zip}
zipfile (bool)
  When true, the result is a zip file containing profiling result along with the python code (and, when not possible, the disassembled bytecode) of all files which appear in the profiling result.
  When false, the result is a bare profiling result (cachegrind file format).
"""
from time import sleep
from StringIO import StringIO
profiler, thread = context.ERP5Site_getStatisticalProfilerAndThread(single=False)
with thread:
  sleep(duration)
response = context.REQUEST.RESPONSE
filename = DateTime().strftime('%Y%m%d%H%M%S')
if base_name:
  filename = base_name + '_' + filename
if zipfile:
  data, content_type = profiler.asZip()
  filename = 'statistical_' + filename + '.zip'
else:
  out = StringIO()
  profiler.callgrind(out, relative_path=True)
  data = out.getvalue()
  content_type = 'application/x-kcachegrind'
  filename = 'cachegrind.out.' + filename
response.setHeader('content-type', content_type)
response.setHeader('content-disposition', 'attachment; filename="' + filename + '"')
return data
