"""At first call, this script prefills values for all tasks that are
going to be created. If values are already there, this script check that
information is correct.
"""
portal = context.getPortalObject()
line_portal_type = "Sale Order Line"
request = context.REQUEST
from Products.PythonScripts.standard import Object
from Products.ERP5Type.Message import translateString

initial_value_dict = {}
for line in (listbox or []):
  initial_value_dict[line['listbox_key']] = line

listbox = []
validation_errors = {}
def getRecursiveLineList(current, line_list):
  # We parse recursively all delivery line and we keep only ones
  # without child
  sub_line_list = current.objectValues(portal_type=line_portal_type)
  if len(sub_line_list) == 0:
    if current.getPortalType() == line_portal_type:
      line_list.append(current)
  else:
    for sub_line in sub_line_list:
      getRecursiveLineList(sub_line, line_list)
line_list = []
getRecursiveLineList(context, line_list)
i = 1
project_search_dict = {}
for line in line_list:
  line_dict = {}
  key = str(i).zfill(3)
  for property_name in ('title', 'quantity_unit_title', 'quantity',
                        'resource_title', 'total_price', 'price',
                        'reference', 'relative_url'):
    property_value = line.getProperty(property_name)
    line_dict[property_name] = line.getProperty(property_name)
    request.form["field_listbox_%s_new_%s"% (property_name, key)] = \
      property_value
  line_dict.update(**initial_value_dict.get(key, {}))
  if line_dict.get('source_project_title', '') == '':
    line_dict['source_project_title'] = source_project_title
  line_source_project_title = line_dict.get('source_project_title', '')
  request.form["field_listbox_%s_new_%s"% ('source_project_title', key)] = \
      line_source_project_title
  if line_source_project_title != '':
    # Check if we have exactly one corresponding project
    result = project_search_dict.get(line_source_project_title, None)
    error_message = None
    if result is None:
      result = portal.portal_catalog(portal_type=('Project', 'Project Line'),
                                     title=line_source_project_title)
      project_search_dict[line_source_project_title] = result
    if len(result) == 0:
      error_message = "No such project"
    elif len(result) > 1:
      error_message = "Too many matching projects"
    else:
      line_dict['source_project_relative_url'] = result[0].getRelativeUrl()
    if error_message:
      validation_errors['listbox_source_project_title_new_%s' % key] = Object(
          field_id='listbox_source_project_title_new_%s' % key,
          getMessage=lambda translateString, message=error_message: translateString(message),
      )
  listbox.append(line_dict)
  i += 1

context.Base_updateDialogForm(listbox=listbox,update=1,kw=kw)

if len(validation_errors):
  request.set('field_errors',validation_errors)
  kw['REQUEST'] = request

# if called from the validate action we create tasks
if create and len(validation_errors) == 0:
  for line in listbox:
    delivery_line = portal.restrictedTraverse(line['relative_url'])
    portal.task_module.newContent(
              title=delivery_line.getTitle(),
              source_project=line['source_project_relative_url'],
              source=delivery_line.getSourceTrade(),
              reference=delivery_line.getReference(),
              task_line_quantity=delivery_line.getQuantity(),
              task_line_price=delivery_line.getPrice(),
              task_line_quantity_unit=delivery_line.getQuantityUnit(),
              task_line_resource=delivery_line.getResource(),
              start_date=delivery_line.getStartDate(),
              stop_date=delivery_line.getStopDate(),
              description=delivery_line.getDescription(),
              price_currency=context.getPriceCurrency(),
              source_section=delivery_line.getSourceSection(),
              destination=delivery_line.getDestination(),
              causality=delivery_line.getRelativeUrl(),
              destination_section=delivery_line.getDestinationSection(),
              destination_decision=delivery_line.getDestinationDecision())
  return context.Base_redirect(form_id, keep_items=dict(
        portal_status_message=translateString('${task_count} Tasks Created.', mapping={'task_count': len(listbox)})))
return context.Delivery_viewTaskFastInputDialog(listbox=listbox, **kw)
