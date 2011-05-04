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
            <value> <string encoding="cdata"><![CDATA[

# This script will calculate the exchange value for the current\n
# context. If to_currency is provided, then instead of using\n
# the context, it will generate a temp object.\n
\n
# Handle the case where from_currency is to_currency\n
# Assumes that 2 currencies with the same ID, they are the same currency\n
if from_currency is not None and to_currency is not None and \\\n
   [x for x in from_currency.split(\'/\') if x.strip()][-1] == [x for x in to_currency.split(\'/\') if x.strip()][-1]:\n
    return [1]\n
\n
def sort_by_date(a, b):\n
  if a.getStartDateRangeMin() > b.getStartDateRangeMin() :\n
    return -1\n
  return 1\n
\n
object = context\n
\n
from Products.ERP5Type.Cache import CachingMethod\n
\n
if to_currency is not None:\n
  # we have parameters, not a context, so we can use cache\n
  def calculateExchangeFromParameters(from_currency=None,\n
                                      to_currency=None,\n
                                      currency_exchange_type=\'sale\',\n
                                      start_date=None,**kw):\n
    if start_date is None:\n
      from DateTime import DateTime\n
      start_date = DateTime()\n
    from Products.ERP5Type.Document import newTempBase\n
    # Note: SupplyCell is the class of Currency Exchange Line portal type objects\n
    # But in reality, anything should do.\n
    from Products.ERP5Type.Document import newTempSupplyCell as newTemp\n
    temp_object = newTemp(context.getPortalObject(),\'temp_object\')\n
    temp_kw = {\'category_list\':[\'resource/%s\' % from_currency,\n
                                \'price_currency/%s\' % to_currency],\n
               \'start_date\':start_date\n
              }\n
    if currency_exchange_type is not None:\n
      temp_kw[\'category_list\'].append(\'currency_exchange_type/%s\' % currency_exchange_type)\n
    temp_object.edit(**temp_kw)\n
    object = temp_object\n
    mapped_value = context.portal_domains.generateMappedValue(object, \n
                                                      has_cell_content=0, \n
                                                      validation_state=\'validated\',\n
                                                      sort_method=sort_by_date)\n
    base_price = getattr(mapped_value, \'base_price\', None)\n
    discount = getattr(mapped_value, \'discount\', None)\n
    if base_price is None and discount is None:\n
      mapped_value = context.portal_domains.generateMappedValue(object, \n
                                                      has_cell_content=1, \n
                                                      validation_state=\'validated\',\n
                                                      sort_method=sort_by_date)\n
      base_price = getattr(mapped_value, \'base_price\', None)\n
      discount = getattr(mapped_value, \'discount\', None)\n
    result = [base_price, discount]\n
    return result\n
  # The cache duration must not be too long, 300 is the maximum\n
  calculateExchangeFromParameters = CachingMethod(calculateExchangeFromParameters, \n
                      id = \'calculateExchangeFromParameters\', cache_factory = \'erp5_ui_short\')\n
  result = calculateExchangeFromParameters(start_date=start_date,\n
                       currency_exchange_type=currency_exchange_type,\n
                       from_currency=from_currency,to_currency=to_currency)\n
else:\n
  if start_date is None:\n
    if getattr(context,\'isDelivery\',None):\n
      start_date = context.getStartDate()\n
  mapped_value = context.portal_domains.generateMappedValue(object, \n
                                                   has_cell_content=0, \n
                                                   validation_state=\'validated\',\n
                                                   sort_method=sort_by_date)\n
  base_price = getattr(mapped_value, \'base_price\', None)\n
  discount = getattr(mapped_value, \'discount\', None)\n
  if base_price is None and discount is None:\n
    mapped_value = context.portal_domains.generateMappedValue(object, \n
                                                   has_cell_content=1, \n
                                                   validation_state=\'validated\',\n
                                                   sort_method=sort_by_date)  \n
    base_price = getattr(mapped_value, \'base_price\', None)\n
    discount = getattr(mapped_value, \'discount\', None)\n
  result = [base_price, discount]\n
return result\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>from_currency=None,to_currency=None,currency_exchange_type=None,start_date=None,**kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>CurrencyExchange_getExchangeRateList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
