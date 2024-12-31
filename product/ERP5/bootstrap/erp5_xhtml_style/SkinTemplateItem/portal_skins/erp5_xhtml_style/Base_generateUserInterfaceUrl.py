"""
   DO NOT USE
   Each time the script is executed, a kitten dies.
   As URL generation is supposed to be separated from data manipulation
   to keep UI related code independant, no script should use both.
"""
redirect_url = context.absolute_url()
if form_id:
  redirect_url += '/' + form_id

from ZTUtils import make_query

parameters = make_query(dict([(k, v) for k, v in keep_items.items() if k and v is not None]))
if len(parameters):
  if '?' in redirect_url:
    separator = '&'
  else:
    separator = '?'
  redirect_url = '%s%s%s' % (redirect_url, separator, parameters)

return redirect_url
