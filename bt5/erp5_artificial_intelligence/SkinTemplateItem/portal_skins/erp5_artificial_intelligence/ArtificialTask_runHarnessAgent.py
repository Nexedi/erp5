"""Refuse every call. This script is retired.

Declare this script with the parameter line:

  artificial_task_report_line_relative_url=None, pending_tool_call_list=None, loop_count=0, **kw

Reason for the retirement. The old body created one Artificial Task Report
Line and never started that line. That line stayed in the state `draft` for
the whole run. The old body also called the provider with no line at all, so
no line held the send parameters. The old body called `deliver()` on one
Artificial Task Line, and the workflow `event_simulation_workflow` holds no
transition `deliver` from the state `draft`.

The supported path is `ArtificialTask_startAgent`. That script creates one
request line, writes the send parameters on that line, and starts that line.
`ArtificialTaskReportLine_processRequest` then reads the line only.

This script creates no document and calls no provider. This script raises
one clear error text.

NOTE: One other option is possible. That option repairs the harness path
instead of the retirement.
"""
RETIRED_MESSAGE = (
  'ArtificialTask_runHarnessAgent is retired. '
  'Call ArtificialTask_startAgent instead. '
  'The old body never started the request line.'
)

raise ValueError(RETIRED_MESSAGE)
