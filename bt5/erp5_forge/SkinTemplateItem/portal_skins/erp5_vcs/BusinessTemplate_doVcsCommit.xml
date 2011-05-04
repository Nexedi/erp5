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

kw = {}\n
request = container.REQUEST\n
for k in \'added\', \'modified\', \'removed\':\n
  file_list = request.get(k, ())\n
  # XXX: ERP5VCS_doCreateJavaScriptStatus should send lists\n
  if isinstance(file_list, basestring):\n
    file_list = file_list != \'none\' and filter(None, file_list.split(\',\')) or ()\n
  kw[k] = file_list\n
\n
changelog = request.get(\'changelog\', \'\')\n
if not changelog.strip():\n
  from Products.ERP5Type.Message import translateString\n
  error_msg = "Please set a ChangeLog message."\n
  request.set(\'portal_status_message\', translateString(error_msg))\n
  request.set(\'cancel_url\', context.absolute_url() +\n
    \'/BusinessTemplate_viewVcsStatus?do_extract:int=0\'\n
    \'&portal_status_message=Commit%20cancelled.\')\n
  return context.asContext(**kw).BusinessTemplate_viewVcsChangelog()\n
\n
try:\n
  return context.getVcsTool().commit(changelog, **kw)\n
except Exception, error:\n
  return context.BusinessTemplate_handleException(error, script.id)\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>**kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>BusinessTemplate_doVcsCommit</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
