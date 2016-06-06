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
            <value> <string>if not len(path_list):\n
  return\n
restrictedTraverse = context.getPortalObject().restrictedTraverse\n
if subscription_path:\n
  subscription = restrictedTraverse(subscription_path)\n
  getId = subscription.getGidFromObject\n
  getData = subscription.getDataFromDocument\n
else:\n
  getId = getData = None\n
\n
method = context.z_catalog_syncml_document_list\n
\n
def generateParameterList():\n
  parameter_append_list = []\n
  append = parameter_append_list.append\n
  parameter_dict = {}\n
  for property in method.arguments_src.split():\n
    parameter_dict[property] = parameter_value_list = []\n
    if property == \'getData\':\n
      getter = getData\n
    elif property == \'getId\':\n
      getter = getId\n
    else:\n
      getter = None\n
    if getter is None:\n
      getter = lambda obj, property=property: getattr(obj, property)()\n
    append((parameter_value_list, getter))\n
  return parameter_dict, parameter_append_list\n
  \n
MAX_PER_QUERY = 1000\n
\n
for path in path_list:\n
  obj = restrictedTraverse(path)\n
  if obj.getPortalType() == "Integration Module":\n
    object_list = obj()\n
  else:\n
    object_list = [obj,]\n
  for x in xrange(0, len(object_list), MAX_PER_QUERY):\n
    parameter_dict, parameter_append_list = generateParameterList()\n
    for obj in object_list[x:x+MAX_PER_QUERY]:\n
      for value_list, getter in parameter_append_list:\n
        value_list.append(getter(obj))\n
    method(**parameter_dict)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>path_list, subscription_path=None, activate_kw=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>SQLCatalog_indexSyncMLDocumentList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
