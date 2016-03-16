from DateTime import DateTime

now = DateTime()
deadline = brain.getStopDate()
css_class = None

low_level_alert = \
brain.restrictedTraverse(brain.REQUEST.get('box_relative_url', '')).\
KnowledgeBox_getDefaultPreferencesDict().get('low_level_alert', None)

if now > deadline:
  css_class = "DataRed"
elif now - deadline > -(int(low_level_alert) or 3):
  css_class = "DataPink"

return css_class
