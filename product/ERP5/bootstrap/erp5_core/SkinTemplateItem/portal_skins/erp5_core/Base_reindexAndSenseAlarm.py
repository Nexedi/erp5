from zExceptions import Unauthorized
if REQUEST is not None:
  raise Unauthorized

portal = context.getPortalObject()
alarm_tool = portal.portal_alarms

# Higher than simulable movement priority
# priority=3, to be executed after all reindex, but also execute simulation _expand
PRIORITY = 3

if alarm_tool.isSubscribed() and len(alarm_id_list):
  # No alarm tool is not subscribed, respect this choice and do not activate any alarm

  tag = None
  if must_reindex_context:
    tag = "%s-%s" % (script.id, context.getRelativeUrl())
    context.reindexObject(activate_kw={'tag': tag})

  for alarm_id in alarm_id_list:
    alarm = alarm_tool.restrictedTraverse(alarm_id)
    deduplication_tag = 'Base_reindexAndSenseAlarm_%s' % alarm_id

    if alarm.isEnabled():
      # do nothing if the alarm is not enabled

      if tag is not None:
        activate_kw = {}
        activate_kw['activity'] = 'SQLQueue'
        activate_kw['after_tag'] = tag
        activate_kw['tag'] = deduplication_tag
        activate_kw['priority'] = max(1, PRIORITY-1)
        # Wait for the context indexation to be finished
        alarm_tool.activate(**activate_kw).Base_reindexAndSenseAlarm([alarm_id],
                                                                     must_reindex_context=False)

      elif portal.portal_activities.countMessageWithTag(deduplication_tag) <= 1:
        if alarm.isActive():
          # If the alarm is active, wait for it
          # and try to reduce the number of activities
          # to reduce the number of alarm execution
          activate_kw = {}
          activate_kw['activity'] = 'SQLQueue'
          activate_kw['priority'] = PRIORITY
          activate_kw['tag'] = deduplication_tag
          activate_kw['after_path'] = alarm.getPath()
          # Wait for the previous alarm run to be finished
          # call on alarm tool to gather and drop with sqldict
          alarm_tool.activate(**activate_kw).Base_reindexAndSenseAlarm([alarm_id],
                                                                       must_reindex_context=False)
        else:
          # activeSense create an activity in SQLDict
          alarm.activeSense()
          # Prevent 2 nodes to call activateSense concurrently
          alarm.serialize()
