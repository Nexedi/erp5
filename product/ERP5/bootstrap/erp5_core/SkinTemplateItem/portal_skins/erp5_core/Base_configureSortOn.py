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
            <value> <string># Updates attributes of an Zope document\n
# which is in a class inheriting from ERP5 Base\n
\n
\n
from Products.Formulator.Errors import ValidationError, FormValidationError\n
\n
request = context.REQUEST\n
field_sort_type = request.form.get(\'field_sort_type\', None)\n
form = context.Folder_viewSortOnDialog\n
\n
try:\n
  # No validation for now\n
  # Direct access to field (BAD)\n
  sort_on = []\n
  i = 0\n
  for k in field_sort_on:\n
    if k != \'None\':\n
      if field_sort_type is None:\n
        v = field_sort_order[i]\n
        sort_on += [(k,v)]\n
      else:\n
        v = field_sort_order[i]\n
        t = field_sort_type[i]\n
        sort_on += [(k, v, t)]\n
    i += 1\n
  context.portal_selections.setSelectionSortOrder(selection_name, sort_on)\n
except FormValidationError, validation_errors:\n
  # Pack errors into the request\n
  field_errors = form.ErrorFields(validation_errors)\n
  request.set(\'field_errors\', field_errors)\n
  return form(request)\n
else:\n
  redirect_url = context.portal_selections.getSelectionListUrlFor(selection_name)\n
\n
request[ \'RESPONSE\' ].redirect( redirect_url )\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>form_id,selection_name,field_sort_on,field_sort_order</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_configureSortOn</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
