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
  Generic method to handle conversion failures ans still return something to use \n
  to explain what when wrong, etc.\n
"""\n
VALID_IMAGE_FORMAT_LIST = (\'jpg\', \'jpeg\', \'png\', \'gif\', \'pnm\', \'ppm\', \'tiff\')\n
\n
# some good defaults\n
mimetype = "text/plain"\n
data = "Conversion failure"\n
\n
if format in VALID_IMAGE_FORMAT_LIST:\n
  # default image is an OFSImage so even if conversion engine is down \n
  # we are still able to deliver it\n
  default_image = getattr(context, "default_conversion_failure_image", None)\n
  if default_image is not None:\n
    mimetype = default_image.getContentType()\n
    data = default_image.index_html(context.REQUEST, context.REQUEST.RESPONSE)\n
\n
return mimetype, data\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>format=None, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Document_getFailsafeConversion</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
