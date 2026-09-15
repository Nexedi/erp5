"""Start the request that this Artificial Task Report Line holds.

The Document Component `ArtificialTaskReportLine` calls this script from the
method `send`. The workflow script `script_Event_send` calls `send` after the
transition `start`.

WARNING: this script must not call the Large Language Model. The transition
`start` runs in the transaction of the caller. This script only starts one
activity.

WARNING: this script must never run inside one web request. A web request
bypasses the workflow and the permission `AccessContentsInformation`. Two
guards stop a web request. The first guard reads the path of the request.
The second guard reads the simulation state of the line. The workflow sets
the state `started` before the workflow runs the script after the
transition. The guard is therefore true for every legitimate caller.
"""
from DateTime import DateTime

SCRIPT_ID = 'ArtificialTaskReportLine_sendRequest'
LINE_PORTAL_TYPE = 'Artificial Task Report Line'

line = context

# Refuse a call over HTTP. Compare every segment of the path. A trailing
# solidus defeats a test on the end.
request_path = ''
try:
  request_path = '%s' % (container.REQUEST.get('PATH_INFO', '') or '', )
except Exception:
  request_path = ''
if SCRIPT_ID in [x for x in request_path.split('/') if x]:
  return 'refused: this script is not a web page'

if line.getSimulationState() != 'started':
  return 'refused: the line is not started'

report = line.getParentValue()

text_content = line.getTextContent()
if not text_content:
  # A bare line is a test line.
  return 'no payload'

# Idempotence guard. Read the siblings from the container, not from the
# catalog. The catalog is not up to date inside the current transaction.
line_relative_url = line.getRelativeUrl()
for sibling in report.objectValues(portal_type=LINE_PORTAL_TYPE):
  if sibling.getCausality() == line_relative_url:
    return 'answer already exists'

line.edit(start_date=DateTime())

artificial_task = report.getFollowUpValue(portal_type='Artificial Task')
if artificial_task is not None:
  serialization_tag = artificial_task.getRelativeUrl()
else:
  serialization_tag = report.getRelativeUrl()

line.activate(
  activity='SQLQueue',
  max_retry=0,
  serialization_tag=serialization_tag,
  after_path_and_method_id=(line.getPath(), ('immediateReindexObject', )),
).ArtificialTaskReportLine_processRequest()

return 'activity started'
