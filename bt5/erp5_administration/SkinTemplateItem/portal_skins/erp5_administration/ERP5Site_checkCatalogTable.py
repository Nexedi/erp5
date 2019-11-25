"""
  Check that catalog tables contain data which is coherent with actual objects.
  Due to the number of objects to check, this function creates activites working
  on, at maximum, bundle_object_count objects.

  bundle_object_count
    Maximum number of objects to deal with in one transaction. 
    An activity is started after each successfull execution which
    found bundle_object_count to work on.
  property_override_method_id
    Id of a method that generates a dictionary of reference values
    for a particular item in the catalog.
  catalog_kw
    Extra parameters passed to catalog
  retry
"""
from DateTime import DateTime
from Products.CMFActivity.ActiveResult import ActiveResult
active_result = ActiveResult()
portal = context.getPortalObject()
activate = portal.portal_activities.activate
result_list = []
if catalog_kw is None:
  catalog_kw = {}

catalog_kw.setdefault('sort_on', (('uid','ascending'),))

if catalog_uid_list is None:
  # No uid list was given: fetch work to do from catalog and spawn activities
  first_run = uid_min is None
  if uid_min is not None:
    # Check what is after last check
    catalog_kw['uid'] = {'query': uid_min, 'range': 'nlt'}
  catalog_uid_list = [x.uid for x in portal.portal_catalog(
          limit=bundle_object_count * activity_count,
          **catalog_kw)]
  # Remove the uid once the parameter was given to catalog
  catalog_kw.pop('uid', None)
  if len(catalog_uid_list):
    # Get the last uid this pass will check,
    # so that next pass will check a batch starting after this uid.
    uid_min = max(catalog_uid_list)
    # Spawn activities
    worker_tag = tag + '_worker'
    activity_kw = {
      'activity': 'SQLQueue',
      'priority': 4,
    }
    check_kw = {
      'property_override_method_id': property_override_method_id,
      'active_process': active_process,
      'activity_count': activity_count,
      'bundle_object_count' : bundle_object_count,
      'tag': tag,
      'fixit': fixit,
    }
    for _ in xrange(activity_count):
      if len(catalog_uid_list) == 0:
        result_list.append('No more uids to check, stop spawning activities.')
        break
      activity_catalog_uid_list = catalog_uid_list[:bundle_object_count]
      catalog_uid_list = catalog_uid_list[bundle_object_count:]
      result_list.append('Spawning activity for range %i..%i (len=%i)'
                         % (activity_catalog_uid_list[0],
                            activity_catalog_uid_list[-1],
                            len(activity_catalog_uid_list)))
      activate(tag=worker_tag, **activity_kw) \
      .ERP5Site_checkCatalogTable(catalog_uid_list=activity_catalog_uid_list,
                                  catalog_kw=catalog_kw, **check_kw)
    else:
      result_list.append('Spawning an activity to fetch a new batch starting'
                         ' above uid %i' % uid_min)
      # For loop was not interrupted by a break, which means that all
      # activities got uids to process. Maybe there is another batch of uids
      # to check besides current one. Spawn an activity to process such batch.
      activate(after_tag=worker_tag, tag=tag, **activity_kw) \
      .ERP5Site_checkCatalogTable(uid_min=uid_min,
                                  catalog_kw=catalog_kw, **check_kw)
  else:
    result_list.append('Base_zGetAllFromcatalog found no more line to check.')
  active_result.edit(summary='Spawning activities', severity=0, detail='\n'.join(result_list))
  # Spawn an activity to save generated active result only if it's not the initial run
  if not first_run:
    activate(active_process=active_process, activity='SQLQueue', priority=2, tag=tag) \
    .ERP5Site_saveCheckCatalogTableResult(active_result)
