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
            <value> <string>"""\n
  Find the list of objects to synchronize by calling the catalog.\n
\n
  Possibly look up a single object based on its ID, GID\n
"""\n
\n
if gid is not None and len(gid):\n
  gid_generator_method_id = context_document.getGidGeneratorMethodId()\n
  method = getattr(context_document, gid_generator_method_id)\n
  for prod in context.getPortalObject().product_module.contentValues():\n
    prod_gid = method(prod)\n
    if prod_gid == gid:\n
      return [prod,]\n
  return []\n
elif id is not None and len(id):\n
  # work on the defined product (id is not None)\n
  product = getattr(context.product_module, id)\n
  if product.getValidationState() not in  [\'invalidated\', \'deleted\'] and \\\n
      product.getTitle() != \'Unknown\':\n
    return [product,]\n
  return []\n
else:\n
  product_list = []\n
  product_append = product_list.append\n
  while context_document.getParentValue().getPortalType() != "Synchronization Tool":\n
    context_document = context_document.getParentValue()\n
  site = [x for x in context_document.Base_getRelatedObjectList(portal_type="Integration Module")][0].getParentValue()\n
\n
  sale_supply_list = context.getPortalObject().sale_supply_module.searchFolder(title=site.getTitle(),\n
                                                                               validation_state="validated")\n
  if len(sale_supply_list) != 1:\n
    return []\n
  sale_supply = sale_supply_list[0].getObject()\n
  for line in sale_supply.contentValues(portal_type="Sale Supply Line"):\n
    resource = line.getResourceValue()\n
    if resource is not None and resource.getValidationState() == "validated":\n
      product_append(resource)\n
  return product_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>context_document=None, id="", gid=""</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ProductModule_getProductValueList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
