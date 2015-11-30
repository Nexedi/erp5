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
            <value> <string>def getResourceInternalPriceSortKeyMethod(high_priority_supply_line_list):\n
  def resourceInternalPriceSortKeyMethod(a):\n
    high_priority_supply_line_list_len = len(high_priority_supply_line_list)\n
    if a in high_priority_supply_line_list:\n
      return high_priority_supply_line_list.index(a)\n
    elif "Internal" in a.getPortalType():\n
      if a.getDestinationSection():\n
        return high_priority_supply_line_list_len\n
      else:\n
        return high_priority_supply_line_list_len + 1\n
    else:\n
      if a.getSourceSection():\n
        return high_priority_supply_line_list_len + 2\n
      else:\n
        return high_priority_supply_line_list_len + 3\n
  return resourceInternalPriceSortKeyMethod\n
\n
\n
def getResourcePurchasePriceSortKeyMethod(high_priority_supply_line_list):\n
  def resourcePurchasePriceSortKeyMethod(a):\n
    high_priority_supply_line_list_len = len(high_priority_supply_line_list)\n
    if a in high_priority_supply_line_list:\n
      return high_priority_supply_line_list.index(a)\n
    elif "Purchase" in a.getPortalType():\n
      if a.getSourceSection():\n
        return high_priority_supply_line_list_len\n
      else:\n
        return high_priority_supply_line_list_len + 1\n
    else:\n
      if a.getDestinationSection():\n
        return high_priority_supply_line_list_len + 2\n
      else:\n
        return high_priority_supply_line_list_len + 3\n
  return resourcePurchasePriceSortKeyMethod\n
\n
\n
def getResourceSalePriceSortKeyMethod(high_priority_supply_line_list):\n
  def resourceSalePriceSortKeyMethod(a):\n
    high_priority_supply_line_list_len = len(high_priority_supply_line_list)\n
    if a in high_priority_supply_line_list:\n
      return high_priority_supply_line_list.index(a)\n
    elif "Sale" in a.getPortalType():\n
      if a.getDestinationSection():\n
        return high_priority_supply_line_list_len\n
      else:\n
        return high_priority_supply_line_list_len + 1\n
    else:\n
      if a.getSourceSection():\n
        return high_priority_supply_line_list_len + 2\n
      else:\n
        return high_priority_supply_line_list_len + 3\n
  return resourceSalePriceSortKeyMethod\n
\n
\n
def getOptimisedPriceCalculationOperandDict(default=None, context=None, **kw):\n
  """\n
   Price Method optimised by the preference \n
  """\n
  movement_portal_type = context.portal_type\n
  preferences = context.portal_preferences\n
  supply_portal_type_list = []\n
  if movement_portal_type in context.getPortalSaleTypeList():\n
    supply_portal_type_list = preferences.getPreferredSaleMovementSupplyPathTypeList()\n
  elif movement_portal_type in context.getPortalPurchaseTypeList():\n
    supply_portal_type_list = preferences.getPreferredPurchaseMovementSupplyPathTypeList()\n
  elif movement_portal_type in context.getPortalInternalTypeList():\n
    supply_portal_type_list = preferences.getPreferredInternalMovementSupplyPathTypeList()\n
  if supply_portal_type_list:\n
    supply_kw = dict(portal_type=supply_portal_type_list)\n
    for key in preferences.getPreferredPricingSupplyPathKeyCategoryList():\n
      key_uid = \'%s_uid\' % key\n
      supply_kw[\'default_%s\' % key_uid] = context.getProperty(key_uid)\n
    supply_uid_list = [str(brain.uid) for brain in context.portal_catalog(**supply_kw)]\n
    if len(supply_uid_list):\n
      kw[\'query\'] = \' catalog.uid IN (%s)\' % \',\'.join(supply_uid_list)\n
    else:\n
      return default\n
  return resource.getPriceCalculationOperandDict(default=default, context=context, **kw)\n
\n
def isPricingOptimise():\n
  """Check whether pricing optimisation is enabled or not """\n
  try:\n
    return context.portal_preferences.getPreferredPricingOptimise()\n
  except AttributeError:\n
    # When the preference is not support the property, for instance, old sites\n
    return False\n
\n
try:\n
  explanation = context.getExplanationValue()\n
except AttributeError:\n
  # Sometime, movements doesn\'t have an explanation.\n
  explanation = None\n
\n
specialise_set = set()\n
\n
if explanation is not None:\n
  explanation_type = explanation.getPortalType()\n
  high_priority_supply_line_list = []\n
  if explanation_type in context.getPortalInvoiceTypeList() +\\\n
                              context.getPortalOrderTypeList() + context.getPortalDeliveryTypeList():\n
    # if there are trade conditions containing supply lines related to that\n
    # order/invoice, we give high priority to those supply lines\n
    for supply_line in explanation.asComposedDocument().objectValues(portal_type=context.getPortalSupplyPathTypeList()):\n
      supply_cell_list = supply_line.objectValues(\n
        portal_type=context.getPortalSupplyPathTypeList())\n
      if supply_cell_list:\n
        high_priority_supply_line_list.extend(list(supply_cell_list))\n
      else:\n
        high_priority_supply_line_list.append(supply_line)\n
      specialise_set.add(supply_line.getParentValue().getRelativeUrl())\n
\n
  # XXX FIXME: Hardcoded values\n
  if "Internal" in explanation_type:\n
    kw[\'sort_key_method\'] = getResourceInternalPriceSortKeyMethod(\n
                                  high_priority_supply_line_list)\n
  elif "Purchase" in explanation_type:\n
    kw[\'sort_key_method\'] = getResourcePurchasePriceSortKeyMethod(\n
                                  high_priority_supply_line_list)\n
  elif "Sale" in explanation_type:\n
    kw[\'sort_key_method\'] = getResourceSalePriceSortKeyMethod(\n
                                  high_priority_supply_line_list)\n
\n
resource = context.getResourceValue()\n
\n
if specialise_set:\n
  kw[\'categories\'] = kw.get(\'categories\', []) + [\'specialise/%s\' % x for x in specialise_set]\n
\n
if resource is not None:\n
  product_line = resource.getProductLine()\n
  if product_line:\n
    kw[\'categories\'] = kw.get(\'categories\', []) + [\'product_line/%s\' % product_line]\n
\n
  if isPricingOptimise():\n
    return getOptimisedPriceCalculationOperandDict(default=default, context=context, **kw)\n
  else:\n
    r = resource.getPriceCalculationOperandDict(\n
                default=default, context=context, **kw)\n
  return r\n
\n
return default\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>default=None, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Movement_getPriceCalculationOperandDict</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
