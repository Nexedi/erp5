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

# Updates attributes of an Zope document\n
# which is in a class inheriting from ERP5 Base\n
#\n
# TODO\n
#   - Implement validation of matrix fields\n
#   - Implement validation of list fields\n
#\n
from Products.ERP5Type.Message import translateString\n
from Products.Formulator.Errors import ValidationError, FormValidationError\n
\n
request=context.REQUEST\n
\n
try:\n
  # Define form basic fields\n
  form = getattr(context,form_id)\n
  # Validate\n
  form.validate_all_to_request(request)\n
  # Basic attributes\n
  kw = {}\n
  # Parse attributes\n
  for f in form.get_fields():\n
    k = f.id\n
    v = getattr(request,k,None)\n
    if v is not None:\n
      if k[0:3] == \'my_\':\n
        # We only take into account\n
        # the object attributes\n
        k = k[3:]\n
        if getattr(v, \'as_dict\'): # FormBox\n
          kw.update(v.as_dict())\n
        else:\n
          kw[k] = v\n
  # Update basic attributes\n
  context.updateConfiguration(**kw)\n
  context.reindexObject()\n
except FormValidationError, validation_errors:\n
  # Pack errors into the request\n
  field_errors = form.ErrorFields(validation_errors)\n
  request.set(\'field_errors\', field_errors)\n
  return form(request)\n
\n
# for web mode, we should use \'view\' instead of passed form_id\n
# after \'Save & View\'.\n
if request.get(\'is_web_mode\', False) and not editable_mode:\n
  form_id = \'view\'\n
\n
return context.Base_redirect(form_id,\n
  keep_items=dict(portal_status_message=translateString(\'Data Updated.\')))\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>form_id=\'view\', selection_index=0, selection_name=\'\', ignore_layout=0, editable_mode=1</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_editConfiguration</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
