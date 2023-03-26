context.newContent(
  portal_type='Action Information',
  reference='view_open_api',
  title='Open API',
  action_type='object_view',
  action='string:${object_url}/OpenAPI_view',
)
context.setTextContent('{}')
context.setContentType('application/json')
context.setTypeClass('OpenAPIService')
