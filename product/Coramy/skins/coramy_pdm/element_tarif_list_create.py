## Script (Python) "element_tarif_list_create"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=form_id=''
##title=
##
request = context.REQUEST
elements_tarif_list = context.objectValues()
elements_list= []

for element in elements_tarif_list :
  if element.portal_type == "Element Tarif" :
    elements_list.append(element)

new_id = "t"+str(len(elements_list))
context.invokeFactory(type_name="Element Tarif",
                      id=new_id,
                      RESPONSE=request.RESPONSE)
context[new_id].flushActivity(invoke=1)

redirect_url = '%s/%s?%s' % ( context.absolute_url()
                              , form_id
                              , 'portal_status_message=1+éléments+de+tarif+créés.'
                              )

request[ 'RESPONSE' ].redirect( redirect_url )
