web_section = context
relative_url_base = web_section.getLayoutProperty('configuration_relative_url_base', default='web_section')

if relative_url_base == 'web_section':
  return ''

web_site = web_section.getWebSiteValue()
root_web_site = web_site.getOriginalDocument()

# raise NotImplementedError('%s %s %s' % (web_section.getRelativeUrl(), web_site.getRelativeUrl(), root_web_site.getRelativeUrl()))
if relative_url_base == 'web_site_language':
  web_site_relative_url = web_site.getRelativeUrl()
elif relative_url_base == 'web_site':
  web_site_relative_url = root_web_site.getRelativeUrl()
else:
  raise ValueError('Not supported relative url base: %s' % relative_url_base)

count = len(web_section.getRelativeUrl()[len(web_site_relative_url):].split('/'))
return '../' * (count - 1)
