portal = context.getPortalObject()

# Get Software Product Object
software_product = portal.restrictedTraverse(software_product_rurl)
# Should make a script for that
if software_product.getId() != software_product.getReference().lower():
  software_product.setId(software_product.getReference().lower())

base_id = "%s-" % (software_product.getId())

data = context.getData()
data_list = data.split('\n')
reference_list = []
started = False
ignore_string_len = len(ignore_string)
for ref in data_list:
  if not started:
    if ref == "CACHE:":
      started = True
    continue
  else:
    if ref == "NETWORK:":
      started = False
      continue
    if ref.startswith(ignore_string):
      reference_list.append(ref[ignore_string_len:])
      continue
    reference_list.append(ref)

# Manifest should also be cloned
reference_list.append(context.getReference())

document_list = portal.portal_catalog(
  validation_state=("published", "published_alive"),
  reference=reference_list,
  )

path_list = [software_product_rurl]

print "    Processing File List \r===============================\r"
for document_brain in document_list:
  document = document_brain.getObject()
  if document.getFollowUp():
    continue
  print document.getId()
  new_document = document.Base_createCloneDocument(batch_mode=True)
  new_id = base_id + new_document.getReference().replace('.', '_')
  if new_id in new_document.getParentValue():
    print "  deleting %s" % new_id
    new_document.getParentValue().manage_delObjects([new_id])
  new_document.setId(new_id)
  path_list.append(new_document.getRelativeUrl())
  # version should not be set by this script but by alarm 
  # new_document.setVersion(base_id + "dev")
  new_document.setFollowUp(software_product_rurl)

print "\r\r    Here is your path list\r===============================\r\r"
print '\r'.join(path_list)
print "\r\r===============================\r\r"
print "    Done"
return printed
