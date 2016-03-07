"""
  Call the scripts to decouple the TioLive Instance.
"""
from Products.ERP5Type.Log import log
log("Starting to decouple the TioLive Instance!")

# Update person module.
result = context.Alarm_updatePersonModulePasswordInformation()
if not result:
  log("TioLive Instance hasn't been decoupled with success! It could not update the objects from Person Module.")
  return False

# Disable the remove user creation.
if not context.Alarm_moveObsoleteSkinObjectList():
  log("TioLive Instance hasn't been decoupled with success! It could not move the obsolete objects.")
  return False

# Remove Authentication Plugin
context.Alarm_removeAuthenticationPlugin()
context.setEnabled(False)

# Hide change password action
context.Alarm_hideChangePasswordAction()

# Notify customer
context.Alarm_notifyDecoupleInstance(person_list=result)

log("Finished to decouple the TioLive Instance!")

return True
