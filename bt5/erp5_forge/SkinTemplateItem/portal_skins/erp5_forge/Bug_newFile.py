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
  attaches it to the current ticket.\n
"""\n
translateString = context.Base_translateString\n
\n
default_bug_line = getattr(context, "default_bug_line", None)\n
if default_bug_line is None and context.getPortalType() == \'Bug\':\n
  default_bug_line = context.newContent(id="default_bug_line",\n
                                        portal_type="Bug Line",\n
                                        title="Default Bug Line")\n
elif default_bug_line is None:\n
  default_bug_line = context\n
\n
# Create a new File or Image Document\n
document = default_bug_line.newContent(portal_type=portal_type,\n
                                       description=description,\n
                                       title=title,\n
                                       file=file,\n
                                       reference=kw.get(\'reference\'),\n
                                       version=kw.get(\'version\'),\n
                                       language=kw.get(\'language\'))\n
\n
if context.getPortalType() == \'Bug\':\n
  bug = context\n
else:\n
  bug = context.getParentValue()\n
body = """\n
New %s was added.\n
 Title: %s\n
 Description: %s\n
 Link: %s/view\n
\n
 Bug Title: %s\n
 Bug Link: %s/view\n
""" % (document.getPortalType(),\n
       document.getTitle(), document.getDescription(),\n
       document.getAbsoluteUrl(), bug.getTitle(),\n
       bug.getAbsoluteUrl())\n
\n
recipient_list= bug.Bug_getRecipientValueList()\n
sender = bug.Bug_getNotificationSenderValue()\n
\n
portal = bug.getPortalObject()\n
portal.portal_notifications.sendMessage(sender=sender,\n
                          recipient=recipient_list,\n
                          subject="[ERP5 Bug] [New File] %s" % (bug.getTitle()),\n
                          message=body)\n
\n
# Redirect to even\n
portal_status_message = translateString("New ${portal_type} added.",\n
                                    mapping = dict(portal_type = translateString(portal_type)))\n
return document.Base_redirect(\'view\', keep_items = dict(portal_status_message=portal_status_message), **kw)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>portal_type, title, description, file, form_id=\'view\', **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Bug_newFile</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
