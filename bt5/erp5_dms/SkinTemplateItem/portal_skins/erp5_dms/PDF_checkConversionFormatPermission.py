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

from Products.ERP5.Document.Document import VALID_IMAGE_FORMAT_LIST\n
\n
if format in VALID_IMAGE_FORMAT_LIST:\n
  # we do not have any data so we can allow conversion to proceed and lead to a \n
  # different conversion errorrather than raise Unautorized\n
  if not context.hasData():\n
    return True\n
\n
  # Check if PDF size is not too large for conversion tool\n
  content_information = context.getContentInformation()\n
  size = content_information.get(\'Page size\')\n
  if not size:\n
    # If we can not extract the size,\n
    # We do not take any risk and disallow conversion\n
    return False\n
\n
  width = float(size.split(\' \')[0])\n
  height = float(size.split(\' \')[2])\n
  # The default resolution is 72 dots per inch,\n
  # which is equivalent to one point per pixel (Macintosh and Postscript standard)\n
\n
  # Max surface allowed to convert an image,\n
  # value is surface of A3 (11.7 inchs * 72 dpi * 16.5 inchs * 72 dpi)\n
  maximum_surface = 1000772\n
\n
  if (width * height) > maximum_surface:\n
    return False\n
\n
return True\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>format, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>PDF_checkConversionFormatPermission</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
