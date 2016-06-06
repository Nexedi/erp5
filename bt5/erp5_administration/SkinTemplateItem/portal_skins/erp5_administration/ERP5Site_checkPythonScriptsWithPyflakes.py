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
            <value> <string>"""Runs pyflakes on all python scripts.\n
\n
TODO / BUGS:\n
* there is an offset in the line numbers in the reports\n
* script containing only a comment cannot be parsed\n
* integrate this directly in python script ZMI\n
* wouldn\'t it be better to use this on a business template to check scripts\n
from the business template ?\n
"""\n
\n
pyflakes = context.ERP5Site_runPyflakes\n
\n
def indent(text):\n
  return \'\'.join(("  " + line) for line in text.splitlines(True))\n
\n
def make_body(script):\n
  """rewrite a python script as if it was a python function with all\n
  bound names in the signature.\n
  """\n
  bound_names = script.getBindingAssignments().getAssignedNamesInOrder()\n
  # printed is from  RestrictedPython.RestrictionMutator the rest comes from\n
  # RestrictedPython.Utilities.utility_builtins\n
  extra_builtins= [\'printed\', \'same_type\', \'string\', \'sequence\', \'random\',\n
    \'DateTime\', \'whrandom\', \'reorder\', \'sets\', \'test\', \'math\']\n
  \n
  params = script.params()\n
  \n
  signature_parts = bound_names + extra_builtins\n
  if params:\n
    signature_parts += [params]\n
  signature = ", ".join(signature_parts)\n
  \n
  function_name = script.getId().replace(".", "__dot__").replace(" ", "__space__")\n
  \n
  body = "def %s(%s):\\n%s" % (function_name, signature, indent(script.body()) or "  pass")\n
  return body\n
\n
\n
for script_container in (context.portal_skins, context.portal_workflow):\n
  for script_path, script in context.ZopeFind(script_container, obj_metatypes=[\'Script (Python)\'], search_sub=1):\n
    err = pyflakes(make_body(script), \'%s/%s\' % (script_container.getId(), script_path))\n
    if err:\n
      print err,\n
\n
return printed\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ERP5Site_checkPythonScriptsWithPyflakes</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
