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
export_file_list = []
result = ""

for order in object_list:

  # some verifications have to be done
  # XXX

  # export the container 
  result +=  order.SalesPackingList_exportEdi( batch_mode = 1) 
  # XXX 
  #context.portal_activities.newMessage('SQLDict', object.getAbsoluteUrl(), {}, 'Container_exportEdi')


# and this is the end ....
if batch_mode:
  return result

else:
  request.RESPONSE.setHeader('Content-Type','application/text')
  return result
