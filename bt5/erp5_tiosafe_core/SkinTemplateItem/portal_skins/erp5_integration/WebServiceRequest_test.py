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
            <value> <string># Build parameter dict\n
parameter_list= parameters.split("\\n")\n
parameter_dict = {}\n
for parameter in parameter_list:\n
  try:\n
    k,v = parameter.split(\'=\')\n
  except ValueError:\n
    continue\n
  parameter_dict[k] = v\n
\n
\n
translateString = context.Base_translateString\n
\n
object_list = context(test_mode=True, **parameter_dict)\n
\n
result_list = []\n
\n
if context.getLastRequestError() is None:\n
  error = None\n
  for obj in object_list:\n
    try:\n
      xml = obj.asXML(debug=True)\n
    except (ValueError, NotImplementedError), msg:\n
      error = msg\n
      continue\n
    if not xml:\n
      error = "Check your mapping, some might be missing"\n
    else:\n
      result_list.append(xml,)\n
\n
\n
  if error:\n
    context.edit(last_request_error = "%r" %(error,))\n
\n
context.edit(last_request_tiosafe_xml_result=\'\\n\'.join(result_list))\n
\n
portal_status_message = translateString("Request Executed.")\n
context.Base_redirect("WebServiceRequest_viewTestResult", keep_items = dict(portal_status_message=portal_status_message))\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>parameters=""</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>WebServiceRequest_test</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
