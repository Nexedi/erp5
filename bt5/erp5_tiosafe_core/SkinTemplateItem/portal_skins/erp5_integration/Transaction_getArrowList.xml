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
            <value> <string>""" Retrieve the arrow list of the transaction. """\n
transaction = context.getObject()\n
\n
sub = context.restrictedTraverse(context_document)\n
while sub.getParentValue().getPortalType() !=  "Synchronization Tool":\n
  sub = sub.getParentValue()\n
\n
im = sub.Base_getRelatedObjectList(portal_type=\'Integration Module\')[0].getObject()\n
org_module = im.getParentValue().organisation_module\n
org_pub = org_module.getSourceSectionValue()\n
person_module = im.getParentValue().person_module\n
person_pub = person_module.getSourceSectionValue()\n
\n
# contains the result list\n
result_list = []\n
\n
# set arrow list\n
arrow_list = [\n
    [\'getSource\', \'getDestination\', ""],\n
    [\'getSourceAdministration\', \'getDestinationAdministration\', \'Administration\'],\n
    [\'getSourceCarrier\', \'getDestinationCarrier\', \'Carrier\'],\n
    [\'getSourceDecision\', \'getDestinationDecision\', \'Decision\'],\n
    [\'getSourceSection\', \'getDestinationSection\', \'Ownership\'],\n
    [\'getSourcePayment\', \'getDestinationPayment\', \'Payment\'],\n
]\n
\n
# browse and add the arrows if exists a source or a destination\n
for get_source, get_destination, category in arrow_list:\n
  source_free_text = getattr(transaction, "%sFreeText" %get_source)(None)\n
  source = getattr(transaction, "%sValue" %get_source)(None)\n
  destination_free_text = getattr(transaction, "%sFreeText" %get_destination)(None)\n
  destination = getattr(transaction, "%sValue" %get_destination)(None)\n
\n
  if source is not None or destination is not None:\n
    arrow_dict = {\'source\': None, \'destination\': None, \'category\': category}\n
  else:\n
    continue\n
\n
  if source_free_text is not None:\n
    arrow_dict[\'source\'] = source_free_text\n
  elif source is not None:\n
    if source.getPortalType() == "Person":\n
      arrow_dict[\'source\'] = person_pub.getGidFromObject(object=source, encoded=False)\n
    else:\n
      arrow_dict[\'source\'] = org_pub.getGidFromObject(object=source, encoded=False)\n
\n
  if destination_free_text is not None:\n
    arrow_dict[\'destination\'] = destination_free_text\n
  elif destination is not None:\n
    if destination.getPortalType() == "Person":\n
      arrow_dict[\'destination\'] = person_pub.getGidFromObject(object=destination, encoded=False)\n
    else:\n
      arrow_dict[\'destination\'] = org_pub.getGidFromObject(object=destination, encoded=False)\n
\n
  result_list.append(arrow_dict)\n
\n
return result_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>context_document</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Transaction_getArrowList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
