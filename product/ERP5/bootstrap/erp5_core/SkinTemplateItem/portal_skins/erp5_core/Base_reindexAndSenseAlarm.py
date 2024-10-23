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

      if (tag is not None) or (context.getRelativeUrl() == alarm.getRelativeUrl()):
        activate_kw = {}
        activate_kw['activity'] = 'SQLQueue'
        if tag is not None:
          # Wait for the context indexation to be finished
          activate_kw['after_tag'] = tag
        else:
          # Wait for alarm to be finished
          # Wait for deduplication to be finished too
          activate_kw['after_path'] = alarm.getPath()
        activate_kw['tag'] = deduplication_tag
        # Use lower priority to accumulate many activities in SQLDict
        # instead of executing them to quickly
        activate_kw['priority'] = max(1, PRIORITY-1)
        alarm_tool.activate(**activate_kw).Base_reindexAndSenseAlarm([alarm_id],
                                                                     must_reindex_context=False)

      elif alarm.isActive() or (1 < portal.portal_activities.countMessageWithTag(deduplication_tag)):
        # If the alarm is active, or if there are multiple planned called
        # try to reduce the number of activities to reduce the number of alarm execution
        activate_kw = {}
        activate_kw['activity'] = 'SQLDict'
        activate_kw['priority'] = PRIORITY
        # call on alarm to gather and drop with sqldict
        # do not wait for anything here to prevent locking
        alarm.activate(**activate_kw).Base_reindexAndSenseAlarm([alarm_id],
                                                                must_reindex_context=False)


      else:
        # activeSense create an activity in SQLDict
        alarm.activeSense()
        # Prevent 2 nodes to call activateSense concurrently
        alarm.serialize()
