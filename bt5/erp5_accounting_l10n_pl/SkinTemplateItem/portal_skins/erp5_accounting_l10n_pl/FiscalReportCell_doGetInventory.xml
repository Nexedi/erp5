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
  This scripts add the balance of every gap account in the list \'accounts\'\n
  it use portal_simulation.getInventory. \n
  The following REQUEST keys are mandatory : \n
      at_date\n
\n
  those are optional : \n
      gap_base\n
      simulation_state\n
      resource\n
      section_category\n
\n
  those are ignored from the request and should explicitely passed as keywords args to this script : \n
      from_date\n
  \n
  parameters keywords to this script overrides REQUEST keys\n
\n
"""\n
\n
request = context.REQUEST\n
kw = {}\n
kw[\'omit_simulation\']   = 1\n
kw[\'omit_input\']=1\n
kw["simulation_state"]  = request.get("simulation_state", [\'stopped\', \'delivered\'])\n
#kw["section_uid"]     = context.restrictedTraverse(request.get("organisation")).getUid()\n
kw["at_date"]           = request[\'at_date\']\n
kw["from_date"]         = request[\'from_date\']\n
kw.update(params_kw)\n
\n
\n
sum = 0\n
\n
for account in accounts :\n
  kw[\'node_category\']= context.shortAccountNumberToFullGapCategory(account, **kw)\n
  #context.log(\'KW for getInventory\',kw)\n
  try : \n
    #val = (context.portal_simulation.getInventory(**kw) or 0)\n
    val = (context.portal_simulation.getInventoryAssetPrice(**kw) or 0)\n
    sum += val\n
  except KeyError : # unknown gap account (i.e. not a category)\n
    pass\n
  except AttributeError: # no account of this gap nr has been set up\n
    return 0\n
#  except :\n
#    raise \'error on\', (account, shortAccountNumberToFullGapCategory(account))\n
return float ("%.2f"%(sum))\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>accounts, **params_kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>FiscalReportCell_doGetInventory</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
