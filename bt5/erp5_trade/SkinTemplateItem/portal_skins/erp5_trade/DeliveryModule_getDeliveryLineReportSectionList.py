from Products.ERP5Form.Report import ReportSection
from six.moves import range
portal = context.getPortalObject()

request = container.REQUEST
module_selection_name = request['selection_name']

# so that ods style does not repeat header on each section
request.set('merge_report_section_list', 1)

# XXX use a larger limit
saved_selection_params = portal.portal_selections.getSelectionParamsFor(module_selection_name)
selection_params = saved_selection_params.copy()
selection_params['limit'] = 100000
context.getPortalObject().portal_selections.setSelectionParamsFor(module_selection_name, selection_params)

report_section_list = []
try:
  all_uid_list = portal.portal_selections.getSelectionCheckedUidsFor(module_selection_name)
  if not all_uid_list:
    all_uid_list = [ x.uid for x in
      portal.portal_selections.callSelectionFor(module_selection_name, context=context)]

  # split in chunks
  batch_size = 1000
  for uid_list in [all_uid_list[x:x+batch_size] for x in range(0, len(all_uid_list), batch_size)]:
    report_section_list.append(
      ReportSection(form_id='DeliveryModule_viewDeliveryLineList',
                     path=context.getPhysicalPath(),
                     selection_params=dict(portal_type=request['portal_type'],
                                           use_list=request['use'],
                                           uid_list=uid_list,
                                           module_selection_name=module_selection_name)))
  return report_section_list
finally:
  context.getPortalObject().portal_selections.setSelectionParamsFor(module_selection_name, saved_selection_params)
