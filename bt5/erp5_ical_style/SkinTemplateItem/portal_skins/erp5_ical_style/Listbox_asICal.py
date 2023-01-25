"""
  An ICal data format implementation.
  USAGE
    Data are drawn from a listbox as they are;
    mandatory columns: ('summary', 'description', 'created', 'dtstamp', 'last-modified', 'uid', 'dtstart', 'dtend', 'component', 'url')
    optional columns: ('location', 'status', 'completed', 'percent-complete', 'categories')
    Title (summary) can be anything, same for description, location and categories (categories can be one word or a comma-separated list, although not all clients can use multiple categories).
    Component can be "journal", "event" or "todo".
    Dates should be returned by listbox with no extra processing - the script formats them appropriately.
    'completed' and 'percent-complete' is valid only for todo
    'status' is valid for todo and can be: needs-action|completed|in-process|cancelled (default is needs-action)
    'status' is valid for event and can be: tentative|confirmed|cancelled
  PREPROCESSING
    If no start date is given, we take created
    If no stop date is given, we take start date
    For "todo" if status is 'completed' and no percent-complete is given, we take 100%.
    For "todo" if status is 'completed' and no completed date is given, we take dtend.
  IMPLEMENTATION DETAILS:
    dtstamp = indicates the date/time that the instance of the iCalendar object was created.
    due (in VTODO) = dtend
    dates are formatted "YYYYMMDDTHHMMSSZ" (which is HTML4 without separators).
    all dates are converted to GMT, then the client will adjust them to its local timezone
"""
from DateTime import DateTime
now = DateTime()
allowed_field_list = ('summary', 'description', 'created',
                      'last-modified', 'uid', 'dtstamp',
                      'dtstart', 'dtend', 'component', 'url',
                      'location', 'categories', 'status',
                      'completed', 'percent-complete')
allowed_status_list_todo = ('COMPLETED', 'IN-PROCESS',
                            'CANCELLED', 'NEEDS-ACTION')

# mapping listbox column headers with iCalendar properties
# if listbox column headers are more than one the index of first occured in listbox columns is getting
related_column_map = {
  'summary' : ('title',),
  'created' : ('creation date',),
  'last-modified' : ('modification date',),
  'dtstart' : ('start date', 'begin date',),
  'dtend' : ('stop date', 'end date',)
}

def convertDate(value):
  """ Format dates. """
  if hasattr(value, 'toZone'):
    # we dont specify time zone in the file,
    # but recalculate everything into UTC
    value = value.toZone('UTC')
    value = value.HTML4()
    value = value.replace('-', '')
    value = value.replace(':', '')
  return value

# figure out which column is which, by using column titles
ical_column_mapping = {}
for index, column_item in enumerate(label_list):
  column_header = column_item[1].lower()
  if column_header in allowed_field_list:
    ical_column_mapping[column_header] = index
    continue
  for related_column in related_column_map:
    if column_header in related_column_map[related_column] and \
       related_column not in ical_column_mapping:
      ical_column_mapping[related_column] = index
      break

for index, column_item in enumerate(label_list):
  column_header = column_item[1].lower()
  if column_header == 'date':
    if column_item[0].find('start_date') or column_item[0].find('startdate'):
      if not ical_column_mapping.get('dtstart', None):
        ical_column_mapping['dtstart'] = index
    elif column_item[0].find('end_date') or column_item[0].find('enddate'):
      if not ical_column_mapping.get('dtstart', None):
        ical_column_mapping['dtend'] = index

