import os

# We first should look to the import folder
import_path = '/var/lib/zope/import'
allowed_portal = ('portal_catalog','portal_categories','portal_types')


def PortalRoot_importAll(self, REQUEST=None):
  """
  this allows to import many zexp files by the same time
  """
  context=self
  file_list = os.listdir(import_path)
  folder_list = []
  portal_list = []


  # First we should retrieve the list of path
  for file_name in file_list:
    if file_name.find('___')>0 and file_name.find('.zexp')>0:
      base_id = file_name[:file_name.find('___')]
      if base_id not in folder_list and base_id not in portal_list:
        folder_list.append(base_id)
    elif file_name.find('.zexp')>0:
      short_name = file_name[:-len('.zexp')] 
      if short_name in allowed_portal:
        portal_list.append(short_name)


  # We should at the beginning delete portals
  for portal_id in portal_list:
    context._delObject(portal_id)
  get_transaction().commit()
  for portal_id in portal_list:
    context.manage_importObject("%s.zexp" % portal_id,set_owner=0)
    get_transaction().commit()


  # Then import all objects...
  for folder_id in folder_list:
    folder = self._getOb(folder_id)
    for file_name in file_list:
      if file_name.find('.zexp')>0 and file_name.find(folder_id)==0:
        try:
          folder.manage_importObject(file_name,set_owner=0)
        except:
          pass
        get_transaction().commit()


