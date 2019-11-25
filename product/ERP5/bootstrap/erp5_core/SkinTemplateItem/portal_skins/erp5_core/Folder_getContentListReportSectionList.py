from Products.ERP5Form.Report import ReportSection

request = context.REQUEST
report_section_list = []
portal = context.getPortalObject()
selection_name = request.get('selection_name', None)
stool = portal.portal_selections

def getFormIdFromAction(action):
  return action['url'].split('/')[-1].split('?')[0]

def getReportSectionForObject(doc):
  """ Get all possible report section for object. """
  doc = doc.getObject()
  actions = portal.portal_actions.listFilteredActionsFor(doc)
  # use the default view
  action = actions['object_view'][0]
  # unless a print action exists
  if actions.get('object_print'):
    # we ignore the default print action.
    valid_print_dialog_list = [ai for ai in actions['object_print']
            if getFormIdFromAction(ai) != 'Base_viewPrintDialog']
    if valid_print_dialog_list:
      action = valid_print_dialog_list[0]
    
  form_id = getFormIdFromAction(action)
  return ReportSection(path=doc.getPath(), form_id=form_id, title=doc.getTitleOrId())

if selection_name is not None:
  # get all documents in the selection
  checked_uid_list = stool.getSelectionCheckedUidsFor(selection_name)
  if checked_uid_list:
    getObject = portal.portal_catalog.getObject
    for uid in checked_uid_list:
      report_section_list.append(getReportSectionForObject(getObject(uid)))
  else:
    for doc in stool.callSelectionFor(selection_name, context=context):
      report_section_list.append(getReportSectionForObject(doc))

return report_section_list
