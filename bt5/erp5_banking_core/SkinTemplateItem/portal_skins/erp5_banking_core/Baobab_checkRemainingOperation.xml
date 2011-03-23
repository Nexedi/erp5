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
            <value> <string># Make sure there is not any operation wich is not finished yet\n
# This is usefull when we close a counter date\n
\n
document_list = context.CounterDate_getRemainingOperationList(site=site)\n
\n
\n
for document in document_list:\n
  from Products.ERP5Type.Message import Message\n
  from Products.DCWorkflow.DCWorkflow import ValidationFailed\n
  portal_type = document.getTranslatedPortalType()\n
  reference = document.getSourceReference()\n
  if reference is None:\n
    reference = Message(domain=\'ui\',message=\'Not defined\')\n
  message = Message(domain="ui", \n
                message="Sorry, the $portal_type (reference:$reference) is not finished",\n
                mapping={\'portal_type\':portal_type,\'reference\':reference})\n
  raise ValidationFailed,message\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>site=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Baobab_checkRemainingOperation</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