items = []
for line in line_list:
  brainObject = line.getBrain()
  column_item_list = line.getValueList()
  ical_item_dict = {}
  # collect values
  for header, index in ical_column_mapping.items():
    value_tuple = column_item_list[index]
    # the [0] is a raw value, the [1] is rendered; we want strings rendered (as unicode),
    # but other stuff (like int or DateTime) we want as they are
    if hasattr(value_tuple[0], 'lower'):
      value = value_tuple[1]
    else:
      if isinstance(value_tuple[0], DateTime):
        value = convertDate(value_tuple[0])
      else:
        value = value_tuple[0]
    ical_item_dict[header.upper()] = value

  for field in allowed_field_list:
    field_upper = field.upper()
    if field_upper not in ical_item_dict:
      if field_upper == 'SUMMARY' and hasattr(brainObject, 'getTitle'):
        ical_item_dict['SUMMARY'] = brainObject.getTitle()
      elif field_upper == 'DESCRIPTION' and hasattr(brainObject, 'getDescription'):
        ical_item_dict['DESCRIPTION'] = brainObject.getDescription()
      elif field_upper == 'CREATED' and hasattr(brainObject, 'getCreationDate'):
        ical_item_dict['CREATED'] = convertDate(brainObject.getCreationDate())
      elif field_upper == 'LAST-MODIFIED' and hasattr(brainObject, 'getModificationDate'):
        ical_item_dict['LAST-MODIFIED'] = convertDate(brainObject.getModificationDate())
      elif field_upper == 'UID' and hasattr(brainObject, 'getUid'):
        ical_item_dict['UID'] = brainObject.getUid()
      elif field_upper == 'COMPONENT':
        if hasattr(brainObject, 'getPortalType'):
          ical_item_dict['COMPONENT'] = context.Base_getICalComponent(brainObject)
        else:
          ical_item_dict['COMPONENT'] = 'journal'
      elif field_upper == 'URL' and hasattr(brainObject, 'absolute_url'):
        ical_item_dict['URL'] = brainObject.absolute_url()
      elif field_upper == 'DTSTAMP':
        ical_item_dict['DTSTAMP'] = convertDate(now)
      elif field_upper == 'DTSTART':
        if hasattr(line.getBrain(), 'getCreationDate'):
          ical_item_dict['DTSTART'] = convertDate(brainObject.getCreationDate())
        else:
          ical_item_dict['DTSTART'] = convertDate(now)
      elif field_upper == 'DTEND':
        ical_item_dict['DTEND'] = ical_item_dict['DTSTART']
      elif field_upper == 'CATEGORIES' and ical_item_dict['COMPONENT'] != 'journal' and \
           hasattr(brainObject, 'getPortalType'):
        ical_item_dict['CATEGORIES'] = context.Base_getICalCategory(brainObject)
      elif field_upper == 'STATUS' and ical_item_dict['COMPONENT'] != 'journal'  and \
           hasattr(brainObject, 'getPortalType'):
        ical_item_dict['STATUS'] = context.Base_getICalStatus(brainObject)
      elif field_upper == 'PERCENT-COMPLETE' and ical_item_dict['COMPONENT'] == 'todo' and \
           hasattr(brainObject, 'getPortalType'):
        ical_item_dict['PERCENT-COMPLETE'] = context.Base_getICalPercentComplete(brainObject)

  # check and process
  if ical_item_dict['DTSTART'] is None:
    ical_item_dict['DTSTART'] = ical_item_dict['CREATED']
  if ical_item_dict['DTEND'] is None:
    ical_item_dict['DTEND'] = ical_item_dict['DTSTART']

  # check and fix for todo and event
  if ical_item_dict['COMPONENT'] == 'todo':
    status = ical_item_dict.get('STATUS', False)
    if status:
      status = status.upper()
      ical_item_dict['STATUS'] = status
      if status not in allowed_status_list_todo:
        raise ValueError('ICal status %s is not allowed' % status)
      if status == 'COMPLETED':
        if not ical_item_dict.get('PERCENT-COMPLETE', False):
          ical_item_dict['PERCENT-COMPLETE'] = 100
        if not ical_item_dict.get('COMPLETED', False):
          ical_item_dict['COMPLETED'] = ical_item_dict['DTEND']
    else:
      ical_item_dict['STATUS'] = 'NEEDS-ACTION'
      if not ical_item_dict.get('PERCENT-COMPLETE', False):
          ical_item_dict['PERCENT-COMPLETE'] = 0
  elif ical_item_dict['COMPONENT'] == 'event':
    status = ical_item_dict.get('STATUS', False)
    if not status:
      ical_item_dict['STATUS'] = 'TENTATIVE'
  items.append(ical_item_dict)

return context.Listbox_renderAsICal(items=items)
