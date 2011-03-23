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
            <value> <string># By default, the destination of a monetary destruction must\n
# be None in order to destroy ressources\n
destination = None\n
\n
if context.getParentValue().isDematerialization() \\\n
  and context.getSource() is not None \\\n
  and context.getSourceSection() is not None:\n
  # We must in this case set the destination to a particular vault\n
  site = context.Baobab_getVaultSite(context.getSource())\n
  site_relative_url = site.getRelativeUrl()\n
  section_id = context.getSourceSectionId()\n
  destination = "%s/%s/%s" % (site_relative_url,\n
                              "caveau/serre/encaisse_des_billets_neufs_non_emis_en_transit_allant_a",\n
                              section_id)\n
return destination\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>*args, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>MonetaryDestructionLine_getBaobabDestination</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
