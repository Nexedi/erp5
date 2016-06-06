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

return """\n
<style type="text/css">\n
body, table {\n
    font-family: Verdana,Arial,sans-serif;\n
    font-size: 24px;\n
    margin:auto;\n
}\n
table {\n
    border: 1px solid #CCCCCC;\n
    border-collapse: collapse;\n
}\n
th, td {\n
    padding-left: 0.3em;\n
    padding-right: 0.3em;\n
}\n
a {\n
    text-decoration: none;\n
}\n
.title {\n
    font-style: italic;\n
}\n
.selected {\n
    background-color: #FFFFCC;\n
}\n
.status_done {\n
    background-color: #EEFFEE;\n
}\n
.status_passed {\n
    background-color: #CCFFCC;\n
}\n
.status_failed {\n
    background-color: #FFCCCC;\n
}\n
.breakpoint {\n
    background-color: #CCCCCC;\n
    border: 1px solid black;\n
}\n
</style>\n
\n
"""\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>TestPage_testReportCSS</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
