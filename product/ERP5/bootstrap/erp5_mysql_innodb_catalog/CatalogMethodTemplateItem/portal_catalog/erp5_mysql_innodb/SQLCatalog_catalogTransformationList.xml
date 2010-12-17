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

# Indexing all transformation lines for all possible variations of a Resource can be very costly.\n
# Avoid doing this in a single transaction, and split the operation.\n
\n
batch_size = 100\n
current_batch = []\n
current_size = 0\n
\n
for i, transformation in enumerate(getDefaultConversionTransformationValue):\n
  if transformation is None:\n
    continue\n
  transformation_relative_url = transformation.getRelativeUrl()\n
  variation_list_list = getTransformationVariationCategoryCartesianProduct[i]\n
  size = len(transformation)*len(variation_list_list)\n
\n
  if size + current_size < batch_size:\n
    current_batch.append((transformation_relative_url, variation_list_list))\n
    current_size += size\n
  else:\n
    if current_batch:\n
      context.activate(activity=\'SQLQueue\').SQLCatalog_catalogTransformation(current_batch)\n
    current_batch = [(transformation_relative_url, variation_list_list)]\n
    current_size = size\n
\n
\n
if current_batch:\n
  context.activate(activity=\'SQLQueue\').SQLCatalog_catalogTransformation(current_batch)\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>getDefaultConversionTransformationValue, getTransformationVariationCategoryCartesianProduct</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>SQLCatalog_catalogTransformationList</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>Catalog the ways to produce all variations of a Resource</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
