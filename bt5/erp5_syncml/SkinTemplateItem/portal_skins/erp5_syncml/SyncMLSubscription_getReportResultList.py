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

"""\n
  Returns the list of results of the specified process\n
  or of the last process if nothing specified.\n
"""\n
\n
def getLastActiveProcess(sub):\n
  """\n
  This returns the last active process finished. So it will\n
  not returns the current one\n
  """\n
  limit = 1\n
  active_process_list = context.getPortalObject().portal_catalog(\n
    portal_type=\'Active Process\', limit=limit,\n
    sort_on=((\'creation_date\', \'DESC\'),\n
             # XXX Work around poor resolution of MySQL dates.\n
             (\'CONVERT(`catalog`.`id`, UNSIGNED)\', \'DESC\')),\n
    causality_uid=sub.getUid())\n
  if len(active_process_list) < limit:\n
    process = None\n
  else:\n
    process = active_process_list[-1].getObject()\n
  return process\n
\n
\n
if active_process is None:\n
  active_process = getLastActiveProcess(context)\n
else:\n
  active_process = context.getPortalObject().restrictedTraverse(active_process)\n
\n
result_list = []\n
\n
if active_process is not None:\n
  result_list = [x for x in active_process.getResultList()]\n
  # High severity will be displayed first\n
  result_list.sort(key=lambda x: -x.severity)\n
\n
return result_list\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>active_process=None, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>SyncMLSubscription_getReportResultList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
