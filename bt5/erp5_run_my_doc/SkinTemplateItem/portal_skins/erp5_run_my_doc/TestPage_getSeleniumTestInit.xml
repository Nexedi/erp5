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

request = context.REQUEST\n
\n
url = request.get(\'url\', None)\n
if url is not None:\n
  html_init = """<tr>\n
          <td>store</td>\n
          <td>%s</td>\n
          <td>base_url</td>\n
        </tr>\n
""" % url\n
else:\n
  html_init = """<span metal:use-macro="container/Zuite_CommonTemplate/macros/init" style="display: none;">init</span>"""\n
\n
html_init += """        <tr>\n
          <td>store</td>\n
          <!-- ERP5TypeTestCase is the default for any UnitTest -->\n
          <td>%s</td>\n
          <td>base_user</td>\n
         </tr>\n
""" % request.get(\'user\', "ERP5TypeTestCase")\n
\n
html_init += """        <tr>\n
          <td>store</td>\n
          <td>%s</td>\n
          <td>base_password</td>\n
         </tr>""" % request.get(\'password\', "")\n
\n
return html_init\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>TestPage_getSeleniumTestInit</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
