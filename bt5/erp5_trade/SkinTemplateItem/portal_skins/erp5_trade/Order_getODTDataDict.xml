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
            <value> <string>def getSourceReference(line):\n
  category_list = line.getAcquiredCategoryList()\n
  portal_type_list = (\'Purchase Supply Line\',\n
                      \'Purchase Supply Cell\',)\n
  tmp_context = line.asContext(context=line, categories=category_list)\n
  predicate_list = context.portal_domains.searchPredicateList(tmp_context, portal_type=portal_type_list)\n
  for predicate in predicate_list:\n
    source_reference = predicate.getSourceReference()\n
    if source_reference:\n
     return source_reference\n
  return \'\'\n
\n
def getDestinationReference(line):\n
  category_list = line.getAcquiredCategoryList()\n
  portal_type_list = (\'Sale Supply Line\',\n
                      \'Sale Supply Cell\',)\n
  tmp_context = line.asContext(context=line, categories=category_list)\n
  predicate_list = context.portal_domains.searchPredicateList(tmp_context, portal_type=portal_type_list)\n
  for predicate in predicate_list:\n
    destination_reference = predicate.getDestinationReference()\n
    if destination_reference:\n
     return destination_reference\n
  return \'\'\n
\n
#if context.getPortalType() in context.getPortalSaleTypeList():\n
if \'Sale\' in context.getPortalType():\n
  reference_method = getDestinationReference\n
else:\n
  reference_method = getSourceReference\n
\n
def getSubLineList(obj):\n
  sub_list = []\n
  for x in obj.contentValues(portal_type=context.getPortalOrderMovementTypeList(),\n
                             sort_on=[(\'int_index\', \'ascending\'), (\'reference\', \'ascending\')]):\n
    if x.getPortalType() in obj.getPortalTaxMovementTypeList():\n
      continue\n
    sub_list.append(x)\n
    sub_list.extend(getSubLineList(x))\n
  return sub_list\n
\n
return context.Delivery_getODTDataDict(reference_method, getSubLineList)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Order_getODTDataDict</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
