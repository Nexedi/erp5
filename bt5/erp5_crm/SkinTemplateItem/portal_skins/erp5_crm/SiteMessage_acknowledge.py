# A Site Message is used in order to display messages to some users
# in the User Interface. A Site Message define
# which user will get the notification. When an user match the destination
# properties of the site message, a message is displayed in the
# browser, as part of the html page. The user must approve this message
# and then an acknowledge document will be created.

if user_name is None:
  raise ValueError("User name must be provided")

person_value = context.Base_getUserValueByUserId(user_name)

result = None
if not context.isAcknowledged(user_name=user_name):
  person_value.serialize()
  event = context
  tag="%s_%s" % (user_name, event.getRelativeUrl())
  acknowledgement = context.event_module.newContent(portal_type="Acknowledgement",
                                        destination=person_value.getRelativeUrl(),
                                        causality=event.getRelativeUrl(),
                                        document_proxy=event.getRelativeUrl(),
                                        resource=event.getResource(),
                                        title=event.getTitle(),
                                        start_date = DateTime(),
                                        activate_kw={'tag': tag})
  acknowledgement.deliver()
  result = acknowledgement

return result
