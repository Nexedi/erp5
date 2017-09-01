"""Return the notification messages that can be used as a template to create an event.
"""
reference_set = set() # If there are two messages with same reference, we only
                      # display one entry, because later code will use getDocumentValue
item_list = [('', '')]

portal = context.getPortalObject()

preferred_use_list = portal.portal_preferences.getPreferredEventResponseUseList()

for notification_message in portal.portal_catalog(
        validation_state='validated', portal_type='Notification Message'):
  notification_message = notification_message.getObject()
  reference = notification_message.getReference()
  if reference and reference not in reference_set:
    reference_set.add(reference)
    service = notification_message.getSpecialiseValue()
    if response_only and preferred_use_list:
      if service is not None:
        for preferred_use in preferred_use_list:
          if service.isMemberOf('use/%s' % preferred_use):
            item_list.append(
              ('%s - %s' % (reference, notification_message.getTranslatedTitle()), reference))
    else:
      item_list.append(
        ('%s - %s' % (reference, notification_message.getTranslatedTitle()), reference))

return sorted(item_list)
