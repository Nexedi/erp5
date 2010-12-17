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
            <value> <string># precision for editable fields\n
params = context.ERP5Accounting_getParams(selection_name)\n
if params.get(\'precision\', None) is not None:\n
  context.REQUEST.set(\'precision\', params[\'precision\'])\n
\n
use_account_reference = \\\n
 context.portal_preferences.getPreferredAccountNumberMethod() == \'account_reference\'\n
\n
if preferred_gap_id:\n
  if use_account_reference:\n
    kwd[\'reference\'] = preferred_gap_id\n
  else:\n
    kwd[\'preferred_gap_id\'] = preferred_gap_id\n
\n
\n
# XXX workaround for #458, we rewrite sort_on id to sort_on using\n
# strict_membership.\n
new_sort_on = []\n
if sort_on is not None:\n
  for sort_on_item in sort_on:\n
    if sort_on_item[0] == \'preferred_gap_id\':\n
      if use_account_reference:\n
        new_sort_on.append((\'reference\', sort_on_item[1]))\n
      else:\n
        new_sort_on.append(\n
            (\'preferred_gap_strict_membership_id\', sort_on_item[1]))\n
    else:\n
      new_sort_on.append(sort_on_item)\n
\n
return context.portal_catalog(sort_on=new_sort_on, **kwd)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>preferred_gap_id=None, sort_on=None, selection=None, selection_name=None, **kwd</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>AccountModule_getAccountList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
