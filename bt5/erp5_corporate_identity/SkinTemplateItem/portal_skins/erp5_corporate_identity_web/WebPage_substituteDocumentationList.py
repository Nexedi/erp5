import cgi

def escapeInnerHTML(string_to_escape):
  return cgi.escape("%s" % string_to_escape, quote=False)

def escapeAttributeProperty(string_to_escape):
  return cgi.escape("%s" % string_to_escape, quote=True)

# XXX HARDCODED
category_relative_url_list = [
  'group/template_test_group',
  'function/company/executive'
]

web_site_value = context.getWebSiteValue()

result = {}

if (web_site_value is not None):
  for category_relative_url in category_relative_url_list:
    base_category, _ = category_relative_url.split('/', 1)

    result[category_relative_url.replace('/', '__')] = '<ul>%s</ul>' % ''.join(['<li><a href="%s">%s</a></li>' % (escapeAttributeProperty(x.getReference()), escapeInnerHTML(x.getTitle())) for x in web_site_value.getDocumentValueList(
      sort_on=[['title', 'ASC']],
      **{'%s__relative_url' % base_category: category_relative_url}
    )])
return result
