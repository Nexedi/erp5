## Script (Python) "transfer_vetement"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
vetement = context
vetement_relative_url = vetement.getRelativeUrl()

related_object_list = vetement.getSpecialiseRelatedValueList()

forme = vetement.aq_parent

vetement_module = context.getPortalObject().vetement

# copy and paste vetement
copy_data = forme.manage_copyObjects(ids=[vetement.getId()])
new_id_list = vetement_module.manage_pasteObjects(copy_data)
new_vetement = vetement_module[new_id_list[0]['new_id']]

# forme_id_list is used to build the specialise relation between the vetement and formes
forme_id_list = []
forme_id_list.append(forme.getId())

# update relation on each related_object and complete forme_id_list
for related_object in related_object_list :
  category_items = related_object.getCategoryList()
  filtered_items = filter(lambda cat_item:cat_item.find(vetement_relative_url) == (-1) , category_items)
#  print related_object.getId()
#  print len(category_items)
#  print len(filtered_items)
  # update categories on related_object
  filtered_items.append("specialise/vetement/"+vetement.getId())
  related_object.edit(categories = filtered_items)

  if related_object.getPortalType() == "Modele" :
    modele_forme_list = related_object.getFormeIdList()
    for forme_id in modele_forme_list :
      if forme_id in forme_id_list :
        pass
      else :
        forme_id_list.append(forme_id)

#print forme_id_list
# set forme_id_list on vetement
vetement_categories = new_vetement.getCategoryList()
for forme_id in forme_id_list :
  vetement_categories += ('specialise/forme/'+forme_id,)

# update fichier Lectra
fichierLectra = new_vetement.getLibrairie()+'/'+new_vetement.getId()

new_vetement.edit(categories = vetement_categories, librairie = fichierLectra)

# delete old vetement
forme.deleteContent(vetement.getId())

#return printed
