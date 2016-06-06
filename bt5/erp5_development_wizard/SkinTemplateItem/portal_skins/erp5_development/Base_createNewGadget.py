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
            <value> <string>"""\n
  Create new report dialog\n
"""\n
\n
MARKER = [\'\', None]\n
portal_gadgets = context.getPortalObject().portal_gadgets\n
portal_skins = context.getPortalObject().portal_skins\n
\n
if create_skin_id not in MARKER:\n
  # create skin\n
  skin_folder = context.Base_createSkinFolder(create_skin_id)\n
else:\n
  skin_folder = getattr(portal_skins, selected_skin_id)\n
\n
# create\n
if view_form_id in MARKER:\n
  view_form_id = \'ERP5Site_view%sGadget\' % gadget_title.replace(\' \', \'\')\n
if edit_form_id in MARKER:\n
  edit_form_id = \'ERP5Site_view%sGadgetPreferences\' % gadget_title.replace(\' \', \'\')\n
\n
kw = {\'id\': gadget_id,\n
      \'title\': gadget_title,\n
      \'portal_type\': \'Gadget\',\n
      \'view_form_id\': view_form_id,\n
      \'edit_form_id\': edit_form_id,\n
      \'render_type\': render_type,\n
      \'gadget_type\': [\'erp5_front\',\'web_front\', \'web_section\']}\n
 \n
gadget = portal_gadgets.newContent(**kw)\n
gadget.visible()\n
\n
# XXX: set image (not appears?)\n
erp5_logo = context.logoERP5\n
image = gadget.newContent(portal_type=\'Image\', id=\'default_image\')\n
image.setData(str(erp5_logo))\n
\n
# create code\n
if gadget_code_type==\'erp5\':\n
  skin_folder.manage_addProduct[\'ERP5Form\'].addERP5Form(view_form_id)\n
  view_form = getattr(skin_folder, view_form_id)\n
  skin_folder.manage_addProduct[\'ERP5Form\'].addERP5Form(edit_form_id)\n
  edit_form = getattr(skin_folder, edit_form_id)\n
  context.editForm(view_form, {\'pt\': \'gadget_view\'})\n
  context.editForm(edit_form, {\'pt\': \'gadget_view\'})\n
elif gadget_code_type==\'zpt\':\n
  skin_folder.manage_addProduct[\'PageTemplates\'].manage_addPageTemplate(view_form_id, gadget_title)\n
  skin_folder.manage_addProduct[\'PageTemplates\'].manage_addPageTemplate(edit_form_id, gadget_title)\n
elif gadget_code_type==\'python\':\n
  skin_folder.manage_addProduct[\'PythonScripts\'].manage_addPythonScript(id=view_form_id)\n
  script = getattr(skin_folder, view_form_id)\n
  script.ZPythonScript_edit(\'**kw\', \'return "Replace this script (%s) with your code."\' % view_form_id)\n
  skin_folder.manage_addProduct[\'PythonScripts\'].manage_addPythonScript(id=edit_form_id)\n
  script = getattr(skin_folder, edit_form_id)\n
  script.ZPythonScript_edit(\'**kw\', \'return "Replace this script (%s) with your code."\' % edit_form_id)\n
\n
return gadget.Base_redirect(\'view\', \n
                              keep_items=dict(portal_status_message="Gadget successfuly created"))\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>create_skin_id=None, selected_skin_id=None, gadget_title=None, gadget_id=None, view_form_id=None, edit_form_id=None, gadget_code_type=None,render_type=None, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_createNewGadget</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
