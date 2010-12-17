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

kw.update(context.REQUEST.form)\n
\n
def getObjectFromArg(argument):\n
  """\n
    Return an object identified by argument.\n
    If argument is a string, assume it\'s the path to the object.\n
    Otherwise, assume it\'s the object itself.\n
  """\n
  if isinstance(argument, str):\n
    return context.restrictedTraverse(argument)\n
  return argument\n
\n
kw_value_list = kw.values()\n
kw_len = len(kw_value_list)\n
if kw_len == 1:\n
  object_a = context\n
  object_b = getObjectFromArg(kw_value_list[0])\n
elif kw_len == 2:\n
  kw_value_list = kw.values()\n
  object_a = getObjectFromArg(kw_value_list[0])\n
  object_b = getObjectFromArg(kw_value_list[1])\n
else:\n
  raise ValueError, \'%s is not a valid number of arguments for diff.\' % (kw_len, )\n
\n
diff_dict, missing_in_a_dict, missing_in_b_dict = diff_recursive(object_a, object_b)\n
\n
context.REQUEST.RESPONSE.setHeader(\'Content-Type\', \'text/html; charset=utf-8\')\n
print \'<html>\'\n
print \'<head><title>Diff between %s and %s</title></head>\' % (object_a.id, object_b.id)\n
print \'<body><pre>\'\n
print \'--- <a href="%s">%s</a>\' % (object_a.absolute_url(), object_a.id)\n
print \'+++ <a href="%s">%s</a>\' % (object_b.absolute_url(), object_b.id)\n
print \'</pre><h1>Modified files</h1><ul>\'\n
for id, diff in diff_dict.items():\n
  print \'<li><b>%s</b><pre>\' % (id, )\n
  for line in diff:\n
    print line\n
  print \'</pre></li>\'\n
print \'</ul>\'\n
if len(missing_in_a_dict):\n
  print \'<h1>Objects missing in first object</h1><ul>\'\n
  for id in missing_in_a_dict.keys():\n
    print \'<li>%s</li>\' % (id, )\n
  print \'</ul>\'\n
if len(missing_in_b_dict):\n
  print \'<h1>Objects missing in second object</h1><ul>\'\n
  for id in missing_in_b_dict.keys():\n
    print \'<li>%s</li>\' % (id, )\n
  print \'</ul>\'\n
print \'</body></html>\'\n
return printed\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>**kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>diff</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
