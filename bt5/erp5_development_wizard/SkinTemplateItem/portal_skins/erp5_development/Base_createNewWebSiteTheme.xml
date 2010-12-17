<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="PythonScript" module="Products.PythonScripts.PythonScript"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>Script_magic</string> </key>
            <value> <int>3</int> </value>
        </item>
        <item>
            <key> <string>_bind_names</string> </key>
            <value>
              <object>
                <klass>
                  <global name="NameAssignments" module="Shared.DC.Scripts.Bindings"/>
                </klass>
                <tuple/>
                <state>
                  <dictionary>
                    <item>
                        <key> <string>_asgns</string> </key>
                        <value>
                          <dictionary>
                            <item>
                                <key> <string>name_container</string> </key>
                                <value> <string>container</string> </value>
                            </item>
                            <item>
                                <key> <string>name_context</string> </key>
                                <value> <string>context</string> </value>
                            </item>
                            <item>
                                <key> <string>name_m_self</string> </key>
                                <value> <string>script</string> </value>
                            </item>
                            <item>
                                <key> <string>name_subpath</string> </key>
                                <value> <string>traverse_subpath</string> </value>
                            </item>
                          </dictionary>
                        </value>
                    </item>
                  </dictionary>
                </state>
              </object>
            </value>
        </item>
        <item>
            <key> <string>_body</string> </key>
            <value> <string encoding="cdata"><![CDATA[

"""\n
  Create new report theme web.\n
"""\n
portal_skins = context.getPortalObject().portal_skins\n
erp5_development = portal_skins.erp5_development\n
\n
MARKER = [\'\', None]\n
page_template_header = """<tal:block define="dummy python: request.RESPONSE.setHeader(\'Content-Type\', \'text/__REPLACE__;; charset=utf-8\')"/>\n
"""\n
theme_id = web_site_theme_id.lower().replace(" ", "_")\n
main_template_id = "template_%s" % theme_id\n
default_form_group = "feature box (News)"\n
\n
# XXX Should support Web Section too?\n
web_site = context.getWebSiteValue()\n
\n
skin_folder = context.Base_createSkinFolder("%s_theme" % theme_id)\n
\n
# Create Default Folder structure\n
skin_folder.manage_addProduct[\'OFSP\'].manage_addFolder(\'%s_css\' % (theme_id))\n
css_folder = getattr(skin_folder, \'%s_css\' % (theme_id))\n
\n
skin_folder.manage_addProduct[\'OFSP\'].manage_addFolder(\'%s_image\' % (theme_id))\n
image_folder = getattr(skin_folder, \'%s_image\' % (theme_id))\n
\n
skin_folder.manage_addProduct[\'OFSP\'].manage_addFolder(\'%s_js\' % (theme_id))\n
js_folder = getattr(skin_folder, \'%s_js\' % (theme_id))\n
\n
css_id = "%s_web.css" % theme_id\n
css_folder.manage_addProduct[\'PageTemplates\'].manage_addPageTemplate(css_id, "Default CSS" )\n
css_body = page_template_header.replace(\'__REPLACE__\', \'css\')\n
css_body += css_text\n
getattr(css_folder, css_id).write(css_body)\n
\n
js_id = "%s_web.js" % theme_id\n
js_folder.manage_addProduct[\'PageTemplates\'].manage_addPageTemplate(js_id, "Default js")\n
js_body = page_template_header.replace(\'__REPLACE__\', \'javascript\')\n
js_body += js_text\n
getattr(js_folder, js_id).write(js_body)\n
\n
css_tales = "\'%%s/%s_css/%s\' %% portal_path," % (theme_id, css_id)\n
js_tales = "\'%%s/%s_js/%s\' %% portal_path," % (theme_id, js_id)\n
\n
context.Base_createNewWebSiteMainTemplateTheme(html_text, main_template_id, \n
                                               skin_folder.getId(), \n
                                               css_tales, js_tales,\n
                                               main_div_class_name)\n
\n
# Create Configuration Form\n
configuration_form_id = "WebSection_view%sThemeConfiguration" % web_site_theme_title.replace(" ", "")\n
skin_folder.manage_addProduct[\'ERP5Form\'].addERP5Form(configuration_form_id)\n
configuration_form = getattr(skin_folder, configuration_form_id)\n
context.editForm(configuration_form, {\'pt\': \'form_view\'})\n
context.editForm(configuration_form, {\'action\': \'Base_edit\'})\n
context.editForm(configuration_form, {\'title\': "Web Site Configuration"})\n
\n
# Add Default Field? This can be a form entry.\n
configuration_form.manage_addField(\'my_layout_background\', \'Background\', \'ProxyField\')\n
field = getattr(configuration_form, \'my_layout_background\')\n
field.manage_edit_xmlrpc(dict(form_id=\'Base_viewFieldLibrary\', field_id=\'my_string_field\'))\n
\n
# Create content layout\n
content_layout_form_id = "%s_content_layout" % theme_id\n
skin_folder.manage_addProduct[\'ERP5Form\'].addERP5Form(content_layout_form_id)\n
layout_form = getattr(skin_folder, content_layout_form_id)\n
for form_group in ["right", \'hidden\', \'center\', \'bottom\']:\n
  layout_form.remove_group(form_group)\n
layout_form.rename_group(\'left\', default_form_group)\n
context.editForm(layout_form, {\'pt\': main_template_id})\n
\n
# Create default web layout\n
layout_form_id = "%s_layout" % theme_id\n
skin_folder.manage_addProduct[\'ERP5Form\'].addERP5Form(layout_form_id)\n
layout_form = getattr(skin_folder,layout_form_id)\n
for form_group in ["right", \'hidden\', \'center\', \'bottom\']:\n
  layout_form.remove_group(form_group)\n
layout_form.rename_group(\'left\', default_form_group)\n
context.editForm(layout_form, {\'pt\': main_template_id})\n
\n
if apply_web_site_theme:\n
  web_site.edit(content_layout=content_layout_form_id, \n
                container_layout=layout_form_id,\n
                layout_configuration_form_id=configuration_form_id)\n
\n
portal_status_message = "New Theme successfuly created, See: %s/manage_main" % (skin_folder.absolute_url())\n
return web_site.Base_redirect("view", \n
                              keep_items=dict(portal_status_message=portal_status_message))\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>web_site_theme_id, web_site_theme_title, css_text, js_text, html_text, main_div_class_name, apply_web_site_theme=None, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_createNewWebSiteTheme</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
