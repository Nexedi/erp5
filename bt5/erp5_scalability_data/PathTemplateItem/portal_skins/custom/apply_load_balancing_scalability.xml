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

import json\n
portal_actitivities = context.getPortalObject().portal_activities\n
\n
distribution_node = \'\'\n
processing_nodes = []\n
idle_nodes = []\n
\n
# Store each node to distribution, processing or idle group\n
# in function of his port number.\n
node_list = portal_actitivities.getNodeList()\n
for node in node_list:\n
  port = int(node.split(":")[1])\n
  # Node with port >= 2300 are processing nodes, others are idle nodes\n
  if port >= 2300:\n
    processing_nodes.append(node)\n
  else:\n
    idle_nodes.append(node)\n
\n
  # Special port for distribution\n
  if port == 2350 or port == 2250:\n
    distribution_node = node\n
\n
# Change distribution node\n
portal_actitivities.manage_setDistributingNode(distribution_node)\n
# Add processing nodes\n
for node in processing_nodes:\n
  portal_actitivities.manage_addToProcessingList((node,))\n
# Remove idle nodes from processing nodes\n
for node in idle_nodes:\n
  portal_actitivities.manage_removeFromProcessingList((node,))\n
\n
print \'Distributing Node:\'\n
print json.dumps(portal_actitivities.getDistributingNode())\n
print \'Processing Nodes:\'\n
print json.dumps(portal_actitivities.getProcessingNodeList())\n
\n
return printed\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>apply_load_balancing_scalability</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
