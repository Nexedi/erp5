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

import json\n
#from Products.ERP5Type.Log import log\n
# use JSON.parse as json.loads and JSON.stringify as json.dumps\n
\n
context.REQUEST.response.setHeader("Access-Control-Allow-Origin", "*")\n
\n
# dataType "json"\n
# when sending -> [{"name": stringA, "value": stringB}]\n
# context.REQUEST.form <- {stringA: stringB}\n
\n
jio = context.JIO_class()\n
\n
try: doc = jio.jsonUtf8Loads(context.REQUEST.form["doc"])\n
except KeyError:\n
  return jio.sendError(jio.createBadRequestDict("Cannot get document", "No document information received"))\n
\n
try: mode = str(context.REQUEST.form["mode"])\n
except KeyError: mode = "generic"\n
jio.setMode(mode)\n
\n
try:\n
  attachment_data = jio.getDocumentAttachment(doc)\n
except ValueError as e:\n
  return jio.sendError(jio.createConflictDict("Cannot get attachment", str(e)))\n
except LookupError as e:\n
  return jio.sendError(jio.createNotFoundDict("Cannot get attachment", str(e)))\n
\n
return jio.sendSuccess(attachment_data)\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>JIO_getAttachment</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
