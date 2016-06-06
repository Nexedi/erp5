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
            <value> <string>"""Produce an xml fragment for this accounting transaction and post it to the\n
active result.\n
We need a proxy role to post the result.\n
"""\n
from Products.CMFActivity.ActiveResult import ActiveResult\n
\n
portal = context.getPortalObject()\n
active_process = portal.restrictedTraverse(active_process)\n
accounting_line_list = context.contentValues(portal_type=portal.getPortalAccountingMovementTypeList())\n
\n
if context.getSourceSectionUid() in section_uid_list:\n
  if any([line.getSource(portal_type=\'Account\') for line in accounting_line_list]):\n
    source_xml = context.AccountingTransaction_viewAsSourceFECXML()\n
    active_process.postResult(ActiveResult(detail=source_xml.encode(\'utf8\').encode(\'zlib\')))\n
\n
if context.getDestinationSectionUid() in section_uid_list:\n
  if any([line.getDestination(portal_type=\'Account\') for line in accounting_line_list]):\n
    destination_xml = context.AccountingTransaction_viewAsDestinationFECXML()\n
    active_process.postResult(ActiveResult(detail=destination_xml.encode(\'utf8\').encode(\'zlib\')))\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>active_process, section_uid_list</string> </value>
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
            <value> <string>AccountingTransaction_postFECResult</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
