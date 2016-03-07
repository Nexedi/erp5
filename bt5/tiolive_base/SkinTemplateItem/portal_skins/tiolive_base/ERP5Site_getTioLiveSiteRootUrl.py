"""
  Get TioLive Site root URL.
"""
root_url = context.REQUEST.get('BASE0', 'https://www.tiolive.com')
language = context.Localizer.get_selected_language()

# This is far from perfect, to add language all the time
# in the url, because default languages of
# websites are usually not included in the url. But this
# script is also used in tiolive instances, and from them
# it is impossible to have the configuration of the web site
if language is not None and include_language:
  root_url = "%s/%s" % (root_url, language)
  
return root_url
