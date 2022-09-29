from Products.PythonScripts.standard import html_quote
import re

web_section = context
web_site = web_section.getWebSiteValue()

def _(string_to_escape):
  return html_quote("%s" % string_to_escape)


def generateSectionListHTML(result_list, section_list):
  if (section_list):
    result_list.append('<ul>')
    for section in section_list:
      # Add missing / suffix to get correct relative url generation
      # XXX Fix WebSection_getSiteMapTree instead, but no idea what would be the site effects
      result_list.append('<li><a href="%s">%s</a>' % (_(section['url'] + '/'), _(section['translated_title'])))
      generateSectionListHTML(result_list, section['subsection'])
      result_list.append('</li>')
    result_list.append('</ul>')


def generateDocumentListHTML(result_list, document_list):
  if (document_list):
    result_list.append('<aside id="document_list"><ul class="h-feed">')
    for section in document_list:
      publication_date = section['effective_date'] or section['modification_date']
      result_list.append("""
<li class="h-entry">
  <div class="e-content">
    <h2 class="p-name">%s</h2>
    %s
  </div>
  %s
  <p><a class="u-url" rel="permalink" href="%s"><time class="dt-published" datetime="%s">%s</time></a></p>
</li>""" % (
  _(section['translated_title']),
  ('<p class="p-summary">%s</p>' % _(section['description'])) if section.get('description') else '',
  ('<p class="p-author h-card">%s</p>' % _(section['document'].Document_getContributorTitleList()[0])),
  _(section['url']),
  _(publication_date.HTML4()),
  _(publication_date.rfc822())
))
    result_list.append('</ul></aside>')


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
  result_list += '<li><a href="%s" hreflang="%s"><abbr lang="%s">%s</abbr></a></li>' % (_(url), _(language), _(language), _(language))
result_list.append('</ul></nav>')

# Sitemap
result_list.append('<nav id="sitemap">')
result_list.append('<a href="%s">%s</a>' % (_(web_site.absolute_url()), _(web_site.getTranslatedTitle())))
generateSectionListHTML(result_list, web_site.WebSection_getSiteMapTree(include_document=False, depth=99))
result_list.append('</nav>')

# Documents
if include_document:
  generateDocumentListHTML(result_list, web_section.WebSection_getSiteMapTree(include_subsection=False, exclude_default_document=True, depth=1, property_mapping=('translated_title', 'description', 'effective_date', 'modification_date')))

return ''.join(result_list)
