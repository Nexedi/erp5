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
            <value> <string>from Products.Formulator.Errors import ValidationError, FormValidationError\n
from ZTUtils import make_query\n
\n
request=context.REQUEST\n
\n
if isinstance(list_form_id,tuple):\n
  list_form_id = list_form_id[0]\n
# The type list is not working with isinstance, I have do do this bad hack\n
if hasattr(list_form_id,\'sort\'):\n
  list_form_id = list_form_id[0]\n
\n
module_name = context.getId()\n
\n
try:\n
  # Validate the form\n
  form = getattr(context,dialog_id)\n
  form.validate_all_to_request(request)\n
  kw = {}\n
  for f in form.get_fields():\n
    k = f.id\n
    # XXX Remove your_ parameters...\n
    k = k[5:]\n
    v = getattr(request,k,None)\n
    if v is not None and k != \'list_form_id\' :\n
      kw[k] = v\n
    if list_method_id is not None and list_method_id  != \'\' :\n
      kw[\'list_method_id\'] = list_method_id\n
  url_params_string = make_query(kw)\n
#  raise str(kw), url_params_string\n
\n
except FormValidationError, validation_errors:\n
  # Pack errors into the request\n
  field_errors = form.ErrorFields(validation_errors)\n
  request.set(\'field_errors\', field_errors)\n
  return form(request)\n
\n
\n
if url_params_string != \'\':\n
  redirect_url = \'%s/%s?%s\' % ( context.absolute_url()\n
                            , list_form_id\n
                            , url_params_string\n
                            )\n
else:\n
  redirect_url = \'%s/%s\' % ( context.absolute_url()\n
                            , list_form_id\n
                            )\n
\n
\n
return request.RESPONSE.redirect( redirect_url )\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>form_id,dialog_id,list_form_id,list_method_id=\'\'</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_searchHandler</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
