context.newContent(
  portal_type='Action Information',
  reference='view',
  title='Open API',
  action_type='object_view',
  action='string:${object_url}/OpenAPIService_view',
)
context.setTextContent('{}')
context.setContentType('application/json')
context.setTypeClass('OpenAPIService')
context.setTypeWorkflowList(['edit_workflow', 'validation_workflow'])
