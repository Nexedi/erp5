"""
 This script is part of ERP5 Base

 The default implementation searches for
 documents which are in the user language if any
 with same reference.
"""
#XXX : Diff with standart version by using proxy role auditor to allow
#      anonymous to find email. May be change workflow instead of this
#      Remove as possible hardcoding on default_language


portal = context.getPortalObject()
portal_catalog = portal.portal_catalog
# The list of portal types here should be large enough to include
# all portal_types defined in the various sections so that
# href tags which point to a document by reference can still work.
valid_portal_type_list = ('Notification Message',)

# Find the applicable language
if language is None:
  language = portal.Localizer.get_selected_language()

# Find the default language
default_language = portal.Localizer.get_default_language() or 'en'

if validation_state is None:
  validation_state = ('validated',)

# Search the catalog for all documents matching the reference
# this will only return documents which are accessible by the user

notification_message_list = portal_catalog(reference=reference,
                                           portal_type=valid_portal_type_list,
                                           validation_state=validation_state,
                                           language=language,
                                           sort_on=[('version', 'descending')],
                                           group_by=('reference',),
                                           **kw)

if len(notification_message_list) == 0 and language != default_language:
  # Search again with English as a fallback.
  notification_message_list = portal_catalog(reference=reference,
                                             portal_type=valid_portal_type_list,
                                             validation_state=validation_state,
                                             language=default_language,
                                             sort_on=[('version', 'descending')],
                                             group_by=('reference',),
                                             **kw)

if len(notification_message_list) == 0:
  # Search again without the language
  notification_message_list = portal_catalog(reference=reference,
                                             portal_type=valid_portal_type_list,
                                             validation_state=validation_state,
                                             sort_on=[('version', 'descending')],
                                             group_by=('reference',),
                                             **kw)

if len(notification_message_list) == 0:
  # Default returns None
  notification_message = None
else:
  # Try to get the first page on the list
  notification_message = notification_message_list[0]
  notification_message = notification_message.getObject()

# return the Notification Message
return notification_message
