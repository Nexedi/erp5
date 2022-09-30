# pylint: disable-all
from Products.CMFCore.utils import getToolByName
from Products.PythonScripts.standard import html_quote

request = context.REQUEST
response = request.RESPONSE

uuid = traverse_subpath.pop(0)
#reference_tool = getToolByName(context, 'reference_catalog')
#obj = reference_tool.lookupObject(uuid)
catalog_tool = getToolByName(context, 'portal_catalog')
obj = catalog_tool.getObject(uuid)
if not obj:
    return context.standard_error_message(error_type=404,
     error_message='''The link you followed appears to be broken''')

if traverse_subpath:
    traverse_subpath.insert(0, obj.absolute_url())
    target = '/'.join(traverse_subpath)
else:
    target = obj.absolute_url()

if request.QUERY_STRING:
    target += '?' + request.QUERY_STRING
return response.redirect(target, status=301)
