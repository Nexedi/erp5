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
            <value> <string>from Products.ERP5Type.Cache import CachingMethod\n
\n
def display(x):\n
  try:\n
    pcg_id = x.getGap().split(\'/\')[-1]\n
  except:\n
    pcg_id = None\n
  account_title = x.getTitle()\n
  display = "%s - %s" % (pcg_id, account_title)\n
  return display\n
\n
def sort_method(x, y):\n
  return cmp(x[0], y[0])\n
\n
def getList():\n
  list = map(lambda o: (display(o), \'account_module/%s\' % o.getId()), context.account_module.objectValues())\n
  list.sort(sort_method)\n
  return list\n
\n
\n
getList = CachingMethod(getList, \'getList\')\n
return [(\'\',\'\')] + getList()\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Immobilisation_getAccounts</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
