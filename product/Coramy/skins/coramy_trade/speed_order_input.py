## Script (Python) "speed_order_input"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=form_id,dialog_id,modeles,quantity,tarif,cout_additionnel,coef_marge,coef_majoration
##title=
##
request=context.REQUEST
order = context.getObject()
error_modeles = []

for modele_item in modeles :
  modele_list = order.modele_sql_search_id(modele_id = modele_item)

  # create a new line for each modle_item
  new_id = str(order.generateNewId())
  context.portal_types.constructContent(type_name="Sample Order Line",
        container=order,
        id=new_id,
        )
  categories = []
  categories.append('tarif/'+tarif)

  if len(modele_list) == 1 :
    modele = modele_list[0].getObject()  

    if modele <> None :

      # search for default_coloris and update if found
      coloris_list = modele.contentValues(filter={'portal_type':'Variante Modele'})
      default_coloris = None
      for coloris in coloris_list :
        if coloris.getPrototype() == 1 :
          default_coloris = coloris
      if default_coloris <> None :
        categories.append('coloris/'+default_coloris.getRelativeUrl())


      order[new_id].edit(quantity=quantity, cout_additionnel=cout_additionnel,
                         coef_marge=coef_marge, coef_majoration=coef_majoration,
                         resource_relative_url=modele.getRelativeUrl(),
                         categories=categories)
      uids = [modele.getUid()]
      order[new_id].setValueUids('resource', uids, portal_type='Modele')
      
    else :
      order[new_id].edit(quantity=quantity, cout_additionnel=cout_additionnel,
                         coef_marge=coef_marge, coef_majoration=coef_majoration,
                         description = modele_item, categories=categories)
      error_modeles.append(modele_item)
  else :
    order[new_id].edit(quantity=quantity, cout_additionnel=cout_additionnel,
                         coef_marge=coef_marge, coef_majoration=coef_majoration,
                         description = modele_item, categories=categories)
    error_modeles.append(modele_item)

if len(error_modeles)>0 :
  redirect_url = '%s/%s?%s' % ( context.absolute_url(), form_id
                                  , 'portal_status_message=%s+lignes+créées.+%s+modeles+non+trouves.'
                                     %(len(modeles),len(error_modeles))
                                  )
else :
  redirect_url = '%s/%s?%s' % ( context.absolute_url(), form_id
                                  , 'portal_status_message=%s+lignes+créées.'
                                     %len(modeles)
                                  )

context.REQUEST[ 'RESPONSE' ].redirect( redirect_url )
