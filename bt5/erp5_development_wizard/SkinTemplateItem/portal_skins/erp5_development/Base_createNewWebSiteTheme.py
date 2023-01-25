"""
  Create new report theme web.
"""
portal_skins = context.getPortalObject().portal_skins
erp5_development = portal_skins.erp5_development

MARKER = ['', None]
page_template_header = """<tal:block define="dummy python: request.RESPONSE.setHeader('Content-Type', 'text/__REPLACE__;; charset=utf-8')"/>
"""
theme_id = web_site_theme_id.lower().replace(" ", "_")
main_template_id = "template_%s" % theme_id
default_form_group = "feature box (News)"

# XXX Should support Web Section too?
web_site = context.getWebSiteValue()

skin_folder = context.Base_createSkinFolder("%s_theme" % theme_id)

# Create Default Folder structure
skin_folder.manage_addProduct['OFSP'].manage_addFolder('%s_css' % (theme_id))
css_folder = getattr(skin_folder, '%s_css' % (theme_id))

skin_folder.manage_addProduct['OFSP'].manage_addFolder('%s_image' % (theme_id))
image_folder = getattr(skin_folder, '%s_image' % (theme_id))

skin_folder.manage_addProduct['OFSP'].manage_addFolder('%s_js' % (theme_id))
js_folder = getattr(skin_folder, '%s_js' % (theme_id))

css_id = "%s_web.css" % theme_id
css_folder.manage_addProduct['PageTemplates'].manage_addPageTemplate(css_id, "Default CSS" )
css_body = page_template_header.replace('__REPLACE__', 'css')
css_body += css_text
getattr(css_folder, css_id).write(css_body)

js_id = "%s_web.js" % theme_id
js_folder.manage_addProduct['PageTemplates'].manage_addPageTemplate(js_id, "Default js")
js_body = page_template_header.replace('__REPLACE__', 'javascript')
js_body += js_text
getattr(js_folder, js_id).write(js_body)

css_tales = "'%%s/%s_css/%s' %% portal_path," % (theme_id, css_id)
js_tales = "'%%s/%s_js/%s' %% portal_path," % (theme_id, js_id)

context.Base_createNewWebSiteMainTemplateTheme(html_text, main_template_id,
                                               skin_folder.getId(),
                                               css_tales, js_tales,
                                               main_div_class_name)

# Create Configuration Form
configuration_form_id = "WebSection_view%sThemeConfiguration" % web_site_theme_title.replace(" ", "")
skin_folder.manage_addProduct['ERP5Form'].addERP5Form(configuration_form_id)
configuration_form = getattr(skin_folder, configuration_form_id)
context.editForm(configuration_form, {'pt': 'form_view'})
context.editForm(configuration_form, {'action': 'Base_edit'})
context.editForm(configuration_form, {'title': "Web Site Configuration"})

# Add Default Field? This can be a form entry.
configuration_form.manage_addField('my_layout_background', 'Background', 'ProxyField')
field = getattr(configuration_form, 'my_layout_background')
field.manage_edit_xmlrpc(dict(form_id='Base_viewFieldLibrary', field_id='my_string_field'))

# Create content layout
content_layout_form_id = "%s_content_layout" % theme_id
skin_folder.manage_addProduct['ERP5Form'].addERP5Form(content_layout_form_id)
layout_form = getattr(skin_folder, content_layout_form_id)
for form_group in ["right", 'hidden', 'center', 'bottom']:
  layout_form.remove_group(form_group)
layout_form.rename_group('left', default_form_group)
context.editForm(layout_form, {'pt': main_template_id})

# Create default web layout
layout_form_id = "%s_layout" % theme_id
skin_folder.manage_addProduct['ERP5Form'].addERP5Form(layout_form_id)
layout_form = getattr(skin_folder,layout_form_id)
for form_group in ["right", 'hidden', 'center', 'bottom']:
  layout_form.remove_group(form_group)
layout_form.rename_group('left', default_form_group)
context.editForm(layout_form, {'pt': main_template_id})

if apply_web_site_theme:
  web_site.edit(content_layout=content_layout_form_id,
                container_layout=layout_form_id,
                layout_configuration_form_id=configuration_form_id)

portal_status_message = "New Theme successfuly created, See: %s/manage_main" % (skin_folder.absolute_url())
return web_site.Base_redirect("view",
                              keep_items=dict(portal_status_message=portal_status_message))
