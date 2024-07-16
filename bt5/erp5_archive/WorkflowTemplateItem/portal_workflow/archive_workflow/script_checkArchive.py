from Products.ERP5Type.Core.Workflow import ValidationFailed
from Products.ERP5Type.Message import Message
from six.moves import range

# Check new catalog or catalog is the same as previous archive
# Check date
# Check connection definition

archive = state_change['object']
min_stop_date = archive.getStopDateRangeMin().Date()
catalog_id = archive.getCatalogId()

if "deferred" not in archive.getDeferredConnectionId():
  msg = Message(domain='ui', message='Deferred connection ID choose is not a deferred connection.')
  raise ValidationFailed(msg)

def sort_max_date(a, b):
  return cmp(a.getStopDateRangeMax(), b.getStopDateRangeMax())


if archive.getStopDateRangeMax() is not None:

  previous_archive_list = [x.getObject() for x in archive.portal_catalog(portal_type="Archive",
                                                                         validation_state='validated')]
  previous_archive_list.sort(sort_max_date)

  if len(previous_archive_list) > 0:
    # Check the date
    for x in range(len(previous_archive_list)):
      previous_archive = previous_archive_list[x]
      # find a previous archive which was not for current catalog
      if previous_archive.getStopDateRangeMax() is not None:
        break
    if previous_archive.getStopDateRangeMax().Date() != min_stop_date:
      msg = Message(domain='ui', message='Archive are not contiguous.')
      raise ValidationFailed(msg)
else:
  previous_archive_list = [x.getObject() for x in archive.portal_catalog(portal_type="Archive",
                                                                         validation_state='ready')]
  previous_archive_list.sort(sort_max_date)

  if len(previous_archive_list) > 0:
    # Check the date
    for x in range(len(previous_archive_list)):
      previous_archive = previous_archive_list[x]
      # find a previous archive which was not for current catalog
      if previous_archive.getStopDateRangeMax() is not None:
        break
    if previous_archive.getStopDateRangeMax().Date() != min_stop_date:
      msg = Message(domain='ui', message='Archive are not contiguous.')
      raise ValidationFailed(msg)


# Check the catalog
previous_archive_list = [x.getObject() for x in archive.portal_catalog(portal_type="Archive",
                                                                       validation_state=['validated', 'ready'])]

for arch in previous_archive_list:
  if arch.getCatalogId() == catalog_id and arch is not previous_archive:
    msg = Message(domain='ui', message='Use of a former catalog is prohibited.')
    raise ValidationFailed(msg)
