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
            <value> <string># this script allows to create a new related event by causality for\n
# the current event\n
from DateTime import DateTime\n
from Products.CMFCore.WorkflowCore import WorkflowException\n
N_ = context.Base_translateString\n
date = DateTime()\n
portal = context.getPortalObject()\n
\n
if portal_type not in portal.event_module.getVisibleAllowedContentTypeList():\n
  raise WorkflowException, "You Don\'t Have Permission to Add New Event"\n
\n
# Create the draft Event\n
related_event = portal.event_module.newContent(\n
                       portal_type=portal_type,\n
                       title=title,\n
                       description=description,\n
                       start_date=date,\n
                       source=context.getDefaultDestination(),\n
                       destination=context.getDefaultSource(),\n
                       causality=context.getRelativeUrl(),\n
                       follow_up=context.getFollowUp(),\n
                       )\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>portal_type, title, description</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Event_createRelatedEvent</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
