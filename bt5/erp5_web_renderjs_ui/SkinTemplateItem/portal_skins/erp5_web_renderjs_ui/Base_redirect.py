# XXX: minimal copy of xhtml_style's implementation, used by OAuth2 authentication.
# This should be removed once erp5js implements outh2 protocol directly instead of going through login forms

from ZTUtils import make_query
# BBB: originally, form_id was the first positional argument
if not redirect_url or '/' not in redirect_url:
  form_id = redirect_url or form_id
  redirect_url = context.absolute_url()
  if form_id:
    if not redirect_url.endswith('/'):
      redirect_url += '/'
    redirect_url += form_id
if keep_items:
  redirect_url += '?' + make_query(keep_items)
context.getPortalObject().REQUEST.RESPONSE.redirect(
  redirect_url,
  status=status_code,
)
