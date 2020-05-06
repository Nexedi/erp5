from Products.ERP5Type.Message import translateString
from Products.ERP5Type.Document import newTempBase

# XXX: allow simulation_mode without detailed_report ?
detailed_report |= simulation_mode

portal = context.getPortalObject()
REQUEST = portal.REQUEST
base_category_property_id_set = portal.portal_types['Base Category'].getInstancePropertySet()
category_property_id_set = portal.portal_types.Category.getInstancePropertySet()
portal_categories = portal.portal_categories
resolveCategory = portal_categories.resolveCategory
getRelatedValueList = portal_categories.getRelatedValueList
isTransitionPossible = portal.portal_workflow.isTransitionPossible
detailed_report_result = []
detailed_report_append = detailed_report_result.append
def report(field_type, message, mapping=None, field_category='', level=None):
  if level and level not in displayed_report:
    return
  detailed_report_append(newTempBase(
    folder=context,
    id='item',
    field_type=field_type,
    field_category=field_category,
    field_message=translateString(
      message,
      mapping=mapping,
    ),
  ))
new_category_counter = 0
updated_category_counter = 0
total_category_counter = 0
invalid_category_id_counter = 0
deleted_category_counter = 0
kept_category_counter = 0
expired_category_counter = 0

def hasRelation(obj):
  # Tests if there is any sensible related objet.
  for o in obj.getIndexableChildValueList():
    for related in getRelatedValueList(o):
      related_url = related.getRelativeUrl()
      if not related_url.startswith(obj.getRelativeUrl()) and not related_url.startswith('portal_trash'):
        return True
  return False

def invalid_category_spreadsheet_handler(message):
  report(
    field_type='Error',
    message=str(message),
  )
  return True
category_list_spreadsheet_dict = context.Base_getCategoriesSpreadSheetMapping(
  import_file,
  invalid_spreadsheet_error_handler=invalid_category_spreadsheet_handler,
)
if detailed_report_result:
  REQUEST.other['portal_status_message'] = translateString('Spreasheet contains errors')
  REQUEST.other['category_import_report'] = detailed_report_result
  REQUEST.RESPONSE.write(portal_categories.CategoryTool_viewImportReport().encode('utf-8'))
  raise Exception('Spreadsheet contains errors')

for base_category, category_list in category_list_spreadsheet_dict.iteritems():
  total_category_counter += len(category_list)
  category_path_set = set()
  for category in category_list:
    is_new_category = False
    category_path = category.pop('path')
    category.pop('id', None)
    try:
      container_path, category_id = category_path.rsplit('/', 1)
    except ValueError:
      category_id = category_path
      container = portal_categories
      category_type = 'Base Category'
      category_type_property_id_set = base_category_property_id_set
    else:
      container = resolveCategory(container_path)
      category_type = 'Category'
      category_type_property_id_set = category_property_id_set
    try:
      category_value = container[category_id]
    except KeyError:
      if category_id in category_type_property_id_set:
        report(
          level='warning',
          field_type='WARNING',
          message="found invalid ID ${id} ",
          mapping={'id':category_id},
        )
        invalid_category_id_counter += 1
        continue
      new_category_counter += 1
      category_value = container.newContent(
        portal_type=category_type,
        id=category_id,
        effective_date=effective_date,
      )
      report(
        level='created',
        field_type='Creation',
        field_category=category_value.getRelativeUrl(),
        message="Created new ${type}",
        mapping={'type': category_type},
      )
      is_new_category = True
    category_path_set.add(category_value.getRelativeUrl())

    category_update_dict = {}
    for key, value in category.iteritems():
      if not create_local_property and key not in category_type_property_id_set:
        report(
          field_type='Update',
          field_category=category_value.getRelativeUrl(),
          message="Ignoring local property ${key} with value ${value}",
          mapping={'key': key, 'value': value},
        )
      elif is_new_category or (
            value not in ('', None) and
            not category_value.hasProperty(key)
          ) or (
            update_existing_property and
            str(category_value.getProperty(key)) != value
          ):
        category_update_dict[key] = value
        if not is_new_category:
          report(
            level='updated',
            field_type='Update',
            field_category=category_value.getRelativeUrl(),
            message="Updated ${key} with value ${value} ",
            mapping={'key': key, 'value': value},
          )
    if category_update_dict:
      if not is_new_category:
        updated_category_counter += 1
      # force_update=1 is required here because
      # edit(short_title='foo', title='foo') only stores short_title property.
      category_value.edit(force_update=1, **category_update_dict)

  to_do_list = [portal_categories[base_category]]
  while to_do_list:
    category = to_do_list.pop()
    recurse = True
    if category.getRelativeUrl() in category_path_set:
      pass
    elif existing_category_list == 'keep':
      report(
        level='kept',
        field_type='Keep',
        field_category=category.getRelativeUrl(),
        message="Kept category",
      )
      kept_category_counter += 1
    elif hasRelation(category):
      # TODO: add a dialog parameter allowing to delete this path
      report(
        level='warning',
        field_type='Warning',
        field_category=category.getRelativeUrl(),
        message="Category is used and can not be deleted or expired ",
      )
    elif existing_category_list == 'delete':
      recurse = False
      deleted_category_counter += 1
      report(
        level='deleted',
        field_type='Delete',
        field_category=category.getRelativeUrl(),
        message="Deleted category",
      )
      category.getParentValue().deleteContent(category.getId())
    elif existing_category_list == 'expire':
      report(
        level='expired',
        field_type='Expire',
        field_category=category.getRelativeUrl(),
        message="Expired category",
      )
      if expiration_date:
        expired_category_counter += 1
        category.edit(expiration_date=expiration_date)
      elif isTransitionPossible(category, 'expire'):
        expired_category_counter += 1
        category.expire()
      # Report failure otherwise ?
    # Report failure on unexpected value ?
    if recurse:
      to_do_list.extend(category.objectValues())

portal.portal_caches.clearAllCache()

# TODO: translate
portal_status_message = '%s categories found in %s: %s created, %s updated, %s untouched, %s invalid ID. %s existing categories: %s deleted, %s expired, %s kept.%s' % (
  total_category_counter,
  getattr(import_file, 'filename', '?'),
  new_category_counter,
  updated_category_counter,
  total_category_counter - new_category_counter - updated_category_counter,
  invalid_category_id_counter,
  deleted_category_counter + kept_category_counter + expired_category_counter,
  deleted_category_counter,
  expired_category_counter,
  kept_category_counter,
  ' (nothing done, simulation mode enabled)' if simulation_mode else '',
)
if detailed_report:
  REQUEST.other['portal_status_message'] = portal_status_message
  REQUEST.other['category_import_report'] = detailed_report_result
  result = portal_categories.CategoryTool_viewImportReport().encode('utf-8')
  if simulation_mode:
    REQUEST.RESPONSE.write(result)
    raise Exception('Dry run')  
  return result
portal_categories.Base_redirect(
  keep_items={
    'portal_status_message': portal_status_message,
  },
  abort_transaction=simulation_mode,
)
