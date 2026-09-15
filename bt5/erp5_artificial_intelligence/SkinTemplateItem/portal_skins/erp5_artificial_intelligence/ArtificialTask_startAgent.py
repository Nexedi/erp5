"""Start the agent of this Artificial Task.

The script calls `ArtificialTask_buildRequestLine`. That script holds the
whole build of the run. That script answers the Artificial Task Report and the
first `llm_request` line. This script starts that line.

The script returns the relative url of the Artificial Task Report.

WARNING: one run must hold one open request only.
`ArtificialTask_buildRequestLine` refuses a second build while one request is
open. The script then answers no line, and this script starts no line.
"""
result = context.ArtificialTask_buildRequestLine()
report = result[0]
request_line = result[1]
if request_line is not None:
  request_line.start()

return report.getRelativeUrl()
