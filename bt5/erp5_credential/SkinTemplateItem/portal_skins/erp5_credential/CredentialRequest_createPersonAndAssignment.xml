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
  For a credential request as context, we set the related person informations,\n
  the assignments of the person and send notificaiton email\n
  Proxy:\n
  Auditor -- allow to get credential request informations\n
"""\n
\n
# check the script is not called from a url\n
if REQUEST is not None:\n
  return None\n
\n
portal = context.getPortalObject()\n
portal_preferences = context.portal_preferences\n
\n
# XXX by default we don\'t want to automatically create/update organisation\n
# Someone should confirm this informations before creating the organisation\n
#if context.getOrganisationTitle():\n
#  related_portal_type.append(\'Organisation\')\n
\n
#Create related object, pass a copy of the dict\n
context.CredentialRequest_setDefaultDestinationDecision([x for x in related_portal_type])\n
\n
# Check consistency of the subscription, pass a copy of the dict\n
context.Credential_checkConsistency([x for x in related_portal_type])\n
\n
# Create assignment\n
context.CredentialRequest_updatePersonAssignment()\n
\n
# Create account\n
login, password = context.CredentialRequest_createUser()\n
\n
# Fill related object with credential request\n
for portal_type in related_portal_type:\n
  getattr(context,\'CredentialRequest_setRegisteredInformationTo%s\' % portal_type.replace(\' \',\'\'))()\n
\n
# Update Local Roles\n
context.CredentialRequest_updateLocalRolesOnSecurityGroups()\n
\n
if password is not None:\n
  if password.startswith(\'{SSHA}\'):\n
    #password is encoded, set it to None to script witch send the password to user\n
    password = None\n
# Send notification in activities\n
context.activate(activity=\'SQLQueue\').CredentialRequest_sendAcceptedNotification(login, password)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>related_portal_type = [\'Person\'], REQUEST=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>CredentialRequest_createPersonAndAssignment</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
