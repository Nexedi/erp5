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
            <value> <string>source = context.getSource()\n
destination = context.getDestinationSection()\n
context.log(source, destination)\n
if source is None or destination is None:\n
  return None\n
\n
has_banknote = 0\n
has_coin = 0\n
\n
for movement in context.getMovementList():\n
  resource_portal_type = movement.getResourceValue().getPortalType()\n
  if resource_portal_type == \'Coin\':\n
    has_coin = 1\n
    break\n
  elif resource_portal_type == \'Banknote\':\n
    has_banknote = 1\n
    break\n
\n
if has_banknote == 1:\n
  if source.split("/")[-1] == destination.split("/")[-1] or "transit" not in source:\n
    destination = "%s/caveau/serre/encaisse_des_billets_neufs_non_emis" % destination\n
  else:\n
    destination = "%s/caveau/serre/encaisse_des_billets_neufs_non_emis_en_transit_allant_a/%s" % (destination, source.split("/")[-1])\n
elif has_coin == 1:\n
  destination = "%s/caveau/serre/encaisse_des_billets_neufs_non_emis" % destination\n
else:\n
  destination = None\n
\n
return destination\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>*args, **kw</string> </value>
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
            <value> <string>CashMovementNewNotEmitted_getBaobabDestination</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
