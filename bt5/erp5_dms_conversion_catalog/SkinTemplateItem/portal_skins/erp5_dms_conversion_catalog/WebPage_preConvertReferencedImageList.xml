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

"""\n
  Get all images inside a document and try to pre convert relative ones\n
"""\n
portal = context.getPortalObject()\n
\n
MARKER = (None, \'\',)\n
API_ARGUMENT_LIST = [\'format\', \'display\', \'display_list\', \'quality\', \'resolution\']\n
validation_state = (\'released\', \'released_alive\', \'published\', \'published_alive\',\n
                    \'shared\', \'shared_alive\', \'public\', \'validated\')\n
\n
def convertUrlArgumentsToDict(convert_string):\n
  convert_kw = {}\n
  # some editors when creating wbe page content do escape \'&\' properly\n
  convert_string = convert_string.replace(\'&amp;\', \'&\')\n
\n
  # convert from URL string to python arguments dict\n
  for pair in convert_string.split(\'&\'):\n
    arg_list = pair.split(\'=\')\n
    if len(arg_list)==2:\n
      convert_kw[arg_list[0]] = arg_list[1]\n
  return convert_kw\n
\n
image_url_list = context.Base_extractImageUrlList()\n
for image_url in image_url_list:\n
  if not image_url.startswith(\'http://\') and not image_url.startswith(\'https://\'):\n
    # try to use only relative URLs\n
    part_list = image_url.split(\'?\')\n
    if len(part_list)==2:\n
      # don\'t deal with bad URLs (having more than one \'?\') inside\n
      reference = part_list[0]\n
      convert_string = part_list[1]\n
\n
      # check we have locally such a reference so we can convert it\n
      catalog_kw = {\'portal_type\': portal.getPortalDocumentTypeList() + portal.getPortalEmbeddedDocumentTypeList(),\n
                    \'reference\': reference,\n
                    \'validation_state\': validation_state}\n
\n
      document = portal.portal_catalog.getResultValue(**catalog_kw)\n
      if document is not None:\n
        # try to pre convert it based on extracted URL\'s arguments\n
        convert_kw = convertUrlArgumentsToDict(convert_string)\n
\n
        # XXX: we do check if "data" methods exists on pretending to be Document portal types\n
        # we need a way to do this by introspection\n
        if ((getattr(document, "getData", None) is not None and document.getData() not in MARKER) or \\\n
           (getattr(document, "getBaseData", None) is not None and document.getBaseData() not in MARKER)):\n
          if \'display\' in convert_kw.keys():\n
            # conversion script aggregate all possible display options into a list\n
            convert_kw[\'display_list\'] = [convert_kw.pop(\'display\')]\n
\n
          # only certain arguments make sense due to API so leave only them\n
          for key in convert_kw.keys():\n
            if key not in API_ARGUMENT_LIST:\n
              convert_kw.pop(key)\n
\n
          # due to API we need certain arguments\n
          if convert_kw.get(\'quality\') is None:\n
            convert_kw[\'quality\'] = kw.get(\'quality\')\n
\n
          # do real conversion\n
          format = convert_kw.get(\'format\')\n
          quality = convert_kw.get(\'quality\')\n
          if format not in MARKER and quality not in MARKER:\n
            # format is mandatory if it\'s missing then anyway URL request will fail so\n
            # don\'t bother create an activity\n
            document.activate(priority=4, tag="conversion").Base_callPreConvert(**convert_kw)\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>**kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>WebPage_preConvertReferencedImageList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
