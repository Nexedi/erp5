import hashlib
portal = context.getPortalObject()

if ignore_folder_list is None:
  ignore_folder_list = []

if ignore_skin_list is None:
  ignore_skin_list = []

if ignore_custom:
  ignore_folder_list.append("custom")

def getSkinHash(skin, skin_container):
  content = ''
  if skin.meta_type in ('Script (Python)', 'Z SQL Method', ):
    content = skin.document_src()
  elif skin.meta_type in ('File', ):
    content = str(skin.data)
  elif skin.meta_type in ('ERP5 Form', ):
    try:
      content = skin.formXML()
      if not isinstance(content, bytes):
        content = content.encode('utf8', 'repr')
    except AttributeError as e:
      # This can happen with dead proxy fields.
      content = "broken form %s" % e
    content = b'ignore'
  m = hashlib.md5()
  m.update(content)
  content_hash = m.hexdigest()
  return ";".join((skin_container.getId(), skin.getId(), skin.meta_type, content_hash))


for skin_folder in portal.portal_skins.objectValues('Folder'):
  if skin_folder.getId() in ignore_folder_list:
    continue
  for skin in skin_folder.objectValues():
    if skin.getId() in ignore_skin_list:
      continue
    print(getSkinHash(skin, skin_folder))

if include_workflow_scripts:
  for workflow in portal.portal_workflow.objectValues():
    for skin in workflow.scripts.objectValues():
      print(getSkinHash(skin, workflow))

container.REQUEST.RESPONSE.setHeader('content-type', 'text/plain')
return '\n'.join(sorted(printed.splitlines()))
