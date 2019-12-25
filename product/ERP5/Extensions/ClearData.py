def clearData(self,REQUEST=None):
  """
  this allows to erase every data object
  """
  import transaction
  context=self
  for folder in context.objectValues(("ERP5 Folder",)):
    print "#### Deleting inside the folder %s ####" % folder.id
    # Getting the list of ids
    to_delete_list = folder.objectIds()
    while len(to_delete_list) > 0:
      for id in to_delete_list:
        folder.manage_delObjects(id)
      to_delete_list = folder.objectIds()
    transaction.commit()

  print "work done"