else:
  # Process given uid list
  retry_uid_list = []
  restrictedTraverse = portal.restrictedTraverse
  catalog_line_list = portal.portal_catalog(uid=catalog_uid_list, **catalog_kw)
  attribute_id_list = catalog_line_list.names()
  attribute_id_list.remove('path')

  def error(message):
    if retry:
      retry_uid_list.append(catalog_line['uid'])
    else:
      result_list.append(message)
      return fixit

  def normalize(value):
    if value not in ('', None, 0.0, 0): # values which are all considered equal
      if isinstance(value, float):
        return float(str(value))
      if isinstance(value, DateTime):
        return DateTime("%s Universal" % value.toZone("Universal").ISO())
      return value

  for catalog_line in catalog_line_list:
    object_path = catalog_line['path']
    if object_path is None:
      error('Object with uid %r has no path in catalog.' % catalog_line['uid'])
      continue
    elif object_path == "deleted":
      continue
    try:
      actual_object = restrictedTraverse(object_path)
    except KeyError:
      actual_object = None
    if actual_object is None or actual_object.getPath() != object_path:
      if error('Object with path %r cannot be found in the ZODB.'
               % object_path):
        result_list.append('Catalog line will be deleted.')
        portal.portal_catalog.activate(activity='SQLQueue') \
        .unindexObject(uid=catalog_line['uid'])
      continue
    if exception_portal_type_list is not None and \
        actual_object.getPortalType() in exception_portal_type_list:
      continue
    try:
      explanation_value = actual_object.getExplanationValue()
    except AttributeError:
      explanation_value = None
    # There is already activity changing the state
    if actual_object.hasActivity() \
          or (explanation_value is not None \
          and explanation_value.hasActivity()):
      continue
    if property_override_method_id is None:
      reference_dict = {'uid': actual_object.getUid()}
    else:
      reference_dict = getattr(context, property_override_method_id)(instance=actual_object)
    do_reindex = False
    for attribute_id in attribute_id_list:
      if not reference_dict.has_key(attribute_id):
        reference_value = actual_object.getProperty(attribute_id)
      else:
        reference_value = reference_dict[attribute_id]
      catalog_value = normalize(catalog_line[attribute_id])
      # reference_value may be a list (or tuple) when we don't know exactly
      # what should be the value in the catalog, for example when checking
      # stocks (1 line with a positive value and another with a negative one).
      is_reference_value_list = same_type(reference_value, ()) \
                             or same_type(reference_value, [])
      if (catalog_value not in map(normalize, not is_reference_value_list
          and (reference_value,) or reference_value)):
        if error('%s.%s %s %r, but catalog contains %r'
                 % (actual_object.getRelativeUrl(), attribute_id,
                    is_reference_value_list and 'has candidate list' or '=',
                    reference_value, catalog_line[attribute_id])):
          do_reindex = True
    if do_reindex:
      result_list.append('Object %r will be reindexed.' % object_path)
      actual_object.reindexObject()

  summary_list = []
  begin = catalog_uid_list[0]
  end = catalog_uid_list[-1]
  entry_summary = '%s Entries (%s..%s)' % (len(catalog_uid_list), begin, end)
  summary_list.append(entry_summary)
  severity = len(result_list)
  if severity == 0:
    summary_list.append('Success')
  else:
    summary_list.append('Failed')
  active_result.edit(summary=', '.join(summary_list),
                     severity=severity,
                     detail='\n'.join(result_list))
  activate(active_process=active_process,
            activity='SQLQueue', 
            priority=2,
            tag=tag).ERP5Site_saveCheckCatalogTableResult(active_result)


  if len(retry_uid_list):
    # Check again document in case of another sql connection commit changes related to it
    worker_tag = tag + '_worker'
    activity_kw = {
      'activity': 'SQLQueue',
      'priority': 4,
    }
    check_kw = {
      'property_override_method_id': property_override_method_id,
      'active_process': active_process,
      'activity_count': activity_count,
      'bundle_object_count' : bundle_object_count,
      'tag': tag,
      'fixit': fixit,
    }
    activate(tag=worker_tag, **activity_kw) \
    .ERP5Site_checkCatalogTable(catalog_uid_list=retry_uid_list, retry=False,
                                catalog_kw=catalog_kw, **check_kw)

return active_result
