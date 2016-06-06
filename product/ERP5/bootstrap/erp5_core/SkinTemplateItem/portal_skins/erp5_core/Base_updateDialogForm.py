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
            <value> <string>from string import zfill\n
request = context.REQUEST\n
\n
from string import zfill\n
\n
for k in kw.keys():\n
  v = kw[k]\n
  if k.endswith(\'listbox\'):\n
    listbox = {}\n
    listbox_key = "%s_key" % k\n
    if v is not None:\n
      i = 1\n
      for line in v:\n
        if line.has_key(listbox_key):\n
          key = \'%s\' % line[listbox_key]\n
        else:\n
          key = str(zfill(i,3))\n
        listbox[key] = line\n
        i+=1\n
      request.set(k,listbox)\n
  else:\n
    request.set(\'your_%s\' % k, v)\n
    request.set(\'%s\' % k, v)\n
    # for backward compatibility, we keep my_ for dialog\n
    # using old naming conventions\n
    request.set(\'my_%s\' % k, v)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>**kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_updateDialogForm</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
