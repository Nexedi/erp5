## Script (Python) "transformation_identity_update"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=lang
##title=
##

from ZTUtils import make_query

request = context.REQUEST
query = make_query(request.form)

# Try to get the id of the DTML method / PT / etc.
method_id = request.URL0[len(request.URL1):]
my_id = context.id
if callable(my_id): my_id = my_id()
if '/' + my_id == method_id:
  method_id = ''
relative_url = context.portal_url.getRelativeUrl(context)

# Chop useless language information
for l in context.gettext.get_available_languages():
  if relative_url[0:len(l) + 1] == l + '/':
    relative_url = relative_url[len(l) + 1:]

# Chop useless /
if relative_url == '':
  if len(method_id) > 0:
    if method_id[0] == '/':
      method_id = method_id[1:]

# Build the new URL
if query == '':
  return '%s/%s/%s%s' % (context.portal_url.getPortalObject().absolute_url(), lang,
                     relative_url,
                     method_id)
else:
  return '%s/%s/%s%s?%s' % (context.portal_url.getPortalObject().absolute_url(), lang,
                     relative_url,
                     method_id, query)
