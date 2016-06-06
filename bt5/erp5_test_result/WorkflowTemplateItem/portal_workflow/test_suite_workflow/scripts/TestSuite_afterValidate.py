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

import string\n
from random import choice\n
\n
test_suite = state_change[\'object\']\n
portal = test_suite.getPortalObject()\n
\n
def int2letter(i):\n
  """Convert an integer to letters, to use as a grouping reference code.\n
  A, B, C ..., Z, AA, AB, ..., AZ, BA, ..., ZZ, AAA ...\n
  """\n
  if i < 26:\n
    return (chr(i + ord(\'a\')))\n
  d, m = divmod(i, 26)\n
  return int2letter(d - 1) + int2letter(m)\n
\n
new_id = portal.portal_ids.generateNewId(id_generator="uid", id_group="test_suite_reference")\n
test_suite.setReference(int2letter(new_id))\n
\n
def generateRandomString(size):\n
  tab = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"  \n
  my_string = \'\'\n
  for i in range(size):\n
    my_string = my_string + choice(tab)\n
  return my_string\n
\n
if test_suite.getPortalType() == "Scalability Test Suite":\n
  random_path = test_suite.getReference() + "_" + generateRandomString(64)\n
  test_suite.setRandomizedPath(random_path)\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>state_change, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>TestSuite_afterValidate</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
