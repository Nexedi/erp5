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

"""Usage example:\n
\n
- in a url ``<your erp5 url>/portal_skins/Folder_resolvePath?path=**``\n
- in a script ``context.Folder_resolvePath("**")``\n
    - for a business template path list ``portal.Folder_resolvePath(bt.getTemplatePathList())``\n
\n
Arguments:\n
\n
- ``path`` can be a string or a list (if ``path_list`` is not defined).\n
- ``path_list`` must be a list (if ``path`` is not defined).\n
- ``traverse`` if True, return object list instead of path list.\n
- ``globbing`` if False, handle "*" and "**" as normal id.\n
"""\n
if path is None:\n
  if path_list is None:\n
    raise TypeError("`path` or `path_list` argument should be defined")\n
elif isinstance(path, (list, tuple)):\n
  path_list = path\n
else:\n
  path_list = [path]\n
\n
context_is_portal = context.getPortalObject() == context\n
contextTraverse = context.restrictedTraverse\n
\n
resolved_list = []\n
append = resolved_list.append\n
\n
if globbing:\n
  for path in path_list:\n
    if path == "*" or (context_is_portal and path == "**"): # acts like _resolvePath in Products.ERP5.Document.BusinessTemplate.PathTemplateItem\n
      for sub_path, sub_obj in context.ZopeFind(context, search_sub=0):\n
        if traverse:\n
          append(sub_obj)\n
        else:\n
          append(sub_path)\n
    elif path == "**":\n
      for sub_path, sub_obj in context.ZopeFind(context, search_sub=1):\n
        if traverse:\n
          append(sub_obj)\n
        else:\n
          append(sub_path)\n
    elif path.endswith("/**"):\n
      parent_path = path[:-3]\n
      obj = contextTraverse(parent_path)\n
      for sub_path, sub_obj in obj.ZopeFind(obj, search_sub=1):\n
        if traverse:\n
          append(sub_obj)\n
        else:\n
          append(parent_path + "/" + sub_path)\n
    elif path.endswith("/*"):\n
      parent_path = path[:-2]\n
      obj = contextTraverse(parent_path)\n
      for sub_path, sub_obj in obj.ZopeFind(obj, search_sub=0):\n
        if traverse:\n
          append(sub_obj)\n
        else:\n
          append(parent_path + "/" + sub_path)\n
    else:\n
      if traverse:\n
        append(contextTraverse(path))\n
      else:\n
        append(path)\n
else:\n
  for path in path_list:\n
    if traverse:\n
      append(contextTraverse(path))\n
    else:\n
      append(path)\n
return resolved_list\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>path=None, path_list=None, traverse=False, globbing=True</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Folder_resolvePath</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
