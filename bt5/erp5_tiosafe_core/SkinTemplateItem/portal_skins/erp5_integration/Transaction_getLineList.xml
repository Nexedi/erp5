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
            <value> <string>""" Retrieve the movement list of the transaction. """\n
movement_list = []\n
\n
sub = context.restrictedTraverse(context_document)\n
while sub.getParentValue().getPortalType() !=  "Synchronization Tool":\n
  sub = sub.getParentValue()\n
\n
im = sub.Base_getRelatedObjectList(portal_type=\'Integration Module\')[0].getObject()\n
prod_module = im.getParentValue().product_module\n
prod_pub = prod_module.getSourceSectionValue()\n
\n
# getter and corresponding property (the order is important)\n
getter_tuple_list = [\n
    (\'getTitle\', \'title\'),\n
    (\'fake_getGid\', \'resource\'),\n
    (\'getReference\', \'reference\'),\n
    (\'getQuantity\', \'quantity\'),\n
    (\'getPrice\', \'price\'),\n
]\n
\n
# browse the movement list, build the element to sort and movement\'s data\n
for movement in context.getMovementList():\n
  movement_dict = {\n
      \'title\': None,\n
      \'resource\': None,\n
      \'reference\': None,\n
      \'quantity\': None,\n
      \'price\': None,\n
      \'VAT\' : None,\n
  }\n
  property_list = []\n
\n
  # browse the main element of the movement\n
  for getter, key in getter_tuple_list:\n
    if getter == \'fake_getGid\':\n
      value = prod_pub.getGidFromObject(object=movement.getResourceValue(), encoded=False)\n
    else:\n
      # XXX-Aurel : maybe there is better way to know if it is a cell\n
      if \'Cell\' in movement.getPortalType() and \\\n
          getter in [\'getTitle\', \'getReference\']:\n
        value = getattr(movement.getParentValue(), getter)()\n
      else:\n
        value = getattr(movement, getter)()\n
        if value is not None:\n
          if getter == \'getPrice\':\n
            value = \'%.6f\' % value\n
          elif getter == \'getQuantity\':\n
            value = \'%.2f\' % value\n
    \n
    if value is not None:\n
      movement_dict[key] = value\n
      property_list.append(value)\n
\n
  # set the variations of the movement in another list, it\'s using by the sort\n
  variation_list = []\n
  if movement.getBaseContributionValue() is not None:\n
    movement_dict[\'VAT\'] = movement.getBaseContribution().split(\'/\')[-1]\n
\n
  variation_list = movement.getVariationCategoryList()\n
  variation_list.sort()\n
  movement_list.append(movement_dict)\n
  # to not interfer with the sort, set to the end the object\n
  movement_dict[\'object\'] = movement\n
  movement_dict[\'variation_list\'] = variation_list\n
\n
\n
def cmp_resource(a,b):\n
  a_str = "%s %s %s" %(a[\'resource\'], a[\'title\'], \' \'.join(a[\'variation_list\']))\n
  b_str = "%s %s %s" %(b[\'resource\'], b[\'title\'], \' \'.join(b[\'variation_list\']))\n
  return cmp(a_str, b_str)\n
\n
movement_list.sort(cmp=cmp_resource)\n
\n
return movement_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>context_document</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Transaction_getLineList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
