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
            <value> <string>"""Return item list of accounts that can be used as node for this accounting\n
transaction line.\n
The id of the line is used to filter the list, unless `omit_filter` is true.\n
If `mirror` is set to a true value, the list will be filtered for the mirror\n
node.\n
"""\n
from Products.ERP5Type.Cache import CachingMethod\n
from AccessControl import getSecurityManager\n
\n
portal = context.getPortalObject()\n
\n
if omit_filter:\n
  category_dict = {\n
    \'income\': \'account_type\',\n
    \'expense\': \'account_type\',\n
    \'payable\': \'account_type\',\n
    \'receivable\': \'account_type\',\n
    \'collected_vat\': \'account_type\',\n
    \'refundable_vat\': \'account_type\',\n
    \'bank\': \'account_type/asset\',\n
    \'cash\': \'account_type/asset\', }\n
elif not mirror:\n
  category_dict = {\n
    \'income\': \'account_type/income\',\n
    \'expense\': \'account_type/expense\',\n
    \'payable\': \'account_type/liability/payable\',\n
    \'receivable\': \'account_type/asset/receivable\',\n
    \'collected_vat\': \'account_type/liability/payable/collected_vat\',\n
    \'refundable_vat\': \'account_type/asset/receivable/refundable_vat\',\n
    \'bank\': \'account_type/asset/cash\',\n
    \'cash\': \'account_type/asset/cash\', }\n
else:\n
  category_dict = {\n
    \'income\': \'account_type/expense\',\n
    \'expense\': \'account_type/income\',\n
    \'payable\': \'account_type/asset/receivable\',\n
    \'receivable\': \'account_type/liability/payable\',\n
    \'collected_vat\': \'account_type/asset/receivable/refundable_vat\',\n
    \'refundable_vat\': \'account_type/liability/payable/collected_vat\',\n
    \'bank\': \'account_type/asset/cash\',\n
    \'cash\': \'account_type/asset/cash\', }\n
\n
category = category_dict.get(context.getId())\n
\n
display_cache = {}\n
display_funct = context.Account_getFormattedTitle\n
\n
def display(x):\n
  if x not in display_cache:\n
    display_cache[x] = display_funct(x)\n
  return display_cache[x]\n
\n
def sort(x,y):\n
  return cmp(display(x), display(y))\n
\n
def getItemList(category=None, portal_path=None, mirror=0, omit_filter=0,\n
                user_name=None, simulation_state=None):\n
  """Returns a list of Account path items. """\n
  if category is not None:\n
    cat = portal.portal_categories.resolveCategory(category)\n
  else:\n
    cat = portal.portal_categories.account_type\n
  filter_dict = {}\n
\n
  # we don\'t filter in existing transactions or report / search dialogs\n
  if simulation_state not in (\'delivered\', \'stopped\',\n
                              \'cancelled\', \'no_simulation_state\'):\n
    filter_dict[\'validation_state\'] = (\'draft\', \'validated\')\n
  \n
  item_list = cat.getCategoryMemberItemList(\n
                              portal_type=\'Account\',\n
                              base=0,\n
                              display_method=display,\n
                              sort_method=sort,\n
                              filter=filter_dict)\n
  return item_list\n
\n
# wrap the previous method in a cache\n
getItemList = CachingMethod(getItemList,\n
                            id=\'AccountingTransactionLine_getNodeItemList\',\n
                            cache_factory=\'erp5_content_long\')\n
\n
# the cache vary with the simulation state of the current transaction,\n
# to display all accounts when the transaction is already delivered.\n
simulation_state = \'no_simulation_state\'\n
if hasattr(context, \'getSimulationState\'):\n
  simulation_state = context.getSimulationState()\n
item_list = getItemList( category=category,\n
                    portal_path=context.getPortalObject().getPhysicalPath(),\n
                    mirror=mirror,\n
                    omit_filter=omit_filter, # XXX possible optim: only one cache if omit_filter\n
                    user_name=str(getSecurityManager().getUser()),\n
                    simulation_state=simulation_state)\n
\n
# make sure that the current value is included in this list, this is \n
# mostly for compatibility with old versions. XXX This is slow. \n
if omit_filter:\n
  return item_list\n
\n
if not hasattr(context, \'getSource\'):\n
  return item_list\n
\n
for node in (context.getSource(portal_type=\'Account\'),\n
             context.getDestination(portal_type=\'Account\')):\n
  if node:\n
    if node not in [x[1] for x in item_list]:\n
      return context.AccountingTransactionLine_getNodeItemList(mirror=mirror, omit_filter=1)\n
\n
return item_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>mirror=0, omit_filter=0</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>AccountingTransactionLine_getNodeItemList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
