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
            <value> <string>"""\n
  Returns a list of acceptable formats for conversion\n
  in the form of tuples (for listfield in ERP5Form)\n
"""\n
from Products.ERP5Type.Cache import CachingMethod\n
\n
def contentTypeMatch(content_type, glob):\n
  if \'*\' == glob[-1]:\n
    # \'image/png\' must match \'image/*\'\n
    index = glob.index(\'*\')\n
    return content_type[:index] == glob[:index]\n
  else:\n
    return content_type == glob\n
\n
portal = context.getPortalObject()\n
content_type = context.getContentType()\n
\n
def getTargetFormatItemList(content_type):\n
  # without content type no wayto determine target format\n
  if content_type is None:\n
    return []\n
  format_list = []\n
  output_content_type_list = []\n
  for obj in portal.portal_transforms.objectValues():\n
    for input in obj.inputs:\n
      if contentTypeMatch(content_type, input) and \\\n
        obj.output not in output_content_type_list and\\\n
        obj.output!=content_type:\n
        output_content_type_list.append(obj.output)\n
\n
  for output_content_type in output_content_type_list:\n
    mimetypes_registry_extension_list = portal.mimetypes_registry.lookup(output_content_type)\n
    for mimetypes_registry_extension in mimetypes_registry_extension_list:\n
      title = mimetypes_registry_extension.name()\n
      try:\n
        format = mimetypes_registry_extension.extensions[0]\n
      except IndexError:\n
        format = None\n
      if format is not None and format not in format_list:\n
        format_list.append((title, format,))\n
  return format_list\n
\n
getTargetFormatItemList = CachingMethod(getTargetFormatItemList,\n
                                        id=\'Base_getTargetFormatItemList\',\n
                                        cache_factory=\'erp5_ui_long\')\n
return getTargetFormatItemList(content_type)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_getTargetFormatItemList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
