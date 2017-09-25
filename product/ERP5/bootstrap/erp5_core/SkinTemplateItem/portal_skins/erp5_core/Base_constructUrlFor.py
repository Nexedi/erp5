'''
  - context: should the document that we need as base for the url.
  In case it is not given, the context will be used
  - form_id: the form that is invoked
  - document_reference: the reference of a document that is rendered,
  - parameter_dict: dictionary containing all get parameters
'''
from ZTUtils import make_query

absolute_url = context.absolute_url()
if context.getPortalType() in ('Web Section', 'Web Site') and absolute_url.endswith('/'):
  # Web Section and Web Site absulute_url should be overriden to add trailing slash.
  # Yet we do chekck if it ends with slash, for backwards compatibility
  url = absolute_url[:-1]
else:
  url = absolute_url

# Note that form_id and document_reference are handled the same way,
# it is different variable for semantic reasons
assert not (form_id and document_reference), 'Not allowed to have both form and document in the same url'
if form_id:
  url = '%s/%s' % (url, form_id)
elif document_reference:
  url = '%s/%s' % (url, document_reference)
else:
  url = url + '/'

if parameter_dict:
  url = '%s?%s' % (url, make_query(parameter_dict))
return url
