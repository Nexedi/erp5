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

# XXX: This does not show anything for folders.\n
#      A recursive diff should be displayed instead.\n
# XXX: Consider merging BusinessTemplate_{do,view}VcsMultiDiff \n
# TODO: handle Svn SSL/login exceptions, preferably reusing vcs_dialog(_error)\n
# TODO: Git support\n
\n
from Products.ERP5Type.DiffUtils import DiffFile\n
\n
request = context.REQUEST\n
try:\n
  revision_list = [uid.split(\'.\', 1) for uid in request[\'uids\']]\n
  revision_list.sort()\n
  rev2, rev1 = revision_list\n
except (KeyError, ValueError):\n
  request.set(\'portal_status_message\', \'You must select TWO revisions.\')\n
  return context.BusinessTemplate_viewVcsLog()\n
\n
vcs_tool = context.getVcsTool()\n
diff = vcs_tool.getHeader(added)\n
diff += \'<hr/>\'\n
diff += DiffFile(vcs_tool.diff(added, revision1=rev1[1], revision2=rev2[1])).toHTML()\n
return context.asContext(diff=diff).BusinessTemplate_viewVcsMultiDiff()\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>added, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>BusinessTemplate_doVcsMultiDiff</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
