<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <tuple>
        <global name="PythonScript" module="Products.PythonScripts.PythonScript"/>
        <tuple/>
      </tuple>
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
            <value> <string>#try:         //Implement try catch instead of if else\n
#from Products.ERP5Type.JSON import dumps\n
from Products.ERP5Type.JSONEncoder import encodeInJson as dumps\n
\n
portal = context.getPortalObject()\n
reference = portal.portal_membership.getAuthenticatedMember().getUserName()\n
processing = None\n
\n
if reference == "Anonymous User":\n
  processing = "anonymous_user"\n
else:\n
  session = portal.portal_sessions[reference]\n
  document_url = session.get(\'document_url\',None)\n
  if document_url is None:\n
    processing = "document_url_error"\n
  else:\n
    document = portal.restrictedTraverse(document_url)\n
\n
  try:\n
    processing = document.getExternalProcessingState()\n
  except AttributeError:\n
    processing = \'empty\'\n
\n
informations = { \'processing\': processing,\n
                  \'reference\': reference  }\n
\n
if informations[\'processing\'] in [\'converted\', \'conversion_failed\',\'empty\']:\n
  informations[\'permanent_url\'] = document.Document_getPermanentUrl()\n
  print dumps(informations) #print info before del object\n
  portal.portal_sessions.manage_delObjects(reference)\n
else:\n
  print dumps(informations)\n
\n
return printed\n
</string> </value>
        </item>
        <item>
            <key> <string>_code</string> </key>
            <value>
              <none/>
            </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>_proxy_roles</string> </key>
            <value>
              <tuple/>
            </value>
        </item>
        <item>
            <key> <string>errors</string> </key>
            <value>
              <tuple/>
            </value>
        </item>
        <item>
            <key> <string>func_code</string> </key>
            <value>
              <object>
                <klass>
                  <global name="FuncCode" module="Shared.DC.Scripts.Signature"/>
                </klass>
                <tuple/>
                <state>
                  <dictionary>
                    <item>
                        <key> <string>co_argcount</string> </key>
                        <value> <int>0</int> </value>
                    </item>
                    <item>
                        <key> <string>co_varnames</string> </key>
                        <value>
                          <tuple>
                            <string>_print_</string>
                            <string>_print</string>
                            <string>Products.ERP5Type.JSONEncoder</string>
                            <string>encodeInJson</string>
                            <string>dumps</string>
                            <string>_getattr_</string>
                            <string>context</string>
                            <string>portal</string>
                            <string>reference</string>
                            <string>None</string>
                            <string>processing</string>
                            <string>_getitem_</string>
                            <string>session</string>
                            <string>document_url</string>
                            <string>document</string>
                            <string>AttributeError</string>
                            <string>informations</string>
                            <string>_write_</string>
                          </tuple>
                        </value>
                    </item>
                  </dictionary>
                </state>
              </object>
            </value>
        </item>
        <item>
            <key> <string>func_defaults</string> </key>
            <value>
              <none/>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Document_getPropertiesAsJSON</string> </value>
        </item>
        <item>
            <key> <string>warnings</string> </key>
            <value>
              <tuple/>
            </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
