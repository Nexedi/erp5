# coding=UTF-8
from DateTime import DateTime

portal = context.getPortalObject()

web_page_portal_type = "Web Page"
web_site_portal_type = "Web Site"
web_section_portal_type = "Web Section"

web_site_id = "erp5_web_js_style_test_site"
web_section_id_prefix = "erp5_web_js_style_test_section_"

web_page_frontend_reference = "erp5_web_js_style_test_frontpage"
web_page_frontend_en_id = "erp5_web_js_style_test_frontpage_en"
web_page_frontend_fr_id = "erp5_web_js_style_test_frontpage_fr"
web_page_frontend_zh_id = "erp5_web_js_style_test_frontpage_zh"

web_page_content_reference = "erp5_web_js_style_test_contentpage"
web_page_content_en_id = "erp5_web_js_style_test_contentpage_en"
web_page_content_fr_id = "erp5_web_js_style_test_contentpage_fr"
web_page_content_zh_id = "erp5_web_js_style_test_contentpage_zh"

### English web page
module = portal.getDefaultModule(web_page_portal_type)
if getattr(module, web_page_frontend_en_id, None) is not None:
  module.manage_delObjects([web_page_frontend_en_id])
web_page = module.newContent(
  portal_type=web_page_portal_type,
  id=web_page_frontend_en_id,
  reference=web_page_frontend_reference,
  language="en",
  version="001",
  text_content="""
<p>Frontpage content</p>

<p><a href='%s'>%s</a></p>
<p><a href='.'>base link</a></p>
""" % (web_page_content_reference, web_page_content_reference)
)
portal.portal_workflow.doActionFor(web_page, 'publish_action')

if getattr(module, web_page_content_en_id, None) is not None:
  module.manage_delObjects([web_page_content_en_id])
web_page = module.newContent(
  portal_type=web_page_portal_type,
  id=web_page_content_en_id,
  reference=web_page_content_reference,
  language="en",
  version="001",
  text_content="""
<p>Subpage content</p>
"""
)
portal.portal_workflow.doActionFor(web_page, 'publish_action')

### French web page
if getattr(module, web_page_frontend_fr_id, None) is not None:
  module.manage_delObjects([web_page_frontend_fr_id])
web_page = module.newContent(
  portal_type=web_page_portal_type,
  id=web_page_frontend_fr_id,
  reference=web_page_frontend_reference,
  language="fr",
  version="001",
  text_content="""
<p>Contenu de la page d'accueil</p>

<p><a href='%s'>%s</a></p>
<p><a href='.'>base link</a></p>
""" % (web_page_content_reference, web_page_content_reference)
)
portal.portal_workflow.doActionFor(web_page, 'publish_action')

if getattr(module, web_page_content_fr_id, None) is not None:
  module.manage_delObjects([web_page_content_fr_id])
web_page = module.newContent(
  portal_type=web_page_portal_type,
  id=web_page_content_fr_id,
  reference=web_page_content_reference,
  language="fr",
  version="001",
  text_content="""
<p>Contenu de la sous page</p>
"""
)
portal.portal_workflow.doActionFor(web_page, 'publish_action')

### Chinese web page
if getattr(module, web_page_frontend_zh_id, None) is not None:
  module.manage_delObjects([web_page_frontend_zh_id])
web_page = module.newContent(
  portal_type=web_page_portal_type,
  id=web_page_frontend_zh_id,
  reference=web_page_frontend_reference,
  language="zh",
  version="001",
  text_content="""
<p>主页内容</p>

<p><a href='%s'>%s</a></p>
<p><a href='.'>base link</a></p>
""" % (web_page_content_reference, web_page_content_reference)
)
portal.portal_workflow.doActionFor(web_page, 'publish_action')

if getattr(module, web_page_content_zh_id, None) is not None:
  module.manage_delObjects([web_page_content_zh_id])
web_page = module.newContent(
  portal_type=web_page_portal_type,
  id=web_page_content_zh_id,
  reference=web_page_content_reference,
  language="zh",
  version="001",
  text_content="""
<p>子页面内容</p>
"""
)
portal.portal_workflow.doActionFor(web_page, 'publish_action')

