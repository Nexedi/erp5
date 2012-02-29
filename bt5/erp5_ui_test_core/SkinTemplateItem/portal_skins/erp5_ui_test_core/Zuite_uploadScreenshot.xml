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
  Upload a screenshot taken by the test to ERP5\n
"""\n
from Products.ERP5Type.Log import log\n
\n
data_uri = context.REQUEST.form.get(\'data_uri\', \'default\')\n
\n
image_module = getattr(context, "image_module", None)\n
if image_module is None:\n
  return "erp5_dms is not Installed"\n
\n
image = image_module.getPortalObject().WebSection_getDocumentValue(\n
                                                   name=image_reference)\n
\n
if image is None or image.getPortalType() != "Image":\n
  # Image is an embedded file or not an image\n
  return "Image: " + str(image_reference) + " not found"\n
\n
image.setContentType(\'image/png\')\n
data_text = data_uri.read()\n
data = data_text.decode(\'base64\')\n
\n
image.edit(data=data,\n
           filename=str(image_reference) + \'.png\', \n
           content_type = \'image/png\')\n
\n
context.Zuite_updateImage(image)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>data_uri, image_reference</string> </value>
        </item>
        <item>
            <key> <string>_proxy_roles</string> </key>
            <value>
              <tuple>
                <string>Manager</string>
              </tuple>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Zuite_uploadScreenshot</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
