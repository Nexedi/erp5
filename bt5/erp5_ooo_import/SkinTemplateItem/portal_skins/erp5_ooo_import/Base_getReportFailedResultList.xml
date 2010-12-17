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
            <value> <string>from Products.ERP5Type.Document import newTempBase\n
from string import zfill\n
\n
portal_object = context.getPortalObject()\n
num = 0\n
result_listbox = []\n
\n
if active_process_path is None:\n
  #return []\n
  active_process_path=context.REQUEST.get(\'active_process\')\n
\n
active_process_value = context.getPortalObject().restrictedTraverse(active_process_path)\n
result_list = [[x.method_id, x.result] for x in active_process_value.getResultList()]\n
\n
result_list.sort()\n
\n
for [method_id, result] in result_list:\n
  safe_id = context.Base_getSafeIdFromString(\'result %s\' % num)\n
  num += 1\n
  int_len = 7\n
  if not result[\'success\']:\n
      o = newTempBase(portal_object, safe_id)\n
      o.setUid(  \'new_%s\' % zfill(num, int_len)) # XXX There is a security issue here\n
      o.edit(uid=\'new_%s\' % zfill(num, int_len)) # XXX There is a security issue here\n
      o.edit(**result[\'object\'])\n
      result_listbox.append(o)\n
\n
return result_listbox\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>active_process_path=None, **kw</string> </value>
        </item>
        <item>
            <key> <string>_proxy_roles</string> </key>
            <value>
              <tuple>
                <string>Manager</string>
              </tuple>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_getReportFailedResultList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
