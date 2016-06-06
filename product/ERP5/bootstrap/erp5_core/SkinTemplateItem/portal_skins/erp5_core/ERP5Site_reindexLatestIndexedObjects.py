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
            <value> <string># Reindex objects which indexation_timestamp is at most\n
# delta seconds before current time (ie, bound inclued).\n
# Unindex objects which cannot be found.\n
# Default delta is 172800 (=2*24*60*60=2 days)\n
\n
portal = context.getPortalObject()\n
catalog = portal.portal_catalog.getSQLCatalog()\n
candidate_list = context.ERP5Site_zGetLatestIndexedObjectList(delta=delta)\n
\n
reindex_count = 0\n
unindex_count = 0\n
\n
for candidate in candidate_list:\n
  path = candidate[\'path\']\n
  try:\n
    object = portal.restrictedTraverse(path)\n
  except KeyError:\n
    # Object is unreachable, remove it from catalog\n
    # Use SQLQueue because all activities are triggered on the same object,\n
    # and SQLDict keeps only one.\n
    catalog.activate(activity="SQLQueue").unindexObject(uid=candidate[\'uid\'])\n
    unindex_count += 1\n
  else:\n
    object.reindexObject()\n
    reindex_count += 1\n
\n
print \'%s object reindexed, %s object unindexed\' % (reindex_count, unindex_count)\n
return printed\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>delta=172800</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ERP5Site_reindexLatestIndexedObjects</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
