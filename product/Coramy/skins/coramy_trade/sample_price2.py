## Script (Python) "sample_price2"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=form_id=''
##title=
##
REQUEST = context.REQUEST
ligne = context
modele = ligne.getDefaultValue('resource',portal_type=['Modele'])

if modele <> None :
  modele_tarif_list = modele.contentValues(filter={'portal_type':'Element Tarif'})
  for modele_tarif in modele_tarif_list :
    modele.manage_copyObjects(modele_tarif.getId(), REQUEST, REQUEST.RESPONSE)
    if ligne.cb_dataValid:
      ligne.manage_pasteObjects(REQUEST['__cp'])
    
  redirect_url = '%s/%s?%s' % ( context.absolute_url()
                              , form_id
                              , 'portal_status_message=%s+elements+de+tarif+crees.'%len(modele_tarif_list)
                              )

else :

  redirect_url = '%s/%s?%s' % ( context.absolute_url()
                              , form_id
                              , 'portal_status_message=Pas+de+modèle+défini.'
                              )


request[ 'RESPONSE' ].redirect( redirect_url )
