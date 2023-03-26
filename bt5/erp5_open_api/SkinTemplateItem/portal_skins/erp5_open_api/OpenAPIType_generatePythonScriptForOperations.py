import six
from Products.ERP5Type.Message import translateString

portal = context.getPortalObject()
skin_folder = portal.portal_skins[skin_folder_id]

type_id = context.getId().replace(' ', '')

for path, path_item in six.iteritems(context.getSchema()['paths']):
  for http_method, operation in six.iteritems(path_item):
    operation_id = operation.get('operationId')
    if operation_id:
      script_id = '{type_id}_{operation_id}'.format(
        type_id=type_id,
        operation_id=operation_id
      )
      if six.PY2:
        script_id = script_id.encode()
      if script_id not in skin_folder.objectIds():
        skin_folder.manage_addProduct['ERP5'].addPythonScriptThroughZMI(script_id)
      python_script = skin_folder[script_id]
      params = ', '.join(
        [param['name'] for param in operation.get('parameters', [])]
        + (['body'] if operation.get('requestBody') else [])
      )
      python_script.setParameterSignature(params)

      python_script.setBody('''
"""{description}

{http_method} {path}
"""
'''.format(
  description=operation.get('description') or '',
  http_method=http_method.upper(),
  path=path
).encode())

return context.Base_redirect(
  form_id,
  keep_items={
    'portal_status_message': translateString('Python Scripts Generated'),
  }
)
