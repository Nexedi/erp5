## Script (Python) "SalesOrder_importEdiFileList"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=file_path=None, delivery_mode=None, incoterm=None, order_type=None, segmentation_strategique=None, travel_duration=None, batch_mode=0
##title=
##
user_name = context.portal_membership.getAuthenticatedMember().getUserName()

request = context.REQUEST


context.activate(activity="SQLQueue").SalesOrder_importEdiFileListTestAndStart(delivery_mode=delivery_mode, incoterm=incoterm, order_type=order_type, segmentation_strategique=segmentation_strategique, travel_duration=travel_duration, user_name=user_name )

redirect_url = '%s?%s' % ( context.absolute_url()+'/'+'view', 'portal_status_message=Import+des+fichiers+EDI+lancé.')

if batch_mode:
  return None
else:
  request[ 'RESPONSE' ].redirect( redirect_url )
