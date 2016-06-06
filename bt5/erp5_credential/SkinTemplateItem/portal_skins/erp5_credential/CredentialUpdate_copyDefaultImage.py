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
            <value> <string>"""Copy the credential update image to the related entity\n
Proxy\n
Manager -- allow to update all image property"""\n
\n
if REQUEST is not None:\n
  raise ValueError, "This script can not be call from url"\n
\n
def getAccessor(property):\n
  return "".join([x.capitalize() for x in property.split(\'_\')])\n
\n
def copyValue(source_document, source_accessor,\n
              destination_document, destination_accessor):\n
    getter = getattr(source_document, \'get%s\' % source_accessor)\n
    value = getter() \n
    setter = getattr(destination_document, \'set%s\' % destination_accessor)\n
    setter(value)\n
\n
def copyDocument(source_document, destination_document, mapping):\n
    for source_property, destination_property in mapping:\n
        source_accessor, destination_accessor = getAccessor(source_property), getAccessor(destination_property)\n
        copyValue(source_document, source_accessor,\n
                  destination_document, destination_accessor)\n
\n
new_default_image = context.getDefaultImageValue()\n
if new_default_image is not None:\n
  updated_item = context.getDestinationDecisionValue()\n
  default_image = updated_item.getDefaultImageValue()\n
  if default_image is None:\n
    default_image = updated_item.newContent(portal_type="Embedded File",id="default_image")\n
  \n
  image_mapping = (\n
    # (credential image, item image)\n
    (\'source_reference\', \'source_reference\'),\n
    (\'content_type\', \'content_type\'),\n
    (\'content_md5\', \'content_md5\'),\n
    (\'data\', \'data\'),\n
    (\'base_data\', \'base_data\'),\n
    (\'base_content_type\', \'base_content_type\'),\n
    )\n
\n
\n
  copyDocument(new_default_image,default_image, image_mapping)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>REQUEST=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>CredentialUpdate_copyDefaultImage</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
