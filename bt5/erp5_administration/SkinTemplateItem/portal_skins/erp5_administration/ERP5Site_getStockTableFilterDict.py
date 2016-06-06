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
            <value> <string>from DateTime import DateTime\n
\n
def getSourceAndDestinationList(instance):\n
  return (instance.getSourceUid(), instance.getDestinationUid())\n
\n
def getSourcePaymentAndDestinationPaymentList(instance):\n
  return (instance.getSourcePaymentUid(), instance.getDestinationPaymentUid())\n
\n
def getSimulationState(instance):\n
  return instance.getSimulationState()\n
\n
def stripDate(date):\n
  """\n
    Strip everything from the given DateTime parameter,\n
    leaving just year, month and day.\n
  """\n
  if not same_type(date, DateTime()):\n
    return date\n
  return DateTime(date.Date())\n
\n
def getStartDateAndStopDate(instance):\n
  start_date = stripDate(instance.getStartDate())\n
  stop_date = stripDate(instance.getStopDate())\n
  return (start_date, stop_date)\n
\n
def getSourceSectionAndDestinationSectionList(instance):\n
  return (instance.getSourceSectionUid(), instance.getDestinationSectionUid())\n
\n
def getTotalPrice(instance):\n
  price = instance.getTotalPrice()\n
  if price is None:\n
    return None\n
  return (instance.getDestinationInventoriatedTotalAssetPrice(), instance.getSourceInventoriatedTotalAssetPrice())\n
\n
def getQuantity(instance):\n
  quantity = instance.getInventoriatedQuantity()\n
  if quantity is None:\n
    return None\n
  return (quantity, -quantity)\n
\n
return {\n
  \'node_uid\':         getSourceAndDestinationList(instance),\n
  \'payment_uid\':      getSourcePaymentAndDestinationPaymentList(instance),\n
  \'section_uid\':      getSourceSectionAndDestinationSectionList(instance),\n
  \'mirror_section_uid\': getSourceSectionAndDestinationSectionList(instance),\n
  \'date\':             getStartDateAndStopDate(instance),\n
  \'mirror_date\':      getStartDateAndStopDate(instance),\n
  \'total_price\':      getTotalPrice(instance),\n
  \'quantity\':         getQuantity(instance),\n
  \'mirror_node_uid\':  getSourceAndDestinationList(instance),\n
  \'simulation_state\': getSimulationState(instance),\n
}\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>instance = None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ERP5Site_getStockTableFilterDict</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
