# Guards: role: Manager, as it is meaningless (and potentially very expensive) to use this script when one cannot typically see all documents.
import csv
import six
from io import BytesIO, StringIO
from erp5.component.module.Log import log

if not isinstance(from_date, DateTime):
  from_date = DateTime(from_date)
assert from_date < DateTime(), from_date
def always(document_value):
  return True
def if_has_workflow(document_value):
  return hasattr(document_value, 'workflow_history')
def unity(value):
  return value
def strftime(value):
  if value is None:
    return None
  value = value.toZone('UTC')
  return DateTime(
    value.year(),
    value.month(),
    value.day(),
    value.hour(),
    value.minute(),
    int(value.second()),
    'UTC'
  )
select_dict = {
  # column               getter                only if getter present ?  convert zodb  test zodb
  'uid':               ('getUid',              False,                    unity,        always),
  'title':             ('getTitle',            False,                    unity,        always),
  'portal_type':       ('getPortalType',       False,                    unity,        always),
  'creation_date':     ('getCreationDate',     False,                    strftime,     always),
  'modification_date': ('getModificationDate', False,                    strftime,     if_has_workflow),
  'validation_state':  ('getValidationState',  True,                     unity,        always),
  'simulation_state':  ('getSimulationState',  True,                     unity,        always),
}
column_list = select_dict.keys()

portal = context.getPortalObject()
traverse = portal.restrictedTraverse
portal_catalog = portal.portal_catalog
# XXX: abusing CMFActivity's privilege elevation: restricted python is not allowed to call unindexObject
unindexObject = portal_catalog.activate(activity='SQLQueue',
  group_method_id='portal_catalog/uncatalogObjectList',
).unindexObject

if six.PY2:
  io_ = BytesIO()
else:
  io_ = StringIO()
csv_writer = csv.writer(io_)

row_list = portal_catalog(
  select_list=[e for e in column_list if e != 'uid'],
  indexation_timestamp={
    'query': from_date,
    'range': '>=',
  },
).dictionaries()
row_list.extend(
  portal.z_get_deleted_path_list(timestamp=from_date).dictionaries()
)
log('Processing %i rows...' % len(row_list))

column_title_list = ['status', 'has difference', 'path']
for column in column_list:
  column_title_list.append('catalog ' + column)
  column_title_list.append('zodb ' + column)
csv_writer.writerow(column_title_list)

row_count = len(row_list)
for i, row in enumerate(row_list):
  zodb_property_dict = {}
  has_difference = False
  try:
    document_value = traverse(row['path'])
    __traceback_info__ = (row['path'], document_value)
  except KeyError:
    status = 'missing'
    has_difference = True
    unindexObject(uid=row['uid'])
  else:
    status = 'present'
    if document_value.getUid() != row['uid']:
      unindexObject(uid=row['uid'])
    for column_name, (getter_name, may_be_missing, zodb_filter, document_filter) in select_dict.items():
      if (
        (not may_be_missing or hasattr(document_value, getter_name)) and
        document_filter(document_value)
      ):
        value_from_document = zodb_filter(getattr(document_value, getter_name)())
        zodb_property_dict[column_name] = value_from_document
        has_difference |= value_from_document != row.get(column_name)
    # Reindex even if no difference was found
    document_value.reindexObject()
  output_value_list = [
    status,
    int(has_difference), # integers are easier to manage than "True" or "False" in libreoffice
    row['path'],
  ]
  output_value_list_append = output_value_list.append
  for column in column_list:
    output_value_list_append(row.get(column))
    output_value_list_append(zodb_property_dict.get(column))
  csv_writer.writerow(output_value_list)
  if i % 1000 == 0:
    log('processed %i/%i lines' % (i, row_count))

io_.seek(0)
result = io_.getvalue()
if dry:
  result += 'dry run'
  if six.PY3:
    result = result.encode()
  RESPONSE.write(result)
  raise Exception('dry run')
log(result)
return result
