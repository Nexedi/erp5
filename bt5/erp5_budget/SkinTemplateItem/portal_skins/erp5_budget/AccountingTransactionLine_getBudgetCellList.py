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
            <value> <string>\'\'\'Returns budget cells matching an accounting transaction line.\n
\'\'\'\n
portal = context.getPortalObject()\n
\n
def makeContext(doc, **kw):\n
  categories = []\n
  for k, v in kw.items():\n
    if v:\n
      categories.append(\'%s/%s\' % (k,v))\n
  return doc.asContext(categories=categories)\n
  \n
financial_section = \'\'\n
budget_section = \'\'\n
group = \'\'\n
\n
if context.AccountingTransaction_isSourceView():\n
  node = context.getSourceValue()\n
  if node is not None:\n
    financial_section = node.getFinancialSection()\n
    budget_section = node.getBudgetSection()\n
  section = context.getSourceSectionValue()\n
  if section is not None:\n
    group = section.getGroup()\n
\n
  tmp_context = makeContext(\n
       context,\n
       region=context.getSourceRegion(),\n
       ## XXX or destination region ? this means the budget configuration has\n
       # to be known at that point.\n
       source_section=context.getDestinationSection(),\n
       destination_section=context.getSourceSection(),\n
       source=context.getDestination(),\n
       destination=context.getSource(),\n
       resource=context.getResource(),\n
       financial_section=financial_section,\n
       budget_section=budget_section,\n
       group=group,\n
  )\n
else:\n
  node = context.getDestinationValue()\n
  if node is not None:\n
    financial_section = node.getFinancialSection()\n
    budget_section = node.getBudgetSection()\n
  section = context.getDestinationSectionValue()\n
  if section is not None:\n
    group = section.getGroup()\n
\n
  tmp_context = makeContext(\n
       context,\n
       region=context.getDestinationRegion(), #XXX\n
       destination_section=context.getSourceSection(),\n
       source_section=context.getDestinationSection(),\n
       destination=context.getDestination(),\n
       source=context.getSource(),\n
       resource=context.getResource(),\n
       financial_section=financial_section,\n
       budget_section=budget_section,\n
       group=group,\n
 )\n
\n
return portal.portal_domains.searchPredicateList(context=tmp_context, portal_type=\'Budget Cell\')\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>AccountingTransactionLine_getBudgetCellList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
