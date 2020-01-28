"""
  We need proy role as manager to create a new active process
  and post active result
"""
import string
import random

reference =  str(
  DateTime().millis()) + '-' + ''.join(
    random.sample(
      string.letters+string.digits, random.randint(
        6, 10)
    )
)

portal = context.getPortalObject()

if REQUEST:
  return RuntimeError("You cannot run this script in the url")

if active_process_url:
  active_process = portal.restrictedTraverse(active_process_url)
else:
  active_process = portal.portal_activities.newActiveProcess()

active_process.postActiveResult(detail=detail, reference=reference)
return active_process, reference
