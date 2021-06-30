import cgi
import re

web_site = context

def _(string_to_escape):
  return cgi.escape("%s" % string_to_escape, quote=False)


def __(string_to_escape):
  return cgi.escape("%s" % string_to_escape, quote=True)


def generateSectionListHTML(result_list, section_list):
  if (section_list):
    result_list.append('<ul>')
    for section in section_list:
      # Add missing / suffix to get correct relative url generation
      # XXX Fix WebSection_getSiteMapTree instead, but no idea what would be the site effects
      result_list.append('<li><a href="%s">%s</a>' % (__(section['url'] + '/'), _(section['translated_title'])))
      generateSectionListHTML(result_list, section['subsection'])
      result_list.append('</li>')
    result_list.append('</ul>')


def generateDocumentListHTML(result_list, document_list):
  if (document_list):
    result_list.append('<ul>')
    for section in document_list:
      result_list.append('<li><a href="%s">%s</a></li>' % (__(section['url']), _(section['translated_title'])))
    result_list.append('</ul>')


# Language
result_list = ['<nav id="language"><ul>']

available_language_set = web_site.getLayoutProperty("available_language_set", default=['en'])
default_language = web_site.getLayoutProperty("default_available_language", default='en')
website_url_set = {}
root_website_url = web_site.getOriginalDocument().absolute_url()
website_url_pattern = r'^%s(?:%s)*(/|$)' % (
  re.escape(root_website_url),
  '|'.join('/' + re.escape(x) for x in available_language_set))
for language in available_language_set:
  if language == default_language:
    website_url_set[language] = re.sub(website_url_pattern, r'%s/\1' % root_website_url, web_site.absolute_url())
  else:
    website_url_set[language] = re.sub(website_url_pattern, r'%s/%s/\1' % (root_website_url, language), web_site.absolute_url())

for language, url in website_url_set.items():
  result_list += '<li><a href="%s" hreflang="%s"><abbr lang="%s">%s</abbr></a></li>' % (__(url), __(language), __(language), _(language))
result_list.append('</ul></nav>')

# Sitemap
result_list.append('<nav id="sitemap">')
result_list.append('<a href="%s">%s</a>' % (__(web_site.absolute_url()), _(web_site.getTranslatedTitle())))
generateSectionListHTML(result_list, web_site.WebSection_getSiteMapTree(include_document=False, depth=99))
result_list.append('</nav>')

# Documents
result_list.append('<aside id="document_list">')
generateDocumentListHTML(result_list, web_site.WebSection_getSiteMapTree(include_subsection=False, depth=1))
result_list.append('</aside>')

return ''.join(result_list)
