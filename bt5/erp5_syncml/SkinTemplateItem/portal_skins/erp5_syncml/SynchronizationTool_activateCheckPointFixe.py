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

sub_path = method_kw.get("subscription_path")\n
sub = context.getPortalObject().restrictedTraverse(sub_path)\n
search_kw = dict(kw)\n
packet_size = search_kw.pop(\'packet_size\', 30)\n
limit = packet_size * search_kw.pop(\'activity_count\', 100)\n
\n
r = sub.getDocumentIdList(limit=limit, **search_kw)\n
\n
result_count = len(r)\n
if result_count:\n
  if result_count == limit:\n
    # Recursive call to prevent too many activity generation\n
    next_kw = dict(activate_kw, priority=1+activate_kw.get(\'priority\', 1))\n
    kw["min_id"] = r[-1].getId()\n
    sub.activate(**next_kw).SynchronizationTool_activateCheckPointFixe(\n
      callback, method_kw, activate_kw, **kw)\n
\n
  r = [x.getId() for x in r]\n
  callback_method = getattr(sub.activate(**activate_kw), callback)\n
  for i in xrange(0, result_count, packet_size):\n
    callback_method(id_list=r[i:i+packet_size],\n
                    **method_kw)\n
\n
if result_count < limit:\n
  # Register end of point fixe\n
  from Products.CMFActivity.ActiveResult import ActiveResult\n
  active_result = ActiveResult()\n
  active_result.edit(summary=\'Info\',\n
                   severity=0,\n
                   detail="Point fixe check ended at %r" % (DateTime().strftime("%d/%m/%Y %H:%M"),))\n
  sub.activate(active_process=method_kw["active_process"],\n
              activity=\'SQLQueue\', \n
              priority=2,).ERP5Site_saveCheckCatalogTableResult(active_result)\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>callback, method_kw, activate_kw, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>SynchronizationTool_activateCheckPointFixe</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
