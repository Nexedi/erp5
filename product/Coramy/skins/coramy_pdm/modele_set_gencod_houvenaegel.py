## Script (Python) "modele_set_gencod_houvenaegel"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=form_id=''
##title=
##
request = context.REQUEST
modele = context

modele.setEan13Modele(modele.portal_categories.group.Coramy.Houvenaegel)

redirect_url = '%s/%s?%s' % ( context.absolute_url()
                              , form_id
                              , 'portal_status_message=Gencod+mis+a+jour.'
                              )

request[ 'RESPONSE' ].redirect( redirect_url )
