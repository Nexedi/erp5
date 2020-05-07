import cgi

def escapeInnerHTML(string_to_escape):
  return cgi.escape("%s" % string_to_escape, quote=False)

def escapeAttributeProperty(string_to_escape):
  return cgi.escape("%s" % string_to_escape, quote=True)

follow_up_relative_url = context.getFollowUp()
web_site_value = context.getWebSiteValue()

result = {
  'faq_list': '',
  'how_to_list': '',
}

if (web_site_value is not None) and (follow_up_relative_url is not None):
  for key, category in (('faq_list', 'publication_section/faq'),
                        ('how_to_list', 'publication_section/howto')):

    result[key] = '<ul>%s</ul>' % ''.join(['<li><a href="%s">%s</a></li>' % (escapeAttributeProperty(x.getReference()), escapeInnerHTML(x.getTitle())) for x in web_site_value.getDocumentValueList(
      follow_up__relative_url=follow_up_relative_url,
      publication_section__relative_url=category,
      sort_on=[['title', 'ASC']],
    )])
return result
