"""Check the object have an unique reference in it's parent folder
"""
from Products.ERP5Type.Log import log
if editor is None : 
  return 1

reference = editor

document = context.restrictedTraverse(request.object_path, None)
if document is None : 
  log('Base_uniqueReferenceInFolderValidator', 'document is None')
  return 0

parent_folder = document.getParentValue()
for same_reference in parent_folder.searchFolder(reference = reference):
  if same_reference.uid != document.getUid() :
    log('Base_uniqueReferenceInFolderValidator',
                        'another document with reference %s exists at %s' % (reference, same_reference.getPath()))
    return 0

return 1
