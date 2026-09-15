"""Read the answer of every Artificial Task Report Line that waits.

Declare this script with:
  ##parameters=tag, fixit, params

The Alarm `check_artificial_task_report_line_response` calls this script. The
Alarm holds no rule. `ArtificialTaskReportLine_checkResponse` holds every
rule.

The simulation state is the filter of the query. One line leaves the state
`started` as soon as one answer exists, because the answer path writes the
answer line and stops the request line in the same transaction. One line in
the state `started` is therefore one line that waits. The query needs no date.

The loop then skips every line that holds no `destination_reference`. Such one
line holds no request at the provider. The filter is in the loop, not in the
query, because the catalog holds one empty text for one line that a test
closed, and the query of one empty text against NULL is not the same on every
instance.

NOTE: the queue is `SQLQueue`. `SQLQueue` does not merge two identical pending
activities of one line. Two Alarm periods before one check runs therefore give
two check activities. The `serialization_tag` runs the two activities one after
the other, and the second one answers `the line is not started`. This is safe.

NOTE: the loop replaces `searchAndActivate`. `searchAndActivate` applies one
`activate_kw` to every line, so `searchAndActivate` cannot give one
`serialization_tag` per line. The tag matters. Recording one answer can start
the next paid request, so two activities of one run must never run together.
`Alarm_checkMailevaDocumentStatus` uses the same loop.

NOTE: do not pass `max_retry=0` here. A read at the provider pays nothing, so
a retry is safe. Only the create step keeps `max_retry=0`.
"""
portal = context.getPortalObject()

for brain in portal.portal_catalog(
    portal_type='Artificial Task Report Line',
    simulation_state='started'):
  line = brain.getObject()
  if not line.getDestinationReference():
    # No identifier: the request is not at the provider.
    continue
  report = line.getParentValue()
  artificial_task = report.getFollowUpValue(portal_type='Artificial Task')
  if artificial_task is not None:
    serialization_tag = artificial_task.getRelativeUrl()
  else:
    serialization_tag = report.getRelativeUrl()
  # The queue of `ArtificialTaskReportLine_sendRequest`: an older CMFActivity
  # applies one `serialization_tag` inside one queue only.
  line.activate(
    activity='SQLQueue',
    tag=tag,
    serialization_tag=serialization_tag,
  ).ArtificialTaskReportLine_checkResponse()

context.activate(after_tag=tag).getId()
