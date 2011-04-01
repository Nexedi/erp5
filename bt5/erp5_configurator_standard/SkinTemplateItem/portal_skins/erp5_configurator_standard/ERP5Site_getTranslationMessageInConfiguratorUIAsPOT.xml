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
            <value> <string>message_dict = {}\n
FUNC_NAME_LIST = (\'N_\',\n
                  \'Base_translateString\',\n
                  \'translateString\',\n
                  )\n
\n
def safe_get_value(field, key):\n
  try:\n
    return field.get_orig_value(key)\n
  except KeyError:\n
    return field.get_value(key)\n
\n
def add_message(message, comment):\n
  if not message:\n
    return\n
  if message in message_dict:\n
    comment_list = message_dict[message]\n
  else:\n
    comment_list = message_dict[message] = []\n
  if comment not in comment_list:\n
    comment_list.append(comment)\n
\n
portal_url = context.portal_url\n
\n
# Collect skin objects\n
form_list = []\n
field_list = []\n
page_template_list = []\n
python_script_list = []\n
def iterate(obj, script=True, form=True, field=True, listbox=True, template=True):\n
  for i in obj.objectValues():\n
    if script and i.meta_type==\'Script (Python)\':\n
      python_script_list.append(i)\n
    if form and i.meta_type==\'ERP5 Form\':\n
      form_list.append(i)\n
    elif field and i.meta_type.endswith(\'Field\'):\n
      field_list.append(i)\n
    elif template and i.meta_type in (\'Page Template\',\n
                         \'ERP5 PDF Template\',\n
                         \'ERP5 OOo Template\'):\n
      page_template_list.append(i)\n
    if i.isPrincipiaFolderish:\n
      iterate(i, form=form, field=field, template=template)\n
\n
iterate(context.portal_skins.nexedi_express_configuration, form=False)\n
iterate(context.portal_skins.erp5_generator, template=True, form=False, field=False)\n
iterate(context.portal_skins.erp5_generator_widgets, template=True, form=False, field=False)\n
iterate(context.portal_skins.erp5_wizard, template=True, form=False, field=False)\n
\n
# Collect from ERP5Configurator and ERP5Wizard products.\n
for message, path in context.Base_findMessageListFromPythonInProduct(FUNC_NAME_LIST):\n
  if \'ERP5Wizard\' in path or \'ERP5Configurator\' in path:\n
    add_message(message, path)\n
\n
# Collect workflow transition documents from workflow module.\n
for document in context.workflow_module.express_setup_workflow.contentValues():\n
  if document.portal_type==\'Transition\' and document.getTransitionFormId() is not None:\n
    add_message(document.getTitle(), portal_url.getRelativeContentURL(document))\n
\n
\n
# Collect title and description of each wizard page.\n
ui_description = context.portal_skins.nexedi_express_configuration[\'nexedi_express_configuration_ui_description.sxc\']\n
for page_dict in context.ConfigurationTemplate_readOOCalcFile(\'nexedi_express_configuration_ui_description.sxc\'):\n
  add_message(page_dict[\'title\'], portal_url.getRelativeContentURL(ui_description))\n
  add_message(page_dict[\'description\'], portal_url.getRelativeContentURL(ui_description))\n
\n
\n
#\n
# ERP5 Form title\n
#\n
# Add exceptional form\n
form_list.append(context.erp5_wizard.WizardTool_view)\n
form_list.append(context.nexedi_express_configuration.ExpressConfiguration_setupEmployeeListForm)\n
for i in form_list:\n
  if (i.getId().endswith(\'_viewFieldLibrary\') or\n
      i.getId().endswith(\'_viewDialogFieldLibrary\') or\n
      i.getId().endswith(\'_viewReportFieldLibrary\') or\n
      i.getId().endswith(\'_FieldLibrary\')\n
      ):\n
    continue\n
  add_message(i.title, portal_url.getRelativeContentURL(i))\n
\n
# Add exceptional fields\n
field_list.append(context.erp5_wizard.WizardTool_view.my_ac_password)\n
field_list.append(context.erp5_wizard.WizardTool_view.my_user_preferred_language)\n
for i in field_list:\n
  add_message(safe_get_value(i, \'title\'), portal_url.getRelativeContentURL(i))\n
  if i.has_value(\'default\') and not i.get_tales(\'default\'):\n
    add_message(safe_get_value(i, \'default\'), portal_url.getRelativeContentURL(i))\n
\n
# Other Exceptions\n
accounting_period_description = context.portal_skins.nexedi_express_configuration.ExpressConfiguration_setupAccountingForm.your_period_description\n
add_message(accounting_period_description.get_orig_value(\'default\'), portal_url.getRelativeContentURL(accounting_period_description))\n
\n
\n
#\n
# Page Template\n
#\n
Base_findStaticTranslationText = context.Base_findStaticTranslationText\n
for i in page_template_list:\n
  for m in Base_findStaticTranslationText(i, FUNC_NAME_LIST):\n
    add_message(m, portal_url.getRelativeContentURL(i))\n
\n
\n
#\n
# Python script\n
#\n
Base_getFunctionFirstArgumentValue = context.Base_getFunctionFirstArgumentValue\n
for i in python_script_list:\n
  source = i.body()\n
  for func_name in FUNC_NAME_LIST:\n
    call_func_name = \'%s(\' % func_name\n
    if call_func_name in source:\n
      for m in Base_getFunctionFirstArgumentValue(func_name, source):\n
        add_message(m, portal_url.getRelativeContentURL(i))\n
\n
\n
#\n
# Currency List\n
#\n
for row in context.ConfigurationTemplate_readOOCalcFile(\'standard_currency_list.ods\'):\n
  add_message(row[\'currency\'], portal_url.getRelativeContentURL(context.portal_skins.erp5_generator[\'standard_currency_list.ods\']))\n
\n
\n
#\n
# Output\n
#\n
def format(string):\n
  line_list = string.split(\'\\n\')\n
  length = len(line_list)\n
  if length==1:\n
    return \'"%s"\' % string\n
  else:\n
    return \'\\n\'.join([\'""\']+[format(i) for i in line_list])\n
\n
\n
MESSAGE_TEMPLATE = \'\'\'\\\n
%s\n
msgid %s\n
msgstr ""\n
\'\'\'\n
message_list = message_dict.keys()\n
message_list.sort()\n
for message in message_list:\n
  comment_list = message_dict[message]\n
  comment_list.sort()\n
  comment = \'\\n\'.join([(\'#: %s\' % i) for i in comment_list])\n
  print MESSAGE_TEMPLATE % (comment, format(message))\n
\n
context.REQUEST.RESPONSE.setHeader(\'Content-Type\', \'text/plain\')\n
\n
return printed\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ERP5Site_getTranslationMessageInConfiguratorUIAsPOT</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
