## Script (Python) "vetement_mesures_auto_selection"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=form_id=''
##title=
##
request = context.REQUEST
vetement = context
correspondance = vetement.getDefaultValue('specialise',portal_type=['Correspondance Mesures'])

if correspondance <> None :
  mesures_list = correspondance.getMesureVetementList()
  vetement.edit(mesure_vetement = mesures_list)
  redirect_url = '%s/%s?%s' % ( context.absolute_url()
                              , form_id
                              , 'portal_status_message=Mesures+selectionnees.'
                              )

else :

  redirect_url = '%s/%s?%s' % ( context.absolute_url()
                              , form_id
                              , 'portal_status_message=Pas+de+correspondance+définie.'
                              )


request[ 'RESPONSE' ].redirect( redirect_url )
