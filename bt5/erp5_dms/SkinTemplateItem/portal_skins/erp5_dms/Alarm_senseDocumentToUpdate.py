"""
This script selects documents to update.the selection process
is based on calculation of the frequency_index and creation_date_index.
Documents which their frequency_index and creation_date_index are the
same as those calculated, are updated.
"""
from erp5.component.module.DateUtils import convertDateToHour
date_dict = {}

# Shared function
def updateDocumentList(**sql_kw):
  for document in context.portal_catalog(**sql_kw):
    document.getObject().activate().updateContentFromURL()

#Step1: convert the alarm date into hours
alarm_date = convertDateToHour()

#Step2: initialize a dictionary with frequencies
for frequency in context.portal_categories.update_frequency.contentValues():
  frequency_reference = frequency.getIntIndex()
  date_dict[frequency_reference] = alarm_date % frequency_reference

#Step3: update documents
for frequency_reference, creation_date in date_dict.items():
  sql_kw = {'creation_date_index':creation_date, 'frequency_index':frequency_reference, 'limit':None}
  documents_to_update = len(context.portal_catalog(**sql_kw))
  max_in_activities = 1000
  offset = 0
  loop = documents_to_update / max_in_activities
  for _ in range(loop):
    limit = '%s,%s' % (offset, max_in_activities)
    sql_kw['limit'] = limit
    updateDocumentList(**sql_kw)
    offset += max_in_activities
  limit = '%s,%s' % (offset, max_in_activities)
  sql_kw['limit'] = limit
  updateDocumentList(**sql_kw)
