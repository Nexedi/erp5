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
            <value> <string>request = context.REQUEST\n
\n
display_cache = {}\n
def display(x):\n
  if x not in display_cache:\n
    display_cache[x] = "%s" % getERP5CategoryUrl(x)\n
  return display_cache[x]\n
\n
def sort(x,y):\n
  return cmp(display(x), display(y))\n
\n
def getERP5CategoryUrl(category):\n
  if category.getPortalType() == "Base Category":\n
    return category.getTitle()\n
  else:\n
    return "%s/%s" % (getERP5CategoryUrl(category.getParent()), category.getTitle())\n
\n
def isUrlInTupleList(tuple_list, url):\n
  for (k,v) in tuple_list:\n
    if v == url:\n
      return True\n
  return False\n
\n
if context.getPortalType() == "Integration Category Mapping":\n
  try:\n
    uid = "_".join(context.getParent().getRelativeUrl().split("/")[2:])\n
    category_url = request.form["field_listbox_destination_reference_new_%s" % uid]\n
  except:\n
    category_url = context.getParent().getDestinationReference()  \n
  if category_url is not None and category_url != "":    \n
    container = context.restrictedTraverse("portal_categories/%s" % category_url)\n
  try:\n
    uid = "_".join(context.getParent().getRelativeUrl().split("/")[2:])\n
    new_destination_reference = request.form["field_listbox_destination_reference_new_%s" % uid]\n
    if new_destination_reference == "":\n
      value = request.form["field_listbox_destination_reference_new_%s" % context.getId()]\n
      return [(value,value)]\n
    else:         \n
      value = request.form["field_listbox_destination_reference_new_%s" % context.getId()]\n
      container = context.restrictedTraverse("portal_categories/%s" % new_destination_reference)\n
      category_child_list = container.getCategoryChildItemList(base=1, checked_permission=\'View\', display_method=display, sort_method=sort)\n
      if isUrlInTupleList(category_child_list, value):\n
        return  category_child_list\n
      else:\n
        return [(value, value)] + category_child_list[1:]\n
  except:\n
    pass\n
  if container is None or category_url is None:\n
    return [(\'\',\'\')]\n
else:\n
  container = context.portal_categories\n
if container ==  context.portal_categories:\n
  return [(\'\', \'\')] + [(bc.getTranslatedTitle(),\n
             bc.getId()) for bc in container.contentValues(sort_on=((\'translated_title\', \'asc\'),))]\n
else:\n
  return container.getCategoryChildItemList(base=1, checked_permission=\'View\', display_method=display, sort_method=sort)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>CategoryMapping_getCategoryList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
