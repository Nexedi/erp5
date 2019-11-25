"""
  Check that number of untranslated messages for a Localizer MessageCatalog instance
  doesn't exceed a fixed alarm_warn_ratio.
"""
alarm_warn_ratio = 0.25

localizer = context.Localizer
for message_catalog in localizer.objectValues('MessageCatalog'):
  all_messages = len(message_catalog.MessageCatalog_getMessageDict().keys())
  not_translated = len(message_catalog.MessageCatalog_getNotTranslatedMessageDict().keys())
  enable_warning = not_translated > all_messages * alarm_warn_ratio
  if enable_warning:
    # we have more than allowed number of untranslated messages,
    # fire alarm
    context.log("Too many untranslated Localizer messages for %s %s/%s" %(message_catalog, all_messages, not_translated))
    return True

return False
