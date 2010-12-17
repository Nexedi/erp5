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
            <value> <string>portal = context.getPortalObject()\n
N_ = portal.Base_translateString\n
\n
if not application_number and id:\n
  application_number = id\n
\n
keep_items = {}\n
\n
# default view is history view\n
form_id=\'PDFDocument_viewHistory\'\n
\n
if application_number:\n
  document = context.portal_catalog.getResultValue(id=application_number)\n
  state = document.getValidationState()\n
  if document is not None:\n
    if state == \'draft\':\n
      form_id=\'view\'\n
    else:\n
      form_id=\'PDFDocument_viewHistory\'\n
    return document.Base_redirect(form_id=form_id, keep_items=keep_items)\n
\n
# Prepare message\n
msg = N_(\'Sorry, this document is not available\')\n
return context.Base_redirect(form_id=\'view\', keep_items = {\'portal_status_message\' : msg})\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>application_number=None, id=None, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>EGov_goToDocument</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
