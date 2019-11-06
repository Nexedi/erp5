"""
Profile the whole execution of a callable.
Always raises, in order to allow profiling repeatedly in the same initial conditions code which would otherwise modify databases.
Writes result to response directly.

args (tuple)
kw (dict)
  Positional and keyword arguments to pass to profiled callable.
func (None, callable)
  Profiled callable, or context if not provided.
statistic (bool)
  Whether to use deterministic or statistic profiling.
  Deterministic is more detailed and easier to read, but has a very large performance cost (10x slower). It is best suited for profiling code which normally runs in a few seconds.
  Statistic is less detailed and harder to read, but has an extremely small performance cost. It is best suited for profiling code which normally takes at least 10s to run.
base_name (None, str):
  Value to include in the name of result file, to help categorise your own results.
  When None, produced file names are of the format: {cachegrind.out.|statistical_}YYYYmmddHHMMSS{|.zip}
  Otherwise, produced file names are of the format: {cachegrind.out.|statistical_}${base_name}_YYYYmmddHHMMSS{|.zip}
zipfile (bool)
  When true, the result is a zip file containing profiling result along with the python code (and, when not possible, the disassembled bytecode) of all files which appear in the profiling result.
  When false, the result is a bare profiling result (cachegrind file format).
"""
from StringIO import StringIO
portal = context.getPortalObject()
if statistic:
  profiler, retriever = portal.ERP5Site_getStatisticalProfilerAndThread(single=True)
else:
  profiler = retriever = portal.ERP5Site_getProfiler()
kw = dict(kw)
if func is None:
  func = context
with retriever:
  func(*args, **kw)
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
response.write(data)
raise Exception('profiling')
