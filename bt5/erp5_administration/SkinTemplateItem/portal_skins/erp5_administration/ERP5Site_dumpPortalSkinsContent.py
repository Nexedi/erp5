import hashlib
portal = context.getPortalObject()


def getSkinHash(skin, skin_container):
  content = ''
  if skin.meta_type in ('Script (Python)', 'Z SQL Method', ):
    content = skin.document_src()
  elif skin.meta_type in ('File', ):
    content = str(skin.data)
  elif skin.meta_type in ('ERP5 Form', ):
    try:
      content = skin.formXML()
      if isinstance(content, unicode):
        content = content.encode('utf8', 'repr')
    except AttributeError as e:
      # This can happen with dead proxy fields.
      content = "broken form %s" % e
    content = 'ignore'
  m = hashlib.md5()
  m.update(content)
  content_hash = m.hexdigest()
  return ";".join((skin_container.getId(), skin.getId(), skin.meta_type, content_hash))


for skin_folder in portal.portal_skins.objectValues('Folder'):
  if ignore_custom and skin_folder.getId() == 'custom':
    continue
  for skin in skin_folder.objectValues():
    print getSkinHash(skin, skin_folder)

if include_workflow_scripts:
  for workflow in portal.portal_workflow.objectValues():
    for skin in workflow.scripts.objectValues():
      print getSkinHash(skin, workflow)

container.REQUEST.RESPONSE.setHeader('content-type', 'text/plain')
return '\n'.join(sorted(printed.splitlines()))
