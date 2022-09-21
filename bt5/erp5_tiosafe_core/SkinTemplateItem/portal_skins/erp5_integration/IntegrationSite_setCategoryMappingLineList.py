from Products.ERP5Type.Message import translateString

def getCategoryUrl(category_mapping=None):
  if getattr(category_mapping.getParentValue(), "getDestinationReference", None) is None:
    return "portal_categories"
  return  "%s/%s" % (getCategoryUrl(category_mapping.getParentValue()), category_mapping.getDestinationReference())

def createCategory(object_mapping=None, category=""):
  if object_mapping is None or category=="":
    return 
  category_url = getCategoryUrl(object_mapping.getParentValue())
  category_object = context.restrictedTraverse(category_url)
  if category_object is not None:
    if category_object.getId() == "portal_categories":
      portal_type = 'Base Category'
    else:
      portal_type = 'Category'

    sub_object_list = category_object.searchFolder(portal_type=portal_type, id=category)
    if len(sub_object_list) == 0:
      return category_object.newContent(portal_type=portal_type,
                                 id=category.replace(" ","_").lower(),
                                 title=category)
    
mapping_dict = {}
destination_list = []
for line in listbox:
  if 'listbox_key' in line:
    line_id = line['listbox_key']
    mapping_dict[line_id] = line
    if line["destination_reference_text"] != "":
      destination_list.append(line["destination_reference_text"])
    else:
      destination_list.append(line["destination_reference"])

#verify duplication category for destinations
# 1 source <----> 1 destination
bad_destination_list = []
for destination in destination_list:
  if destination != "" and destination_list.count(destination) > 1:
    bad_destination_list.append(destination)

request= context.REQUEST
integration_site = context   

if len(bad_destination_list) > 0:
  status_message = "Impossible to create mapping because of %s redundancie(s), use update button before defining mapping" % len({}.fromkeys(bad_destination_list).keys())
  request.set('portal_status_message', status_message)
  return context.Base_redirect("IntegrationSite_viewCategoryMappingFastInputDialog",
          keep_items=dict(portal_status_message=translateString(status_message),),)


line_list = context.getCategoryMappingChildValueList()
len_line_list = len(line_list)
if len_line_list!=0:
  for line in line_list:
    uid = "_".join(line.getRelativeUrl().split("/")[2:])
    your_mapping = mapping_dict[uid]
    your_destination_reference = your_mapping["destination_reference"]
    your_destination_reference_text = your_mapping["destination_reference_text"]
    if your_destination_reference_text != '':
      destination_category = createCategory(line, your_destination_reference_text)  
      if destination_category is not None:
        line.edit(destination_reference=destination_category.getRelativeUrl())
    elif your_destination_reference != '':
      line.edit(destination_reference=your_destination_reference)
    else:
      line.edit(destination_reference=your_destination_reference)
      #raise "Mapping Error", "missing mapping for %s" % line.getTitle()

form_id = "view"     

message = "Category Mapping defined"

return context.Base_redirect(form_id,
          keep_items=dict(portal_status_message=message))
