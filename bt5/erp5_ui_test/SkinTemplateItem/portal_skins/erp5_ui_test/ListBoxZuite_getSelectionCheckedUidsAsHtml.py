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

"""This scripts prints a table of all checked uids as html.\n
The title of the html is in the form "len(checked_uids) == %d"\n
The body contains some /table/tr with td[0] for uid and td[1] for id\n
"""\n
\n
if selection_name is None:\n
  return "selection_name parameter not passed"\n
\n
portal = context.getPortalObject()\n
checked_uids = portal.portal_selections\\\n
                    .getSelectionCheckedUidsFor(selection_name)\n
getObj = portal.portal_catalog.getObject\n
checked_uids_objs = [getObj(uid) for uid in checked_uids]\n
checked_uids_objs.sort(key=lambda x:x.getId())\n
\n
# we produce html for easier Selenium parsing\n
table = "\\n".join(["<tr><td>%s</td><td>%s</td></tr>" % (\n
                    x.getUid(), x.getId()) for x in checked_uids_objs])\n
return """<html>\n
<head><title>len(checked_uids) == %d</title></head>\n
<body>\n
<table>\n
  %s\n
</table>\n
</body>\n
</html>""" % (len(checked_uids), table)\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>selection_name=None, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ListBoxZuite_getSelectionCheckedUidsAsHtml</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>Get Checked Uids as html</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
