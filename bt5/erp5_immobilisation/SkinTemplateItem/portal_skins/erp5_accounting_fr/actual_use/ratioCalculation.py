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
            <value> <string>initial_durability = kw.get(\'initial_durability\')\n
if start_remaining_annuities is None or stop_remaining_annuities is None \\\n
     or start_remaining_durability is None or stop_remaining_durability is None \\\n
     or initial_durability is None:\n
  context.log(\'Error for actual use ratio calculation : one of theses properties is None : start_remaining_annuities : %s, stop_remaining_annuities : %s, start_remaining_durability : %s, stop_remaining_durability : %s, or initial_durability : %s\' % (\n
     repr(start_remaining_annuities), repr(stop_remaining_annuities), repr(start_remaining_durability), repr(stop_remaining_durability), repr(initial_durability)),\'\')\n
  return None\n
\n
consumpted_durability = start_remaining_durability - stop_remaining_durability\n
annuities_number = start_remaining_annuities - stop_remaining_annuities\n
\n
try:\n
  per_annuity_consumption = (consumpted_durability / (annuities_number + 0.))\n
  ratio = per_annuity_consumption / start_remaining_durability\n
  return ratio\n
  #return ratio * start_remaining_durability / initial_durability\n
except ZeroDivisionError:\n
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
