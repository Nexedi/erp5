"""
   This script factorises code required to redirect to the appropriate
   page from a script. It should probably be extended, reviewed and documented
   so that less code is copied and pasted in dialog scripts.

   TODO: improve API and extensively document. ERP5Site_redirect may
   be redundant.
"""
from ZTUtils import make_query

request = context.getPortalObject().REQUEST
request_form = request.form
request_form.update(kw)
request_form = context.ERP5Site_filterParameterList(request_form)
request_form.update(keep_items)
parameter_dict = dict([(k, v) for k, v in request_form.items() if k and v is not None])

if not redirect_url or '/' not in redirect_url:
  # Used when redirect_url is not given explicitely and we redirect to an ERP5 document
  # BBB: originally, form_id was the first positional argument
  form_id = redirect_url or kw.pop('form_id', None)
  redirect_url = context.constructUrlFor(
    form_id=form_id,
    parameter_dict=parameter_dict,
  )
else:
  # Used if redirect_url is given explicitely (e.g. if we redirect to external web page)
  # so constructUrlFor is not usable,
  # since we have no document to redirect using is as context.
  parameters = make_query(parameter_dict)
  if len(parameters):
    if '?' in redirect_url:
      separator = '&'
    else:
      separator = '?'
    redirect_url = '%s%s%s' % (redirect_url, separator, parameters)

if abort_transaction:
  from zExceptions import Redirect
  raise Redirect(redirect_url)
return request.RESPONSE.redirect(redirect_url)
