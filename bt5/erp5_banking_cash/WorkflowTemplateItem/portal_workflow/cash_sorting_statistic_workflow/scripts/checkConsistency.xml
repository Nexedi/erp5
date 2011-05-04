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
            <value> <string>from Products.DCWorkflow.DCWorkflow import ValidationFailed\n
from Products.ERP5Type.Message import Message\n
\n
delivery = state_change[\'object\']\n
\n
cell_list = delivery.getMovementList()\n
\n
# We must check that we have a quantity of 100\n
# for each kind of banknote\n
resource_dict = {}\n
for cell in cell_list:\n
  resource = cell.getResource()\n
  resource_dict[resource] = resource_dict.get(resource, 0.0) + cell.getQuantity()\n
\n
for resource, total_quantity in resource_dict.items():\n
  if round(total_quantity,3) != 1.0:\n
    portal = delivery.getPortalObject()\n
    resource_value = portal.restrictedTraverse(resource)\n
    message = Message(domain=\'ui\', message="Sorry, you must have a quantity of 1 for : $resource_title",\n
                      mapping={\'resource_title\': resource_value.getTranslatedTitle()})\n
    raise ValidationFailed, message\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>state_change, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>checkConsistency</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
