## Script (Python) "modeles_print_list"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=form_id,dialog_id,modeles
##title=
##
request=context.REQUEST
modele_module = context.getObject()
error_modeles = []

for modele_item in modeles :
  modele_list = modele_module.modele_sql_search_id(modele_id = modele_item)

  if len(modele_list) > 0 :
    modele = modele_list[0].getObject()

    if modele <> None :
      print str(modele.getId())+'\t'+str(modele.portal_workflow.getInfoFor(modele, 'modele_state'))+'\t'+str(modele.getModeleOrigine())

    else :
      error_modeles.append(modele_item)

  else :
    modele = None
    error_modeles.append(modele_item)


return printed + str(error_modeles)
