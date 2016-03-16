"""
  We wait until all activities are finished

  RuntimeError is raised in case there is no way
  to finish activities.
"""
from Products.ERP5Type.Utils import sleep
count = int(count)
while len(context.portal_activities.getMessageList()) > 0:
  context.portal_activities.process_timer(0, 0)
  count -= 1
  sleep(t=1)
  if count < 0:
    raise RuntimeError, 'tic is endless'

return 'Done.'
