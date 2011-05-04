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
            <value> <string>from Products.ERP5Type.Message import Message\n
account = None\n
portal = context.getPortalObject()\n
catalog = portal.portal_catalog\n
portal_type = "Bank Account"\n
\n
if reference is None:\n
  message = Message(domain="ui", message="Please give a reference")\n
  raise ValueError, message\n
\n
#context.log(\'reference\',reference)\n
account_list = catalog(string_index=reference, portal_type=portal_type, validation_state=(\'valid\', \'closed\'))\n
# context.log(\'sql src\',catalog(string_index=reference, portal_type=portal_type, validation_state=(\'valid\', \'closed\'),src__=1))\n
# context.log(\'len 1\',len(account_list))\n
if len(account_list) == 0:\n
  account_list = catalog(string_index="%%%s%%" % reference, portal_type=portal_type, validation_state=(\'valid\', \'closed\'))\n
#context.log(\'len 2\',len(account_list))\n
if len(account_list) == 0:\n
  message = Message(domain="ui", message="No bank account have this reference")\n
  raise ValueError, message\n
if force_one_account and len(account_list) != 1:\n
  message = Message(domain="ui", message="More than one account match this research")\n
  raise ValueError, message\n
\n
account_list = [x.getObject() for x in account_list]\n
\n
if total_price:\n
  tmp_dict = {}\n
  new_list = []\n
  for account in account_list:\n
    quantity = account.BankAccount_getCurrentPosition()\n
    tmp_dict[\'total_price\'] = quantity\n
    new_list.append(account.asContext(**tmp_dict))\n
  account_list = new_list\n
\n
# context.log("final account list",account_list)\n
return account_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>reference=None, total_price=0, force_one_account=0</string> </value>
        </item>
        <item>
            <key> <string>_proxy_roles</string> </key>
            <value>
              <tuple>
                <string>Manager</string>
              </tuple>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>BankAccount_getReportInformationList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
