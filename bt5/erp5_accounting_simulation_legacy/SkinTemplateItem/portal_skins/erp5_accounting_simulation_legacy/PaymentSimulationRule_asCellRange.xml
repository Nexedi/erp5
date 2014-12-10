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
            <value> <string>dimension_list = [\'contribution_share\', \'product\', \'region\', \'product_line\',\n
                  \'destination_region\', \'has_vat_number\', \'movement\']\n
\n
for pred in context.objectValues(portal_type=\'Predicate\'):\n
  if pred.getStringIndex() not in dimension_list:\n
    dimension_list.append(pred.getStringIndex())\n
\n
if list_dimensions:\n
  return dimension_list\n
\n
dimension_result_list = []\n
\n
for dimension in dimension_list:\n
  if dimension is not None:\n
    predicate_list = [x for x in context.contentValues(portal_type=\'Predicate\')\n
                       if x.getStringIndex() == dimension ]\n
    predicate_list.sort(key=lambda x: x.getProperty(\'int_index\', 1))\n
    if len(predicate_list):\n
      dimension_result_list.append(predicate_list)\n
\n
dimension_ids_list = []\n
\n
if matrixbox:\n
  for dimension_result in dimension_result_list:\n
    dimension_ids_list.append(\n
              [(x.getObject().getId(),\n
                x.getObject().getTitle()) for x in dimension_result])\n
else :\n
  for dimension_result in dimension_result_list :\n
    dimension_ids_list.append(\n
          [x.getObject().getId() for x in dimension_result])\n
\n
return dimension_ids_list\n
# vim: syntax=python\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>matrixbox=0, list_dimensions=0, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>PaymentSimulationRule_asCellRange</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
