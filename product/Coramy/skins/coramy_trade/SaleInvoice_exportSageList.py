## Script (Python) "SaleInvoice_exportSageList"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=**kw
##title=
##
# generate a export file from a Sale Invoice list for the Sage software

request = context.REQUEST
cr='\r'
# add the header of the file
file = '#FLG 000'+cr
file += '#VER 5'+cr

object_list = context.object_action_list(selection_name='order_selection')

for invoice in object_list:
  try:
    file += invoice.SaleInvoice_exportSage(batch_mode=1,cr=cr)
  except:
    message='Erreur+sur+la+facture:+identifiant+%s+numero+%s.' % (invoice.getId(),invoice.getReference())
    redirect_url = '%s?%s%s' % ( context.absolute_url()+'/view', 'portal_status_message=',message)
    request[ 'RESPONSE' ].redirect( redirect_url )

# add the end of the file
file += '#FIN'

request.RESPONSE.setHeader('Content-Type','text/plain')
return file
