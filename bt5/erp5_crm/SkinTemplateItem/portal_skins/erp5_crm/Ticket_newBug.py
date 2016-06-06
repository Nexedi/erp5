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
            <value> <string>"""\n
  This script creates a new event with given metadata and\n
  attaches it to the current bug.\n
"""\n
Base_translateString = context.Base_translateString\n
portal_type = \'Bug\'\n
module = context.getDefaultModule(portal_type)\n
\n
if portal_type not in module.getVisibleAllowedContentTypeList():\n
  return context.Base_redirect(form_id,\n
                               keep_items=dict(\n
    portal_status_message=Base_translateString("You do not have permission to add new bug.")))\n
\n
# Create a new event\n
bug = module.newContent(portal_type=portal_type,\n
                        description=description,\n
                        title=title,\n
                        follow_up=context.getRelativeUrl())\n
\n
# Redirect to even\n
portal_status_message = Base_translateString(\n
  "Created and associated a new ${portal_type} to the ticket.",\n
  mapping = dict(portal_type=Base_translateString(portal_type)))\n
return bug.Base_redirect(\'view\', keep_items = dict(portal_status_message=portal_status_message), **kw)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>title, description, form_id=\'view\', **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Ticket_newBug</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
