web_page = context.getPortalObject().portal_types['Web Page']
web_page_workflow_list = web_page.getTypeWorkflowList()
if 'publication_workflow' in web_page_workflow_list:
  if fixit:
    web_page.setTypeWorkflowList([w for w in web_page_workflow_list if w != 'publication_workflow'])
  else:
    return ["Web Page portal type should not have publication_workflow bound,it's replaced with document_publication_workflow"]
return []
