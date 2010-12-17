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
            <value> <string>def getUniversalQuantityUnitDefinitionDict():\n
\n
  kw = dict(portal_type="Quantity Unit Conversion Definition",\n
            grand_parent_portal_type="Quantity Unit Conversion Module",\n
            validation_state="validated")\n
\n
  result = {}\n
  for definition in context.portal_catalog(**kw):\n
    definition = definition.getObject()\n
\n
    definition_group = definition.getParentValue()\n
    if definition_group.getValidationState() != "validated":\n
      continue\n
\n
    standard_quantity_unit_uid = definition_group.getQuantityUnitUid()\n
    if standard_quantity_unit_uid is None:\n
      continue\n
\n
    result[standard_quantity_unit_uid] = (None, 1.0)\n
\n
    unit_uid = definition.getQuantityUnitUid()\n
    if unit_uid is None:\n
      continue\n
\n
    definition_ratio = definition.getConversionRatio()\n
    if not definition_ratio:\n
      continue\n
\n
    result[unit_uid] = (definition.getUid(), definition_ratio)\n
\n
  return result\n
\n
def getCategoryQuantityUnitDefinitionDict():\n
  quantity_unit = context.portal_categories.quantity_unit\n
  result = {}\n
  for obj in quantity_unit.getCategoryMemberValueList(portal_type="Category"):\n
    obj = obj.getObject()\n
    quantity = obj.getProperty(\'quantity\')\n
    if quantity is not None:\n
      result[obj.getUid()] = (None, float(quantity))\n
\n
  return result\n
\n
def getQuantityUnitDefinitionDict():\n
  result = getUniversalQuantityUnitDefinitionDict()\n
  if not result:\n
    result = getCategoryQuantityUnitDefinitionDict()\n
  return result\n
\n
from Products.ERP5Type.Cache import CachingMethod\n
return CachingMethod(getQuantityUnitDefinitionDict,\n
                     "getUniversalQuantityUnitDefinitionDict",\n
                     cache_factory="erp5_content_long")()\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>QuantityUnitConversionModule_getUniversalDefinitionDict</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
