import json
import cgi
import re

portal = context.getPortalObject()
REQUEST = portal.REQUEST

def _(string_to_escape):
  return cgi.escape("%s" % string_to_escape, quote=False)


def __(string_to_escape):
  return cgi.escape("%s" % string_to_escape, quote=True)

# http://tools.ietf.org/html/draft-kelly-json-hal-03
forbidden_property_list = ('_links', '_embedded', '_forms')


def dumpshtml(web_section, hal_json):
  result = ""

  # Show title
  result += '<h1>%s</h1>' % _(hal_json['title'])

  # Render the embedded form
  if ('_embedded' in hal_json) and ('_view' in hal_json['_embedded']):
    # Display the form content
    form_hal_json = hal_json['_embedded']['_view']

    result += '<main>'

    for key, value in form_hal_json.items():
      if not key.startswith('_'):
        if value["type"] == "EditorField":
          result += value["default"]
        elif value["type"] == "ImageField":
          result += '<img src="%s">' % (_(value["default"]), )

    result += '</main>'

  # Render the web site tree
  web_site = web_section.getWebSiteValue()
  result += '<footer><ol>'
  result += '<li><a href="%s">%s</a></li>' % (_(web_site.absolute_url()), __(web_site.getTranslatedTitle()))

  for sub_section_dict in web_site.WebSection_getSiteMapTree(depth=1, include_subsection=1, include_document=1):
    result += '<li><a href="%s">%s</a></li>' % (__(sub_section_dict['url']), __(sub_section_dict['translated_title']))
  result += '</ol><ul>'

  # Language
  available_language_set = web_site.getLayoutProperty("available_language_set", default=['en'])
  portal = context.getPortalObject()
  default_language = web_site.getLayoutProperty("default_available_language", default='en')
  website_url_set = {}
  root_website_url = web_site.getOriginalDocument().absolute_url()
  website_url_pattern = r'^%s(?:%s)*(/|$)' % (
    re.escape(root_website_url),
    '|'.join('/' + re.escape(x) for x in available_language_set))
  for language in available_language_set:
    if language == default_language:
      website_url_set[language] = re.sub(website_url_pattern, r'%s/\1' % root_website_url, web_section.absolute_url())
    else:
      website_url_set[language] = re.sub(website_url_pattern, r'%s/%s/\1' % (root_website_url, language), web_section.absolute_url())

  for language, url in website_url_set.items():
    result += '<li><a href="%s">%s</a></li>' % (__(url), __(language))
  result += '</ul><footer>'



  result = '<html><head>' \
      '<meta name="viewport"\n' \
      'content="width=device-width,height=device-height,' \
      'initial-scale=1" />' \
      '<style>body {max-width: 40em;}\n' \
      'label {display: block;}\n' \
      'input:not([type=submit]):not([type=file]) {width: 100%%;}\n' \
      'textarea {height: 15em;width: 100%%;}</style>' \
      '</head><body>%(body)s</body></html>' % {'body': result}
  return result

previous_skin_selection = REQUEST.get('previous_skin_selection', None)

new_skin_name = "Hal"
context.getPortalObject().portal_skins.changeSkin(new_skin_name)
REQUEST.set('portal_skin', new_skin_name)

# REQUEST=None, response=None, view=None, mode='root', query=None, select_list=None, limit=10, local_roles=None, form=None, form_data=None, relative_url=None, list_method=None, default_param_json=None, form_relative_url=None, bulk_list="[]", group_by=None, sort_on=None, selection_domain=None, extra_param_json=None, portal_status_message='', portal_status_level=None, keep_items=None

hal_json = context.ERP5Document_getHateoas(
  REQUEST=REQUEST,
  view='web_view',
  mode='traverse',
  relative_url=context.getRelativeUrl()
)

portal.changeSkin(previous_skin_selection)

# XXX aq_parent is only an hack
web_section = REQUEST.get("current_web_section", context.aq_parent)

REQUEST.response.setHeader('Content-Type', 'text/html')
return dumpshtml(web_section, json.loads(hal_json))
