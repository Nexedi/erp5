## Script (Python) "modeles_apply"
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
      modele_categories = modele.getCategories()
      new_categories = ()

      for categorie_item in modele_categories :
        if categorie_item[0:15] == 'modele_origine/':
          new_categories += ('modele_origine/Reconduction/Cognis',)
        else :
          new_categories += (categorie_item,)

      modele.edit(categories = new_categories)

    else :
      error_modeles.append(modele_item)

  else :
    modele = None
    error_modeles.append(modele_item)


if len(error_modeles)>0 :
  redirect_url = '%s/%s?%s' % ( context.absolute_url(), form_id
                                  , 'portal_status_message=%s+modeles+mis+a+jour.+%s+modeles+non+trouves:%s.'
                                     %(len(modeles),len(error_modeles), str(error_modeles))
                                  )
else :
  redirect_url = '%s/%s?%s' % ( context.absolute_url(), form_id
                                  , 'portal_status_message=%s+modeles+mis+a+jour.'
                                     %len(modeles)
                                  )
context.REQUEST[ 'RESPONSE' ].redirect( redirect_url )
