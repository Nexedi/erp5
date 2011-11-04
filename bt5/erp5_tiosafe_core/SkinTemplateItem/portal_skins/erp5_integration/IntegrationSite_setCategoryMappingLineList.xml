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

from Products.ERP5Type.Message import translateString\n
\n
def getCategoryUrl(category_mapping=None):\n
  if getattr(category_mapping.getParent(), "getDestinationReference", None) is None:\n
    return "portal_categories"\n
  return  "%s/%s" % (getCategoryUrl(category_mapping.getParent()), category_mapping.getDestinationReference())\n
\n
def createCategory(object_mapping=None, category=""):\n
  if object_mapping is None or category=="":\n
    return \n
  category_url = getCategoryUrl(object_mapping.getParent())\n
  category_object = context.restrictedTraverse(category_url)\n
  if category_object is not None:\n
    if category_object.getId() == "portal_categories":\n
      portal_type = \'Base Category\'\n
    else:\n
      portal_type = \'Category\'\n
\n
    sub_object_list = category_object.searchFolder(portal_type=portal_type, id=category)\n
    if len(sub_object_list) == 0:\n
      return category_object.newContent(portal_type=portal_type,\n
                                 id=category.replace(" ","_").lower(),\n
                                 title=category)\n
    \n
mapping_dict = {}\n
destination_list = []\n
for line in listbox:\n
  if line.has_key(\'listbox_key\'):\n
    line_id = line[\'listbox_key\']\n
    mapping_dict[line_id] = line\n
    if line["destination_reference_text"] != "":\n
      destination_list.append(line["destination_reference_text"])\n
    else:\n
      destination_list.append(line["destination_reference"])\n
\n
#verify duplication category for destinations\n
# 1 source <----> 1 destination\n
bad_destination_list = []\n
for destination in destination_list:\n
  if destination != "" and destination_list.count(destination) > 1:\n
    bad_destination_list.append(destination)\n
\n
request= context.REQUEST\n
integration_site = context   \n
\n
if len(bad_destination_list) > 0:\n
  status_message = "Impossible to create mapping because of %s redundancie(s), use update button before defining mapping" % len({}.fromkeys(bad_destination_list).keys())\n
  request.set(\'portal_status_message\', status_message)\n
  return context.Base_redirect("IntegrationSite_viewCategoryMappingFastInputDialog",\n
          keep_items=dict(portal_status_message=translateString(status_message),),)\n
\n
\n
line_list = context.getCategoryMappingChildValueList()\n
len_line_list = len(line_list)\n
if len_line_list!=0:\n
  for line in line_list:\n
    uid = "_".join(line.getRelativeUrl().split("/")[2:])\n
    your_mapping = mapping_dict[uid]\n
    your_destination_reference = your_mapping["destination_reference"]\n
    your_destination_reference_text = your_mapping["destination_reference_text"]\n
    if your_destination_reference_text != \'\':\n
      destination_category = createCategory(line, your_destination_reference_text)  \n
      if destination_category is not None:\n
        line.edit(destination_reference=destination_category.getRelativeUrl())\n
    elif your_destination_reference != \'\':\n
      line.edit(destination_reference=your_destination_reference)\n
    else:\n
      line.edit(destination_reference=your_destination_reference)\n
      #raise "Mapping Error", "missing mapping for %s" % line.getTitle()\n
\n
form_id = "view"     \n
\n
message = "Category Mapping defined"\n
\n
return context.Base_redirect(form_id,\n
          keep_items=dict(portal_status_message=message))\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>listbox={}, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>IntegrationSite_setCategoryMappingLineList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
