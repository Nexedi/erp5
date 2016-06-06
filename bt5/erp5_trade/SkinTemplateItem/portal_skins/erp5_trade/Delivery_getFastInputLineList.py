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
  This script creates a list of empty lines when called with\n
  read_document_lines to False. Otherwise, it displays on \n
  the fast input all documents lines already added\n
"""\n
from Products.ERP5Type.Document import newTempBase\n
request = context.REQUEST\n
portal = context.getPortalObject()\n
trade_document = context\n
result = []\n
# Retrieve lines portal type\n
line_portal_type_list = [x for x in context.getTypeInfo().getTypeAllowedContentTypeList() \\\n
                         if x in portal.getPortalMovementTypeList()]\n
line_portal_type = line_portal_type_list[0]\n
\n
if read_document_lines:\n
  line_list = context.contentValues(portal_type=line_portal_type)\n
else:\n
  line_list = []\n
\n
if line_portal_type in portal.getPortalSaleTypeList():\n
  section_uid = context.getSourceSectionUid()\n
elif line_portal_type in portal.getPortalPurchaseTypeList():\n
  section_uid = context.getDestinationSectionUid()\n
elif line_portal_type in portal.getPortalInternalTypeList() + portal.getPortalInventoryMovementTypeList():\n
  section_uid = None\n
len_line_list = len(line_list)\n
used_id = [] # list use to make sure we do not generate two line with same id/uid\n
used_id_append = used_id.append\n
result_append = result.append\n
\n
# first browse document\'s lines\n
for line in line_list:\n
  resource = line.getResourceValue()\n
\n
  line_id = int(line.getId())\n
\n
  # First check if cells are defined\n
  cell_list = line.getCellValueList()\n
  if len(cell_list):\n
    for cell in cell_list:\n
      while line_id in used_id:\n
        # do not used an id from previously generated lines\n
        line_id+=1\n
      #context.log("inventory values a = %s, c = %s, f = %s" %(resource.getAvailableInventory(\n
      #  section_uid=section_uid,\n
      #  variation_text=cell.getVariationText()),\n
      #                                                        resource.getCurrentInventory(\n
      #  section_uid=section_uid,\n
      #  variation_text=cell.getVariationText()),\n
      #                                                        resource.getInventory(\n
      #  section_uid=section_uid,\n
      #  variation_text=cell.getVariationText())))\n
\n
      obj = trade_document.newContent(portal_type=line_portal_type,\n
                                      id=line_id,\n
                                      source=cell.getRelativeUrl(), # use as a link to the already create line/cell\n
                                      uid="new_%s" % line_id,\n
                                      temp_object=1,\n
                                      is_indexable=0,\n
                                      title=resource.getTitle(),\n
                                      resource_value=resource,\n
                                      reference=resource.getReference(),\n
                                      quantity=cell.getQuantity(),\n
                                      price=cell.getPrice(),\n
                                      total_price=cell.getTotalPrice(),\n
                                      variation_category_list = cell.getVariationCategoryList(),\n
                                      available_quantity=resource.getAvailableInventory(\n
                                                                 section_uid=section_uid,\n
                                                                 variation_text=cell.getVariationText()),\n
                                      current_quantity=resource.getCurrentInventory(\n
                                                                 section_uid=section_uid,\n
                                                                 variation_text=cell.getVariationText()),\n
                                      inventory=resource.getInventory(\n
                                                                 section_uid=section_uid,\n
                                                                 variation_text=cell.getVariationText()))\n
      result_append(obj)\n
      used_id_append(line_id)\n
  else:\n
    while line_id in used_id:\n
      # do not used an id from previously generated lines\n
      line_id+=1\n
    #context.log("inventory values a = %s, c = %s, f = %s" %(resource.getAvailableInventory(\n
    #    section_uid=section_uid,\n
    #    variation_text=line.getVariationText()),\n
    #                                                          resource.getCurrentInventory(\n
    #    section_uid=section_uid,\n
    #    variation_text=line.getVariationText()),\n
    #                                                          resource.getInventory(\n
    #    section_uid=section_uid,\n
    #    variation_text=line.getVariationText())))\n
\n
    obj = trade_document.newContent(portal_type=line_portal_type,\n
                                    id=line_id,\n
                                    uid="new_%s" % line_id,\n
                                    source=line.getRelativeUrl(),\n
                                    temp_object=1,\n
                                    is_indexable=0,\n
                                    title=resource.getTitle(),\n
                                    resource_value=resource,\n
                                    reference=resource.getReference(),\n
                                    quantity=line.getQuantity(),\n
                                    price = line.getPrice(),\n
                                    total_price=line.getTotalPrice(),\n
                                    variation_category_list = line.getVariationCategoryList(),\n
                                    available_quantity=resource.getAvailableInventory(\n
                                                               section_uid=section_uid,\n
                                                               variation_text=line.getVariationText()),\n
                                    current_quantity=resource.getCurrentInventory(\n
                                                               section_uid=section_uid,\n
                                                               variation_text=line.getVariationText()),\n
                                    inventory=resource.getInventory(\n
                                                               section_uid=section_uid,\n
                                                               variation_text=line.getVariationText()))\n
\n
    result_append(obj)\n
    used_id_append(line_id)\n
\n
# then add empty lines\n
empty_line_cpt = 1 # this counter is used so that we always add a fix\n
                   # number of empty lines into the listbox, thus user\n
                   # just have to click "update" to get new empty lines\n
i = len_line_list + 1\n
if read_document_lines is False:\n
  while empty_line_cpt <= lines_num:\n
     while i in used_id:\n
       # do not used an id from previously generated lines\n
       i+=1\n
     # Retrieve values set by the update script\n
     resource_relative_url = getattr(request,"field_listbox_resource_relative_url_new_%s"%i,None)\n
     resource_title = getattr(request,"field_listbox_title_new_%s"%i,None)\n
     reference = getattr(request,"field_listbox_reference_new_%s"%i,None)\n
\n
     obj=trade_document.newContent(portal_type=line_portal_type,\n
                                   id = i,\n
                                   uid="new_%s" % i,\n
                                   temp_object=1,\n
                                   reference=None, # otherwise it is acquired on parent\n
                                   is_indexable=0,)\n
\n
     used_id_append(i)\n
     # Set values inputted by user\n
     if resource_title not in (\'\',None):\n
       empty_line_cpt -= 1\n
       obj.edit(resource_title=resource_title)\n
     if reference not in (\'\',None):\n
       empty_line_cpt -= 1\n
       obj.edit(reference=reference)\n
     # if a resource is selected, use it\n
     if resource_relative_url not in (\'\',None):\n
       empty_line_cpt -= 1\n
       resource = portal.restrictedTraverse(resource_relative_url)\n
       obj.setResourceValue(resource)\n
     empty_line_cpt += 1\n
     result_append(obj)\n
\n
return result\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>lines_num=10, read_document_lines=False, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Delivery_getFastInputLineList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
