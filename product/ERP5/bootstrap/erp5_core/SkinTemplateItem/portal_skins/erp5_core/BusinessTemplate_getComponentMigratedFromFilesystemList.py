template_document_id_list = context.getTemplateDocumentIdList()
template_extension_id_list = context.getTemplateExtensionIdList()
template_test_id_list = context.getTemplateTestIdList()
if not (template_document_id_list or template_extension_id_list or template_test_id_list):
  return []

component_tool = context.getPortalObject().portal_components

from Products.ERP5Type.Document import newTempBase
def addLineListByType(id_list, destination_portal_type, line_list):
  for component_id in id_list:
    if getattr(component_tool, component_id, None) is not None:
      continue

    line = newTempBase(context,
                       'tmp_migrate_%s_%s' % (destination_portal_type, component_id),
                       uid=component_id,
                       name=component_id,
                       destination_portal_type=destination_portal_type)

    line_list.append(line)

line_list = []
addLineListByType(template_document_id_list, 'Document Component', line_list)
addLineListByType(template_extension_id_list, 'Extension Component', line_list)
addLineListByType(template_test_id_list, 'Test Component', line_list)
return line_list
