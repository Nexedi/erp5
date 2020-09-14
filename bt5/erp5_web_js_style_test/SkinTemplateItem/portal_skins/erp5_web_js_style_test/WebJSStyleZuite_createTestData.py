from DateTime import DateTime

portal = context.getPortalObject()

web_page_portal_type = "Web Page"
web_site_portal_type = "Web Site"

web_site_id = "erp5_web_js_style_test_site"
web_page_frontend_en_id = "erp5_web_js_style_test_frontpage_en"
web_page_frontend_fr_id = "erp5_web_js_style_test_frontpage_fr"
web_page_frontend_zh_id = "erp5_web_js_style_test_frontpage_zh"

### English web page
module = portal.getDefaultModule(web_page_portal_type)
if getattr(module, web_page_frontend_en_id, None) is not None:
  module.manage_delObjects([web_page_frontend_en_id])
web_page = module.newContent(
  portal_type=web_page_portal_type,
  id=web_page_frontend_en_id,
  reference="erp5_web_js_style_test_frontpage",
  language="en",
  version="001",
  text_content="""
    <p>Frontpage content</p>

    <p><a href='TEST-Js.Style.Demo.Content'>TEST-Js.Style.Demo.Content</a></p>
  """
)
portal.portal_workflow.doActionFor(web_page, 'publish_action')

### French web page
if getattr(module, web_page_frontend_fr_id, None) is not None:
  module.manage_delObjects([web_page_frontend_fr_id])
web_page = module.newContent(
  portal_type=web_page_portal_type,
  id=web_page_frontend_fr_id,
  reference="erp5_web_js_style_test_frontpage",
  language="fr",
  version="001",
  text_content="""
<p>Contenu de la page d'accueil</p>

<p><a href='TEST-Js.Style.Demo.Content'>TEST-Js.Style.Demo.Content</a></p>
  """
)
portal.portal_workflow.doActionFor(web_page, 'publish_action')

### Chinese web page
if getattr(module, web_page_frontend_zh_id, None) is not None:
  module.manage_delObjects([web_page_frontend_zh_id])
web_page = module.newContent(
  portal_type=web_page_portal_type,
  id=web_page_frontend_zh_id,
  reference="erp5_web_js_style_test_frontpage",
  language="zh",
  version="001",
  text_content="""
<p>主页内容</p>

<p><a href='TEST-Js.Style.Demo.Content'>TEST-Js.Style.Demo.Content</a></p>
  """
)
portal.portal_workflow.doActionFor(web_page, 'publish_action')

configuration_dict = {
  'nostyle': {
    'title': 'No Style'
  },
  'section': {
    'configuration_style_gadget_url': "jsstyle_demo.html",
    'title': "Demo Style",
  },
  'language': {
    'configuration_style_gadget_url': "jsstyle_demo.html",
    'available_language_list': ['en', 'fr', 'zh'],
    'static_language_selection': True,
    'language': "en",
    'aggregate_value': web_page,
    'title': "Demo Style With Language",
  }
}

### Web site
module = portal.getDefaultModule(web_site_portal_type)
if getattr(module, web_site_id, None) is not None:
  module.manage_delObjects([web_site_id])
module.newContent(
  portal_type=web_site_portal_type,
  id=web_site_id,
  skin_selection_name="Jsstyle",
  layout_configuration_form_id="WebSection_viewJsstylePreference",
  **configuration_dict[configuration]
)

return "Web Site created."
