## Script (Python) "SalesPackingList_oneContainerAutoPacking"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=container_type='', delivery_mode='', gross_weight='', user_name='',batch_mode=0
##title=
##
try:
  request = context.REQUEST

  # verify the delivery_mode in the Sales Packing List
  if context.getDeliveryMode() != delivery_mode:
    raise None
  # verify the packing doesn't content any container
  container_list = context.contentValues(filter={'portal_type':'Container'})
  if len(container_list)>0:
    raise None



  delivery_line_list = context.contentValues(filter={'portal_type':'Sales Packing List Line'})


  # creation of the container
  # inspired from Container_fastInput


  #Container_zGetCellList
  container_number = 1




  new_container_id = 'c'+str(container_number)

  # we use container_type to know which are the resource (and variation) of the container
  container_type_item_list = container_type.split('/')
  container_resource_url = '/'.join(container_type_item_list[0:2])
  container_resource_variation = 'variante/'+container_type

  """
  context.portal_types.constructContent(type_name = 'Container',
                                      container = delivery,
                                      int_index = container_number,
                                      serial_number = "%06d%04d" % (int(delivery.getId()),container_number),
                                      resource = container_resource_url,
                                      variation_base_category_list = ['variante'],
                                      variation_category_list = [container_resource_variation],
                                      gross_weight = gross_weight,
                                      id = new_container_id,
  )

  container = delivery[new_container_id]
  """

  


  # construct the container lines
  """
  for delivery_line in delivery_line_list:

    new_container_line_id = str(container.generateNewId())

    # construct new content (container_line)
    context.portal_types.constructContent(type_name = 'Container Line',
                                        container = container,
                                        id = new_container_line_id,
                                        resource = delivery_line.getRelativeUrl(),
                                        variation_base_category_list = delivery_line.getVariationBaseCategoryList(),
                                        variation_category_list = delivery_line.getVariationCategoryList
                                        )
    container_line = container[new_container_line_id]

    # set target_quantities in container_lines
    container_cell_list = container_line.contentValues()
    delivery_cell_list = delivery_line.contentValues()

    for container_cell in container_cell_list:
      quantity_updated = 0
      for delivery_cell in delivery_cell_list:
        if container_cell.test(context.asContext(categories=deliveryCell.getVariationCategoryList()) :
          container_cell.setTargetQuantity(deliveryCell.getQuantity())
          container_cell.flushActivity(invoke=1)
          quantity_updated = 1
          break


    # update target_quantities on delivery_lines or cells
    container.edit()

  """

  # change the workflow
  #context.Item_doWorkflowTransition(workflow_action='user_set_ready', workflow_id='delivery_workflow')


  """

  # print container label
  container.Container_printLabel(user_name=user_name)

  """


  # print
  # XXX this does not print anything, it's just a page template
  #context.sales_packing_list_print()

except:
  message = 'Livraison vente identifiant %s' % context.getId()
  # and this is the end ....
  if batch_mode:
    context.Coramy_sendMailToUser(user_name=user_name,mSubj="Autocolisage échoué",mMsg=message)
  else:
    redirect_url = '%s?%s' % ( context.absolute_url(), 'portal_status_message=Autocolisage+échoué.')
    return request[ 'RESPONSE' ].redirect( redirect_url )

else:
  message = 'Livraison vente identifiant %s' % context.getId()
  # and this is the end ....
  if batch_mode:
    context.Coramy_sendMailToUser(user_name=user_name,mSubj="Autocolisage réussi",mMsg=message)
  else:
    redirect_url = '%s?%s' % ( context.absolute_url(), 'portal_status_message=Autocolisage+réussi.')
    return request[ 'RESPONSE' ].redirect( redirect_url )
