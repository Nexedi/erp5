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
            <value> <string>if initial_remaining_annuities is None or current_annuity is None:\n
  context.log(\'Error in degressive ratioCalculation :\',\n
            \'initial_remaining_annuities (%s) or current_annuity (%s) is None\' % (initial_remaining_annuities, current_annuity))\n
  return None\n
degressive_coef = kw.get(\'initial_degressive_coefficient\', None)\n
if not degressive_coef:\n
  context.log(\'Error in degressive ratioCalculation :\',\n
            \'initial_degressive_coefficient (%s) is None or 0\' % degressive_coef)\n
  return None\n
  \n
\n
# Calculate the ratio for each annuity\n
annuity_ratio_list = []\n
first_linear_ratio = 1./initial_remaining_annuities\n
degressive_ratio = first_linear_ratio * degressive_coef\n
\n
for i in range(int(initial_remaining_annuities)):\n
  linear_ratio = 1. / (initial_remaining_annuities - i)\n
  applied_ratio = max(linear_ratio, degressive_ratio)\n
  annuity_ratio_list.append(applied_ratio)\n
\n
try:\n
  return annuity_ratio_list[current_annuity]\n
except IndexError:\n
  context.log(\'Error in degressive ratioCalculation :\',\n
              \'current_annuity (%s) exceeds initial_remaining_annuities (%s)\' % (current_annuity, initial_remaining_annuities))\n
  return None\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>initial_remaining_annuities=None, start_remaining_annuities=None, stop_remaining_annuities=None, current_annuity=None, start_remaining_durability=None, stop_remaining_durability=None, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ratioCalculation</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
