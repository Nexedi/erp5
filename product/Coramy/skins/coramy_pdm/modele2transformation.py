## Script (Python) "modele2transformation"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=form_id='view', form_id2='', selection_index='', selection_name='', batch_mode=0
##title=
##
request = context.REQUEST
modele = context

pricing_transformation = modele.modele_transformation()

if pricing_transformation is not None :
  if form_id2<>'':
    redirect_url = '%s/%s?form_id=%s' % (pricing_transformation.absolute_url()
                              , form_id
                              , form_id2
                              )
  else :
    redirect_url = '%s/%s' % (pricing_transformation.absolute_url()
                              , form_id
                              )

else :
  redirect_url = '%s/%s?%s' % ( context.absolute_url()
                              , form_id
                              , 'portal_status_message=Pas+de+transformation+définie.'
                              )

request[ 'RESPONSE' ].redirect( redirect_url )
