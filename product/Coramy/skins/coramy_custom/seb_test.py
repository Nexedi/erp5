## Script (Python) "seb_test"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
organisation_list = context.object_action_list(selection_name='organisations_selection')

request = context.REQUEST
tab = '\t'
cr = '\n'
export = ''
del_list = []

for modele_item in organisation_list :
  ligne_modele = ''
  modele=modele_item.getObject()

  if int(modele.getId()) >= 726 :
    del_list.append(modele.getId())

context.getPortalObject().organisation.deleteContent(del_list)
return len(del_list)
