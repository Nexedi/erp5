"""
   This script factorises code required to redirect to the appropriate
   page from a script. It should probably be extended, reviewed and documented
   so that less code is copied and pasted in dialog scripts.

   TODO: improve API and extensively document. ERP5Site_redirect may 
   be redundant.
"""
# BBB: originally, form_id was the first positional argument
if not redirect_url or '/' not in redirect_url:
  form_id = redirect_url or kw.pop('form_id', None)
  redirect_url = context.absolute_url()
  if form_id:
    redirect_url += '/' + form_id

from ZTUtils import make_query
request = context.getPortalObject().REQUEST
request_form = request.form
request_form.update(kw)
request_form = context.ERP5Site_filterParameterList(request_form)
request_form.update(keep_items)

parameters = make_query(dict([(k, v) for k, v in list(request_form.items()) if k and v is not None]))
if len(parameters):
  if '?' in redirect_url:
    separator = '&'
  else:
    separator = '?'
  redirect_url = '%s%s%s' % (redirect_url, separator, parameters)

if abort_transaction:
  from zExceptions import Redirect
  raise Redirect(redirect_url)
return request.RESPONSE.redirect(redirect_url, status=status_code)
