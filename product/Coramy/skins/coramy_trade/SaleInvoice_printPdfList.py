## Script (Python) "SaleInvoice_printPdfList"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=printer='Xerox_DC_440',selection_name=None,render_id=None,template_id=None,number_copies=1,**kw
##title=
##
# generate a pdf file from the sale invoice list

request = context.REQUEST

object_list = context.object_action_list(selection_name=selection_name)
# sort invoice's references
object_list.sort(lambda x,y: cmp(int(x.getReference('0')),int(y.getReference('0'))));

user_name = context.portal_membership.getAuthenticatedMember().getUserName()

for invoice in object_list:
  invoice.activate(activity="SQLQueue").SaleInvoice_printPdf(user_name=user_name,printer=printer,selection_name=selection_name,render_id=render_id,template_id=template_id, number_copies=number_copies)

redirect_url = '%s?%s' % ( context.absolute_url(), 'portal_status_message=Impression+lancée.')
request[ 'RESPONSE' ].redirect( redirect_url )
