## Script (Python) "CreateVarianteModele"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=form_id=''
##title=
##
request = context.REQUEST
gamme = context.getDefaultValue('specialise',portal_type=('Gamme',))
coloris_list = gamme.objectValues()
variantes_modele_list = context.objectValues()
variantes_id_list= []
compteur = 0

for variante_modele in variantes_modele_list :
  if variante_modele.portal_type == "Variante Modele" :
    variantes_id_list.append(variante_modele.id)

if len(coloris_list)>0 :

  for coloris in coloris_list :
    if not(coloris.id in variantes_id_list) :

      compteur = compteur + 1
      context.invokeFactory(type_name="Variante Modele",
                             id=coloris.id,
                             RESPONSE=request.RESPONSE)
      context[coloris.id].edit(description = coloris.getDescription())
      context[coloris.id].flushActivity(invoke=1)

  redirect_url = '%s/%s?%s' % ( context.absolute_url()
                              , form_id
                              , 'portal_status_message=%s+variantes+coloris+créées.'%compteur
                              )

else :

  redirect_url = '%s/%s?%s' % ( context.absolute_url()
                              , form_id
                              , 'portal_status_message=Pas+de+gamme+de+coloris+définie.'
                              )


request[ 'RESPONSE' ].redirect( redirect_url )