configuration_dict = {
  'nostyle': {
    'title': 'No Style',
    'site_map_section_parent': True
  },
  'nostyleform': {
    'title': "No Style Form",
    'custom_render_method_id': 'WebSite_viewJSStyleTestDialog',
    'site_map_section_parent': True
  },
  'section': {
    'configuration_style_gadget_url': "jsstyle_demo.html",
    'title': "Demo Style",
    'site_map_section_parent': True
  },
  'not_loading': {
    'configuration_style_gadget_url': "jsstyle_demo_not_loading.html",
    'title': "Not Loading Style",
    'site_map_section_parent': True
  },
  'favicon': {
    'title': 'Favicon',
    'configuration_favicon_url': "favicon.ico",
    'site_map_section_parent': True
  },
  'faviconform':{
    'title': 'Favicon Form',
    'configuration_favicon_url': "favicon.ico",
    'custom_render_method_id': 'WebSite_viewJSStyleTestDialog',
    'site_map_section_parent': True
  },
  'meta_tag': {
    'title': 'Meta Tag',
    'configuration_description_meta_tag': 'Description Meta Tag',
    'configuration_site_name_meta_tag': 'Site Name Meta Tag',
    'configuration_site_title_meta_tag': 'Site Title Meta Tag',
    'configuration_site_url_meta_tag': 'Site Url Meta Tag',
    'configuration_site_preview_image_url_meta_tag': 'https://example',
    'subject_list': ['keyword1', 'keyword2'],
    'configuration_type_meta_tag': 'website',
    'site_map_section_parent': True
  },
  'meta_tag_form':{
    'title': 'Meta Tag Form',
    'configuration_description_meta_tag': 'Description Meta Tag',
    'configuration_site_name_meta_tag': 'Site Name Meta Tag',
    'configuration_site_title_meta_tag': 'Site Title Meta Tag',
    'configuration_site_url_meta_tag': 'Site Url Meta Tag',
    'configuration_site_preview_image_url_meta_tag': 'https://example',
    'subject_list': ['keyword1', 'keyword2'],
    'configuration_type_meta_tag': 'website',
    'custom_render_method_id': 'WebSite_viewJSStyleTestDialog',
    'site_map_section_parent': True
  },
  'language': {
    'configuration_style_gadget_url': "jsstyle_demo.html",
    'available_language_list': ['en', 'fr', 'zh'],
    'static_language_selection': True,
    'language': "en",
    'aggregate_value': module.restrictedTraverse(web_page_frontend_en_id),
    'title': "Demo Style With Language",
    'site_map_section_parent': True
  },
  'language_with_web_site_language_base': {
    'configuration_relative_url_base': 'web_site_language',
    'configuration_style_gadget_url': "jsstyle_demo.html",
    'available_language_list': ['en', 'fr', 'zh'],
    'static_language_selection': True,
    'language': "en",
    'aggregate_value': module.restrictedTraverse(web_page_frontend_en_id),
    'title': "Demo Style With Language",
    'site_map_section_parent': True
  },
  'language_with_web_site_base': {
    'configuration_relative_url_base': 'web_site',
    'configuration_style_gadget_url': "jsstyle_demo.html",
    'available_language_list': ['en', 'fr', 'zh'],
    'static_language_selection': True,
    'language': "en",
    'aggregate_value': module.restrictedTraverse(web_page_frontend_en_id),
    'title': "Demo Style With Language",
    'site_map_section_parent': True
  },
  'form': {
    'configuration_style_gadget_url': "jsstyle_demo.html",
    'title': "Demo Form",
    'custom_render_method_id': 'WebSite_viewJSStyleTestDialog',
    'site_map_section_parent': True
  },
  'empty_sitemap': {
    'title': 'Empty Sitemap',
    'configuration_style_gadget_url': "jsstyle_demo.html"
  }
}

### Web site
module = portal.getDefaultModule(web_site_portal_type)
if getattr(module, web_site_id, None) is not None:
  module.manage_delObjects([web_site_id])
web_site = module.newContent(
  portal_type=web_site_portal_type,
  id=web_site_id,
  skin_selection_name="Jsstyle",
  layout_configuration_form_id="WebSection_viewJsstylePreference",
  site_map_document_parent=True,
  criterion_property_list=('title',),
  **configuration_dict[configuration]
)
web_site.setCriterion('title', identity='erp5_web_js_style_test_contentpage')

web_section = web_site.newContent(
  portal_type=web_section_portal_type,
  id='%s1' % web_section_id_prefix,
  aggregate_value=web_site.getAggregateValue(),
  title="Demo Section 1",
  visible=True,
  site_map_section_parent=True
)
web_section.newContent(
  portal_type=web_section_portal_type,
  id='%s11' % web_section_id_prefix,
  aggregate_value=web_site.getAggregateValue(),
  title="Demo Section 11",
  visible=True
)
web_site.newContent(
  portal_type=web_section_portal_type,
  id='%s2' % web_section_id_prefix,
  aggregate_value=web_site.getAggregateValue(),
  title="Demo Section 2",
  visible=True
)

if configuration == 'form':
  web_site.newContent(
    portal_type=web_section_portal_type,
    id='%sform' % web_section_id_prefix,
    title="Demo Section Form",
    custom_render_method_id='WebSite_viewJSStyleTestDialog'
  )

return "Web Site created."
