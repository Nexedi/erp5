## Script (Python) "SalesPackingList_exportEdiList"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=batch_mode=0,**kw
##title=
##
# generate the Edi file of the selection of sales packing list
request = context.REQUEST

object_list = context.object_action_list(selection_name='sales_packing_list_selection')
result = ""

for order in object_list:
 
  try:
    # export the container
    result +=  order.SalesPackingList_exportEdi( batch_mode = 1)
  except:
    message='Erreur+sur+la+livraison:+identifiant+%s.' % (order.getId())
    redirect_url = '%s?%s%s' % ( context.absolute_url()+'/view', 'portal_status_message=',message)
    request[ 'RESPONSE' ].redirect( redirect_url )

# and this is the end ....
if batch_mode:
  return result

else:
  request.RESPONSE.setHeader('Content-Type','application/text')
  return result
