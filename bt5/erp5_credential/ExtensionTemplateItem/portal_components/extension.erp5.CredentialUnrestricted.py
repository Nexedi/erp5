from zExceptions import Unauthorized

def unrestrictedSearchMessage(self, key, REQUEST=None):
  if REQUEST is not None:
    raise Unauthorized

  message =  self.getPortalObject().portal_catalog.unrestrictedSearchResults(
    portal_type="Mail Message", reference=key, limit=1)

  if len(message):
    return message[0].getObject()
  return

def unrestrictedGetCredential(self, mail_message, REQUEST=None):
  if REQUEST is not None:
    raise Unauthorized

  credential =  self.getPortalObject().portal_catalog.unrestrictedSearchResults(
    follow_up_related_uid=mail_message.getUid(),
    portal_type="Credential Request", limit=1)

  if len(credential):
    return credential[0].getObject()
  return

def unrestrictedDeliverMessage(self, mail_message, REQUEST=None):
  if REQUEST is not None:
    raise Unauthorized

  try:
    mail_message.deliver()
  except Exception:
    #invalid wf transition
    return