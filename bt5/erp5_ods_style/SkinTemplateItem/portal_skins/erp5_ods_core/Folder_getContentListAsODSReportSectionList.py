from Products.ERP5Form.Report import ReportSection
from Products.ERP5Type.Message import translateString

form = context
request = context.REQUEST
report_section_list = []
portal = context.getPortalObject()
selection_name = request.get('selection_name', None)

def getReportSectionListForObject(doc):
  """ Get all possible report section for object. """
  report_section_list = []
  doc = doc.getObject()
  title = doc.getTitle()
  report_section_list.append(ReportSection(level = 1,
                                           title = title,
                                           form_id = None))
  for action in portal.portal_actions.listFilteredActionsFor(doc)['object_view']:
    form_id = action['url'].split('?')[0].split('/')[-1]
    action_title = action['title']
    if action_title != 'History' and action_title != 'Metadata':
      report_section_list.append(ReportSection(path = doc.getPath(),
                                               form_id = form_id,
                                               level = 2,
                                               title = '%s - %s' % (title, translateString(action_title))))
  return report_section_list

if selection_name is not None:
  checked_uid_list = portal.portal_selections.getSelectionCheckedUidsFor(selection_name)
  if checked_uid_list:
    getObject = portal.portal_catalog.getObject
    for uid in checked_uid_list:
      report_section_list.extend(getReportSectionListForObject(getObject(uid)))
  else:
    # get all documents in the selection
    for doc in portal.portal_selections.callSelectionFor(selection_name, context=form):
      report_section_list.extend(getReportSectionListForObject(doc))
else:
  # get only current (context) document
  report_section_list.extend(getReportSectionListForObject(context))

return report_section_list
