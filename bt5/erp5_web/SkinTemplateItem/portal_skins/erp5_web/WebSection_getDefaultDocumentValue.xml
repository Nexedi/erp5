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
 This script is part of ERP5 Web\n
\n
 ERP5 Web is a business template of ERP5 which provides a way\n
 to create web sites which can display selected\n
 ERP5 contents through multiple custom web layouts.\n
\n
 This script returns the default document to display\n
 as the front page of a given Web Section or Web Site.\n
 If no default is found, it returns None.\n
\n
 The default implementation should look at published\n
 documents which are associated to the section\n
 through the aggregate relation and try to display those\n
 which are available in the user language if any.\n
\n
 Other implementations are possible: ex. display the last\n
 version in the closest language rather than\n
 the latest version in the user language.\n
\n
 This script is intended to be overriden by creating a new script\n
 within a Web Section or a  Web Site instance. Customisation\n
 is also possible per portal type or per meta type through\n
 portal skins. It is recommended to use the first approach\n
 to host multiple sites on a single ERP5Site instance.\n
"""\n
portal_object = context.getPortalObject()\n
\n
# First find the Web Section or Web Site we belong to\n
current_section = context.getWebSectionValue()\n
\n
# First get all the applicable references\n
# There might be more than one reference due to security differences\n
# (ex. a default restricted web page and a default public web page)\n
reference_list = context.getAggregateReferenceList()\n
if not reference_list: return None # Quick return\n
\n
# We should only display those documents which are shared\n
# to some extend. This list takes into account some common\n
# state IDs used in ERP5.\n
return context.getDocumentValue(name=reference_list,\n
            validation_state=(\'released\', \'released_alive\', \'published\', \'published_alive\',\n
                              \'shared\', \'shared_alive\', \'public\', \'validated\'))\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>_proxy_roles</string> </key>
            <value>
              <tuple>
                <string>Assignor</string>
                <string>Manager</string>
              </tuple>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>WebSection_getDefaultDocumentValue</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
