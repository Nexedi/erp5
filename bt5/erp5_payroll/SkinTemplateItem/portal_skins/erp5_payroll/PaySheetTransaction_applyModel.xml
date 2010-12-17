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

Base_translateString = context.Base_translateString\n
paysheet = context\n
\n
# copy categories\n
category_list = [\n
  \'destination_section\', \'source_section\', \'source_payment\',\n
  \'destination_payment\', \'price_currency\',\n
]\n
new_category_dict = {}\n
\n
model = paysheet.getSpecialiseValue().getEffectiveModel(\\\n
    start_date=paysheet.getStartDate(),\n
    stop_date=paysheet.getStopDate())\n
\n
if model is None:\n
  return context.Base_redirect(form_id,\n
     keep_items=dict(portal_status_message=Base_translateString(\'No pay sheet model.\')))\n
\n
for category in category_list:\n
  if force or not paysheet.getPropertyList(category):\n
    v = model.getModelInheritanceEffectiveProperty(paysheet, category)\n
    if v:\n
      new_category_dict[category] = v\n
\n
# copy the price_currency into the ressource :\n
price_currency = model.getModelInheritanceEffectiveProperty(paysheet, \'price_currency\')\n
if price_currency:\n
  new_category_dict[\'resource\'] = price_currency\n
  new_category_dict[\'price_currency\'] = price_currency\n
\n
def copyPaymentCondition(paysheet, model):\n
  filter_dict = {\'portal_type\': \'Payment Condition\'}\n
  effective_model_list = model.findEffectiveSpecialiseValueList(paysheet)\n
  for effective_model in effective_model_list:\n
    to_copy = effective_model.contentIds(filter=filter_dict)\n
    if len(to_copy) > 0 :\n
      copy_data = effective_model.manage_copyObjects(ids=to_copy)\n
      paysheet.manage_pasteObjects(copy_data)\n
\n
filter_dict = {\'portal_type\': \'Payment Condition\'}\n
if force:\n
  paysheet.manage_delObjects(list(paysheet.contentIds(filter=filter_dict)))\n
if len(paysheet.contentIds(filter=filter_dict)) == 0:\n
  copyPaymentCondition(paysheet, model)\n
\n
# copy model sub objects into paysheet\n
paysheet.PaySheetTransaction_copySubObject(\n
                  portal_type_list=(\'Annotation Line\',),\n
                  property_list=(\'quantity\', \'source\', \'resource\'))\n
paysheet.PaySheetTransaction_copySubObject(\n
                  portal_type_list=(\'Pay Sheet Model Ratio Line\',),\n
                  property_list=(\'quantity\',))\n
paysheet.PaySheetTransaction_copySubObject(\n
                  portal_type_list=(\'Payment Condition\',))\n
\n
paysheet.edit(**new_category_dict)\n
\n
if not batch_mode:\n
  return context.Base_redirect(form_id,\n
                   keep_items=dict(portal_status_message=\\\n
                       Base_translateString(\'Pay sheet transaction updated.\')))\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>form_id=\'view\', batch_mode=0, force=0</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>PaySheetTransaction_applyModel</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
