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
            <value> <string>request = context.REQUEST\n
return_value = None\n
if my_choice == \'emission_letter_item\':\n
   my_list = getattr(request,\'my_emission_letter_list\',None)   # Find Emission letter on the REQUEST\n
   if my_list is None:\n
      my_list = getattr(request,\'field_my_emission_letter_list\',None)   # Find Emission letter on the REQUEST\n
\n
   if my_list is not None:\n
      return_value =  [x for x in context.portal_categories.emission_letter.getCategoryChildTitleItemList()\n
                if x[1] in my_list ]\n
   else:\n
      return_value =  [x for x in context.portal_categories.emission_letter.getCategoryChildTitleItemList()]\n
elif my_choice == \'emission_letter_default_value\':\n
   return_value = getattr(request,\'my_emission_letter_list\',None)   # Find Emission letter on the REQUEST\n
   return_value = return_value[1]\n
elif my_choice == \'cash_status_item\':\n
   my_list = getattr(request,\'my_cash_status_list\',None)   # Find cash Status on the REQUEST\n
   if my_list is None:\n
      my_list = getattr(request,\'field_my_cash_status_list\',None)   # Find Emission letter on the REQUEST\n
   if my_list is not None:\n
      return_value =  [x for x in context.portal_categories.cash_status.getCategoryChildTranslatedTitleItemList()\n
                  if x[1] in my_list]\n
   else:\n
      return_value =  [x for x in context.portal_categories.cash_status.getCategoryChildTranslatedTitleItemList()]\n
elif my_choice == \'cash_status_default_value\':\n
   return_value = getattr(request,\'my_cash_status_list\',None)   # Find cash Status on the REQUEST\n
   return_value = return_value[1]\n
\n
elif my_choice == \'variation_item\':\n
   my_list = getattr(request,\'my_variation_list\',None)   # Find variation on the REQUEST\n
   if my_list is None:\n
      my_list = getattr(request,\'field_my_variation_list\',None)   # Find variation on the REQUEST\n
   if my_list is not None:\n
      return_value =  [x for x in context.portal_categories.variation.getCategoryChildTitleItemList()\n
                  if x[1] in my_list]\n
   else:\n
      return_value =  [x for x in context.portal_categories.variation.getCategoryChildTitleItemList()]\n
elif my_choice == \'variation_default_value\':\n
   return_value = getattr(request,\'my_variation_list\',None)   # Find variation on the REQUEST\n
   return_value = return_value[1]\n
\n
\n
return return_value\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>my_choice=None, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>CashDetail_getOthersForMatrixInput</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
