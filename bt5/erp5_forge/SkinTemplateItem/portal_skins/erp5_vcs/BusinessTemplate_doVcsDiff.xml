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

vcs_tool = context.getVcsTool()\n
template_tool = context.getPortalObject().portal_templates\n
if template_tool.getDiffFilterScriptList():\n
  DiffFile = template_tool.getFilteredDiff\n
else:\n
  from Products.ERP5Type.DiffUtils import DiffFile\n
\n
print \'<div style="color: black">\'\n
\n
# XXX: ERP5VCS_doCreateJavaScriptStatus should send lists\n
if isinstance(added, basestring):\n
  added = added != \'none\' and filter(None, added.split(\',\')) or ()\n
if isinstance(modified, basestring):\n
  modified = modified != \'none\' and filter(None, modified.split(\',\')) or \'\'\n
if isinstance(removed, basestring):\n
  removed = removed != \'none\' and filter(None, removed.split(\',\')) or ()\n
\n
for f in modified:\n
  diff = DiffFile(vcs_tool.diff(f))\n
  if not diff:\n
    continue\n
  print \'<input name="modified" value="%s" type="checkbox" checked="checked" />\'% f\n
  print vcs_tool.getHeader(f)\n
  print diff.toHTML()\n
  print "<hr/><br/>"\n
\n
for f in added:\n
  print \'<input name="added" value="%s" type="checkbox" checked="checked" />\'% f\n
  print vcs_tool.getHeader(f)\n
  print "<br/><span style=\'color: green;\'>File Added</span><br/><br/><hr/><br/>"\n
\n
for f in removed:\n
  print \'<input name="removed" value="%s" type="checkbox" checked="checked" />\'% f\n
  print vcs_tool.getHeader(f)\n
  print "<br/><span style=\'color: red;\'>File Removed</span><br/><br/><hr/><br/>"\n
\n
print \'</div>\'\n
return printed\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>added=(), modified=(), removed=()</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>BusinessTemplate_doVcsDiff</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
