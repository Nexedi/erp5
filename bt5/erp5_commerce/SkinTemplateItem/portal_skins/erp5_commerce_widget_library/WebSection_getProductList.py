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
            <value> <string>#TODO : USE CACHE\n
#the goal of this script is to get all the related product of this section\n
current_web_section = context.REQUEST.get(\'current_web_section\', context)\n
product_list = []\n
\n
if not kw.has_key(\'portal_type\'):\n
  kw[\'portal_type\'] = \'Product\'\n
\t\t \n
if not kw.has_key(\'limit\'):\t\t \n
  kw[\'limit\'] = limit\t\t \n
\t\t \n
if not kw.has_key(\'all_versions\'):\t\t \n
  kw[\'all_versions\'] = 1\t\t \n
\t\t \n
if not kw.has_key(\'all_languages\'):\t\t \n
  kw[\'all_languages\'] = 1\t\t \n
\t\t \n
for key in [\'limit\',\'all_versions\',\'all_languages\']:\t\t \n
  kw[key] = int(kw[key])\t\t \n
\t\t \n
product_list = current_web_section.getDocumentValueList(**kw)\n
return product_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>limit=1000, **kw</string> </value>
        </item>
        <item>
            <key> <string>_proxy_roles</string> </key>
            <value>
              <tuple>
                <string>Assignee</string>
                <string>Assignor</string>
                <string>Associate</string>
                <string>Auditor</string>
                <string>Authenticated</string>
                <string>Author</string>
                <string>Manager</string>
                <string>Member</string>
                <string>Owner</string>
                <string>Reviewer</string>
              </tuple>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>WebSection_getProductList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
