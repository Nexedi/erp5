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
            <value> <string>"""\\\n
Browse portal skins to seek for non cached files.\n
\n
This Alarm returns one ActiveResult severity 100 if the file listed in this\n
script from portal_skins are not affected to a cache manager. If all files are\n
correct, it returns one ActiveResult severity 0.\n
\n
If the `fixit` parameter is considered as true, the incorrect parsed files will\n
be affected to the chosen cache manager.\n
"""\n
\n
# Cache manager to use\n
# examples: "http_cache" "anonymous_http_cache" "user_ram_cache"\n
cache_manager_id = "http_cache"\n
\n
# check all files in..\n
meta_type_checklist = "Image", "File", "Filesystem Image", "Filesystem File"\n
\n
# check all files which name endswith..\n
file_extension_checklist = ".css", ".js"\n
\n
################################################################################\n
from Products.CMFActivity.ActiveResult import ActiveResult\n
\n
incorrect_file_absolute_url_list = []\n
\n
def some(iterable, function):\n
  for v in iterable:\n
    if function(v): return True\n
  return False\n
\n
# Browse files and folders recursively\n
def execute(skin):\n
  for o in skin.objectValues():\n
    # browsing files\n
    oid = o.id\n
    # force oid to be a string\n
    if callable(oid): oid = oid()\n
    if o.meta_type in meta_type_checklist or \\\n
       some(file_extension_checklist, oid.endswith):\n
      # this file matches the cheklists requirements\n
      current_cache_manager_id = o.ZCacheable_getManagerId()\n
      if current_cache_manager_id is None:\n
        # the current file is not cached\n
        if fixit: o.ZCacheable_setManagerId(cache_manager_id)\n
        else: incorrect_file_absolute_url_list.append(o.absolute_url(relative=1))\n
    elif o.meta_type == \'Folder\':\n
      execute(o)\n
\n
for skin in context.portal_skins.objectValues():\n
  execute(skin)\n
  \n
if incorrect_file_absolute_url_list != []:\n
  return ActiveResult(severity=100, detail="There is no cache set for:\\n" + "\\n".join(incorrect_file_absolute_url_list))\n
  \n
return ActiveResult(severity=0, detail="OK")\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>fixit=False</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Alarm_checkSkinCacheActive</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
