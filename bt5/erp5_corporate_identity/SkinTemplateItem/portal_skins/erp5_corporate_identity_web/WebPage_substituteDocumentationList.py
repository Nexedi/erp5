from Products.PythonScripts.standard import html_quote

def escape(string_to_escape):
  return html_quote("%s" % string_to_escape)

web_site_value = context.getWebSiteValue()

result = {}

if (web_site_value is not None):
  category_relative_url_list = web_site_value.getLayoutProperty('layout_substitution_category_document_list', default="").split('\n')
  for category_relative_url in category_relative_url_list:
    base_category, _ = category_relative_url.split('/', 1)

    result[category_relative_url.replace('/', '__')] = '<ul>%s</ul>' % ''.join(['<li><a href="%s">%s</a></li>' % (escape(x.getReference()), escape(x.getTitle())) for x in web_site_value.getDocumentValueList(
      sort_on=[['title', 'ASC']],
      **{'%s__relative_url' % base_category: category_relative_url}
    )])
return result
