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

mapping_dict = {}\n
destination_list = []\n
\n
def getMappingUid(mapping):\n
  uid = "_".join(mapping.getRelativeUrl().split("/")[2:])    \n
  return uid\n
  \n
def getMappingChildUid(mapping):\n
  if len(mapping.objectValues()) == 0:\n
    return getMappingUid(mapping)\n
  else:\n
    for o in mapping.objectValues():\n
      return "%s-%s" % (getMappingUid(o), getMappingChildUid(o))\n
\n
def resetListBox(listbox, uid_list):\n
  for line in listbox:\n
    if line.has_key(\'listbox_key\'):\n
      line_id = line[\'listbox_key\']\n
      if line_id in uid_list:\n
        line[\'destination_reference\'] = ""\n
  return listbox\n
\n
for line in listbox:\n
  if line.has_key(\'listbox_key\'):\n
    line_id = line[\'listbox_key\']\n
    mapping_dict[line_id] = line\n
    if line["destination_reference_text"] != "":\n
      destination_list.append(line["destination_reference_text"])\n
    else:\n
      destination_list.append(line["destination_reference"])        \n
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
  status_message = "Impossible to update because of redundancy of %s." % repr({}.fromkeys(bad_destination_list).keys())\n
  request.set(\'portal_status_message\', status_message)\n
  return getattr(context, request.form[\'dialog_id\'])(listbox=listbox, kw=kw)\n
\n
line_list = context.getCategoryMappingChildValueList()\n
len_line_list = len(line_list)\n
reset_uid_list = []\n
if len_line_list!=0:\n
  for line in line_list:\n
    uid = "_".join(line.getRelativeUrl().split("/")[2:])\n
    if uid not in reset_uid_list:\n
      your_mapping = mapping_dict[uid]\n
      your_destination_reference = your_mapping["destination_reference"]\n
      your_destination_reference_text = your_mapping["destination_reference_text"]\n
      line_id = your_mapping[\'listbox_key\']\n
      request.form["field_listbox_destination_reference_new_%s"%line_id] = your_destination_reference\n
      request.form["field_listbox_destination_reference_text_new_%s"%line_id] = your_destination_reference_text\n
      if line.getParent().getPortalType() in ["Integration Category Mapping", "Integration Base Category Mapping"]:        \n
        uid = "_".join(line.getParent().getRelativeUrl().split("/")[2:])\n
        parent_mapping = mapping_dict[uid]\n
        parent_destination_reference = parent_mapping["destination_reference"]\n
        parent_destination_reference_text = parent_mapping["destination_reference_text"]\n
        if parent_destination_reference_text != "":\n
          reset_uid_list = reset_uid_list + getMappingChildUid(line.getParent()).split(\'-\')\n
          for uid in getMappingChildUid(line.getParent()).split(\'-\'):\n
            request.form["field_listbox_destination_reference_new_%s"%uid] = ""\n
            kw["field_listbox_destination_reference_new_%s"%uid] = ""\n
          parent_uid = "_".join(line.getParent().getRelativeUrl().split("/")[2:])              \n
          request.form["field_listbox_destination_reference_new_%s" % parent_uid] = ""\n
          kw["field_listbox_destination_reference_new_%s" % parent_uid] = ""\n
        else:\n
          if parent_destination_reference == "":\n
            reset_uid_list = reset_uid_list + getMappingChildUid(line.getParent()).split(\'-\')\n
            for uid in getMappingChildUid(line.getParent()).split(\'-\'):\n
              request.form["field_listbox_destination_reference_new_%s"%uid] = ""\n
              kw["field_listbox_destination_reference_new_%s"%uid] = ""\n
          #elif parent_destination_reference != line.getParent().getDestinationReference() \\\n
              #and line.getParent().getDestinationReference() not in [None, ""]:\n
          elif line.getParent().getDestinationReference() not in [None, ""]:\n
            line_uid = "_".join(line.getRelativeUrl().split("/")[2:])              \n
            destination_reference = request.form["field_listbox_destination_reference_new_%s"%line_uid]\n
            if destination_reference != "" and not destination_reference.startswith(parent_destination_reference):\n
              reset_uid_list = reset_uid_list + [line_uid]\n
              request.form["field_listbox_destination_reference_new_%s"%line_uid] = ""\n
              kw["field_listbox_destination_reference_new_%s"%line_uid] = ""            \n
              reset_uid_list = reset_uid_list + getMappingChildUid(line).split(\'-\')\n
              for uid in getMappingChildUid(line).split(\'-\'):\n
                request.form["field_listbox_destination_reference_new_%s"%uid] = ""\n
                kw["field_listbox_destination_reference_new_%s"%uid] = ""    \n
          #elif parent_destination_reference == line.getParent().getDestinationReference() \\\n
              #and line.getParent().getDestinationReference() not in [None, ""]:\n
            #line_uid = "_".join(line.getRelativeUrl().split("/")[2:])              \n
            #destination_reference = request.form["field_listbox_destination_reference_new_%s"%line_uid]\n
            #if destination_reference != "" and not destination_reference.startswith(parent_destination_reference):\n
              #reset_uid_list = reset_uid_list + [line_uid]\n
              #request.form["field_listbox_destination_reference_new_%s"%line_uid] = ""\n
              #kw["field_listbox_destination_reference_new_%s"%line_uid] = ""            \n
              #reset_uid_list = reset_uid_list + getMappingChildUid(line).split(\'-\')\n
              #for uid in getMappingChildUid(line).split(\'-\'):\n
                #request.form["field_listbox_destination_reference_new_%s"%uid] = ""\n
                #kw["field_listbox_destination_reference_new_%s"%uid] = ""    \n
         \n
status_message = "Update done."\n
\n
if len(status_message):\n
  request.set(\'portal_status_message\', status_message)\n
\n
context.Base_updateDialogForm(listbox=listbox,update=1,kw=kw)\n
listbox = resetListBox(listbox, reset_uid_list)\n
context.getPortalObject().portal_caches.clearAllCache()\n
return getattr(context, request.form[\'dialog_id\'])(listbox=listbox, kw=kw)\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>listbox={}, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>IntegrationSite_updateCategoryMappingLineList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
