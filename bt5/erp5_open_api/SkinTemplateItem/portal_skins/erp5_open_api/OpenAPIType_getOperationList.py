"""Returns operations in a format suitable for a listbox's list method

"""

from ZTUtils import make_query
from Products.PythonScripts.standard import Object
portal = context.getPortalObject()

service = portal.newContent(portal_type=context.getId(), temp_object=True)


def makeOperation(method, **kw):
  if method is not None:
    kw['method_id'] = method.getId()
    kw['absolute_url'] = method.absolute_url
    kw['getObject'] = method.getObject
  else:
    kw['absolute_url'] = context.absolute_url
    kw['getObject'] = context.getObject

  def getListItemUrl(cname_id, selection_index, selection_name):
    if method is None:
      return None
    return '{}/view?{}'.format(
      method.absolute_url(),
      make_query(
        selection_index=selection_index, selection_name=selection_name))

  kw['getListItemUrl'] = getListItemUrl

  return Object(**kw)


operation_list = []
for operation in context.getOpenAPIOperationIterator():
  operation_id = operation.get('operationId')
  method = None
  if operation_id:
    method = service.getTypeBasedMethod(operation_id)
  operation_list.append(
    makeOperation(
      method,
      uid='new_{}'.format(operation_id),
      operation_id=operation_id,
      path=operation.path,
      request_method=operation.request_method.upper(),
    ))
return operation_list
