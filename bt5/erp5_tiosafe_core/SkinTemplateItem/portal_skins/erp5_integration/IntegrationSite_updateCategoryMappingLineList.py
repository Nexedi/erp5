mapping_dict = {}
destination_list = []

def getMappingUid(mapping):
  uid = "_".join(mapping.getRelativeUrl().split("/")[2:])
  return uid

def getMappingChildUid(mapping):
  if len(mapping.objectValues()) == 0:
    return getMappingUid(mapping)
  else:
    for o in mapping.objectValues():
      return "%s-%s" % (getMappingUid(o), getMappingChildUid(o))

def resetListBox(listbox, uid_list):
  for line in listbox:
    if 'listbox_key' in line:
      line_id = line['listbox_key']
      if line_id in uid_list:
        line['destination_reference'] = ""
  return listbox

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
  status_message = "Impossible to update because of redundancy of %s." % repr(list({}.fromkeys(bad_destination_list).keys()))
  request.set('portal_status_message', status_message)
  return getattr(context, request.form['dialog_id'])(listbox=listbox, kw=kw)

line_list = context.getCategoryMappingChildValueList()
len_line_list = len(line_list)
reset_uid_list = []
if len_line_list!=0:
  for line in line_list:
    uid = "_".join(line.getRelativeUrl().split("/")[2:])
    if uid not in reset_uid_list:
      your_mapping = mapping_dict[uid]
      your_destination_reference = your_mapping["destination_reference"]
      your_destination_reference_text = your_mapping["destination_reference_text"]
      line_id = your_mapping['listbox_key']
      request.form["field_listbox_destination_reference_new_%s"%line_id] = your_destination_reference
      request.form["field_listbox_destination_reference_text_new_%s"%line_id] = your_destination_reference_text
      if line.getParentValue().getPortalType() in ["Integration Category Mapping", "Integration Base Category Mapping"]:
        uid = "_".join(line.getParentValue().getRelativeUrl().split("/")[2:])
        parent_mapping = mapping_dict[uid]
        parent_destination_reference = parent_mapping["destination_reference"]
        parent_destination_reference_text = parent_mapping["destination_reference_text"]
        if parent_destination_reference_text != "":
          reset_uid_list = reset_uid_list + getMappingChildUid(line.getParentValue()).split('-')
          for uid in getMappingChildUid(line.getParentValue()).split('-'):
            request.form["field_listbox_destination_reference_new_%s"%uid] = ""
            kw["field_listbox_destination_reference_new_%s"%uid] = ""
          parent_uid = "_".join(line.getParentValue().getRelativeUrl().split("/")[2:])
          request.form["field_listbox_destination_reference_new_%s" % parent_uid] = ""
          kw["field_listbox_destination_reference_new_%s" % parent_uid] = ""
        else:
          if parent_destination_reference == "":
            reset_uid_list = reset_uid_list + getMappingChildUid(line.getParentValue()).split('-')
            for uid in getMappingChildUid(line.getParentValue()).split('-'):
              request.form["field_listbox_destination_reference_new_%s"%uid] = ""
              kw["field_listbox_destination_reference_new_%s"%uid] = ""
          #elif parent_destination_reference != line.getParentValue().getDestinationReference() \
              #and line.getParentValue().getDestinationReference() not in [None, ""]:
          elif line.getParentValue().getDestinationReference() not in [None, ""]:
            line_uid = "_".join(line.getRelativeUrl().split("/")[2:])
            destination_reference = request.form["field_listbox_destination_reference_new_%s"%line_uid]
            if destination_reference != "" and not destination_reference.startswith(parent_destination_reference):
              reset_uid_list = reset_uid_list + [line_uid]
              request.form["field_listbox_destination_reference_new_%s"%line_uid] = ""
              kw["field_listbox_destination_reference_new_%s"%line_uid] = ""
              reset_uid_list = reset_uid_list + getMappingChildUid(line).split('-')
              for uid in getMappingChildUid(line).split('-'):
                request.form["field_listbox_destination_reference_new_%s"%uid] = ""
                kw["field_listbox_destination_reference_new_%s"%uid] = ""
          #elif parent_destination_reference == line.getParentValue().getDestinationReference() \
              #and line.getParentValue().getDestinationReference() not in [None, ""]:
            #line_uid = "_".join(line.getRelativeUrl().split("/")[2:])
            #destination_reference = request.form["field_listbox_destination_reference_new_%s"%line_uid]
            #if destination_reference != "" and not destination_reference.startswith(parent_destination_reference):
              #reset_uid_list = reset_uid_list + [line_uid]
              #request.form["field_listbox_destination_reference_new_%s"%line_uid] = ""
              #kw["field_listbox_destination_reference_new_%s"%line_uid] = ""
              #reset_uid_list = reset_uid_list + getMappingChildUid(line).split('-')
              #for uid in getMappingChildUid(line).split('-'):
                #request.form["field_listbox_destination_reference_new_%s"%uid] = ""
                #kw["field_listbox_destination_reference_new_%s"%uid] = ""

status_message = "Update done."

if len(status_message):
  request.set('portal_status_message', status_message)

context.Base_updateDialogForm(listbox=listbox,update=1,kw=kw)
listbox = resetListBox(listbox, reset_uid_list)
context.getPortalObject().portal_caches.clearAllCache()
return getattr(context, request.form['dialog_id'])(listbox=listbox, kw=kw)
