"""
  Return a merge list of all workflow history sorted by time.
  Result is returned as a sorted list of tempobject (returned by
  Base_getWorkflowHistoryItemList).
  This script can easily be used as list method by a listbox
"""

from Products.CMFCore.WorkflowCore import WorkflowException
history = {}
workflow_id_list = [workflow_id for workflow_id, _ in context.getWorkflowStateItemList()]
for wf_id in workflow_id_list:
  try:
    history[wf_id] = context.Base_getWorkflowHistoryItemList(workflow_id=wf_id)
  except WorkflowException:
    # some workflow don't have history
    pass

event_list = []
for workflow_id in history.keys():
  event_list += history[workflow_id]
if sort: event_list.sort(key=lambda x:x.time, reverse=True)
return event_list
