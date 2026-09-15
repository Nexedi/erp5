"""Refuse every call. This script is retired.

Declare this script with the parameter line:

  **kw

Reason for the retirement. The old body started the Artificial Task, then
put one activity on `ArtificialTask_runHarnessAgent`. That script is retired
too. One call of the old body left the Artificial Task in the state `started`
with one activity that fails for ever.

The supported path is `ArtificialTask_startAgent`.

This script changes no state and creates no activity. This script raises one
clear error text.

NOTE: One other option is possible. That option repairs the harness path
instead of the retirement.
"""
RETIRED_MESSAGE = (
  'ArtificialTask_startHarnessAgent is retired. '
  'Call ArtificialTask_startAgent instead. '
  'The old body left one activity that fails for ever.'
)

raise ValueError(RETIRED_MESSAGE)
