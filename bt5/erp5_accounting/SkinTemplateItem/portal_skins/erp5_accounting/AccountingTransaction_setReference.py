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
            <value> <string># Get sections.\n
source_section = None\n
source_section_value = context.getSourceSectionValue()\n
if source_section_value is not None \\\n
      and source_section_value.getPortalType() == \'Organisation\':\n
  source_section_value = \\\n
      source_section_value.Organisation_getMappingRelatedOrganisation()\n
  source_section = source_section_value.getRelativeUrl()\n
\n
destination_section = None\n
destination_section_value = context.getDestinationSectionValue()\n
if destination_section_value is not None \\\n
      and destination_section_value.getPortalType() == \'Organisation\':\n
  destination_section_value = \\\n
      destination_section_value.Organisation_getMappingRelatedOrganisation()\n
  destination_section = destination_section_value.getRelativeUrl()\n
\n
portal = context.getPortalObject()\n
id_generator = portal.portal_ids.generateNewId\n
previous_id_getter = portal.portal_ids.getLastGeneratedId\n
\n
# Invoice Reference is automatically filled only for Sale Invoice context.\n
if context.getPortalType() == \'Sale Invoice Transaction\':\n
  if not context.getReference():\n
    invoice_id_group = (\'accounting\', \'invoice\', source_section)\n
    invoice_reference = id_generator(id_generator=\'uid\',\n
                                     id_group=invoice_id_group,\n
                                     default=previous_id_getter(invoice_id_group,\n
                                     default=0) + 1)\n
    context.setReference(invoice_reference)\n
\n
\n
# Generate new values for Source Reference and Destination Reference.\n
if not context.getSourceReference():\n
  period = context.AccountingTransaction_getAccountingPeriodForSourceSection()\n
  period_code = \'\'\n
  if period is not None:\n
    period_code = period.getShortTitle() or period.getTitle() or \'\'\n
  if not period_code:\n
    period_code = str(context.getStartDate().year())\n
  source_id_group = (\'accounting\', \'section\', source_section, period_code)\n
  source_reference = id_generator(id_generator=\'uid\',\n
                                  id_group=source_id_group,\n
                                  default=previous_id_getter(source_id_group,\n
                                                             default=0) + 1)\n
  context.setSourceReference(\'%s-%s\' % (period_code, source_reference))\n
\n
if not context.getDestinationReference():\n
  period = context.AccountingTransaction_getAccountingPeriodForDestinationSection()\n
  period_code = \'\'\n
  if period is not None:\n
    period_code = period.getShortTitle() or period.getTitle() or \'\'\n
  if not period_code:\n
    period_code = str(context.getStopDate().year())\n
  destination_id_group = (\'accounting\', \'section\', destination_section, period_code)\n
  destination_reference = id_generator(id_generator=\'uid\',\n
                                       id_group=destination_id_group,\n
                                       default=previous_id_getter(destination_id_group,\n
                                                                    default=0) + 1)\n
  context.setDestinationReference(\'%s-%s\' % (period_code, destination_reference))\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
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
            <value> <string>AccountingTransaction_setReference</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
