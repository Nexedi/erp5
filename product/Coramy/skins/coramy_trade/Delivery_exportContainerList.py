## Script (Python) "Delivery_exportContainerList"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
delivery = context
request = context.REQUEST
tab = '\t'
cr = '\r'
export = ''
container_list = delivery.contentValues(filter={'portal_type':'Container'})
order = delivery.getCausalityValue(portal_type=['Sales Order'])

for container_item in container_list :
  ligne_container = ''
  container=container_item.getObject()
  container_line_list = container.contentValues(filter={'portal_type':'Container Line'})
  first_line = container_line_list[0]

  ligne_container += order.getId()+tab
  ligne_container += order.getDestinationReference()+tab
  ligne_container += order.getGroup()+tab
  ligne_container += delivery.getId()+tab
  ligne_container += str(container.getIntIndex())+tab
  ligne_container += str(len(container_list))+tab
  ligne_container += "%06d" % container.getTargetTotalQuantity()+tab
  ligne_container += str(container.getGrossWeight())+tab
  ligne_container += first_line.getResourceValue().getId()+tab
  ligne_container += delivery.getDestinationSectionTitle()+tab
  if first_line.getColorisValue() is not None :
    ligne_container += first_line.getColorisValue().getId()+tab
  else :
    ligne_container += ''+tab
  ligne_container += first_line.Amount_getTailleClient()+tab
  ligne_container += "Maillot de bain"+tab
  ligne_container += first_line.Amount_getCodeArticleClient()+tab
  ligne_container += first_line.getResourceValue().getDestinationReference()+tab
  ligne_container += ''+tab # prix conso
  ligne_container += ''+tab # devise
  ligne_container += ''+tab # gencod

  ligne_container += cr
  export += ligne_container

request.RESPONSE.setHeader('Content-Type','application/text')

return export
