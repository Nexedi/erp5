## Script (Python) "modele_update_price"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=form_id, selection_index, selection_name, batch_mode=0
##title=
##
message = ""
request = context.REQUEST

for o in context.searchFolder(portal_type='Element Tarif'):
  o = o.getObject()
  error = o.element_tarif_compute_price(form_id=form_id, selection_index=selection_index, selection_name=selection_name, batch_mode=1)
  if error is not None:
    message += error

if batch_mode:
  return message
else:
  if message is None:
      message = "Prix mis à jour"
  redirect_url = '%s/%s?selection_index=%s&selection_name=%s&%s' % ( context.absolute_url()
                                , form_id
                                , selection_index
                                , selection_name
                                , 'portal_status_message=%s' % message
                                )
  request[ 'RESPONSE' ].redirect( redirect_url )
