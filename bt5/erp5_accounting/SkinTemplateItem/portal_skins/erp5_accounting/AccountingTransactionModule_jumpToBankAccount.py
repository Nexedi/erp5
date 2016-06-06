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
            <value> <string># Jump to a bank account of the current organisation\n
Base_translateString = context.Base_translateString\n
request=context.REQUEST\n
portal = context.getPortalObject()\n
organisation = portal.restrictedTraverse(\n
          portal.portal_preferences.getPreferredAccountingTransactionSourceSection())\n
\n
if organisation is not None :\n
  selection_uid_list = [ bank_account.getUid() for bank_account \\\n
     in organisation.searchFolder(portal_type=portal.getPortalPaymentNodeTypeList()) ]\n
  if len(selection_uid_list) != 0 : \n
    kw = {\'uid\': selection_uid_list}\n
    portal.portal_selections.setSelectionParamsFor(\'Base_jumpToRelatedObjectList\', kw)\n
    request.set(\'object_uid\', context.getUid())\n
    request.set(\'uids\', selection_uid_list)\n
    return context.Base_jumpToRelatedObjectList(\n
          uids=selection_uid_list, REQUEST=request)\n
\n
return context.Base_redirect(form_id, keep_items=dict(portal_status_message=Base_translateString(\'No bank account for current organisation.\')))\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>form_id=\'view\'</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>AccountingTransactionModule_jumpToBankAccount</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
