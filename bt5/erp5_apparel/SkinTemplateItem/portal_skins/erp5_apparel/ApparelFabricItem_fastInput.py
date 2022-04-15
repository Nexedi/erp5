# erp5_apparel/ApparelFabricItem_fastInput

from Products.Formulator.Errors import ValidationError, FormValidationError
request=context.REQUEST

localizer = context.Localizer

# define the name of input
new_quantity_name = 'quantity'
new_net_width_name = 'net_width'
new_source_reference_name = 'title'
new_bath_name = 'grouping_reference'
new_comment_name = 'comment'

fabric_item_portal_type="Apparel Fabric Item"
apparel_bath_portal_type = "Apparel Bath"
inventory_cell_portal_type_list = ("Inventory Cell",)
delivery_cell_portal_type_list = ("Purchase Packing List Cell",)
cell_portal_type_list = inventory_cell_portal_type_list + delivery_cell_portal_type_list
counter = 0
created_item_list = []

start_date = context.getStartDate()
stop_date = context.getStopDate()

error_message = ''

try:
  if context.getPortalType() == fabric_item_portal_type : # we create a sub_item
    my_container = context
  else : # we create a master_item
    my_container = context.getPortalObject().apparel_fabric_item_module
  # get only lines with a piece_number and a quantity
  input_list = filter( (lambda x: (x[new_quantity_name] != '') and (x[new_quantity_name] > 0) ) ,listbox )
  error_message = ''
  for input in input_list:
      title = input[new_source_reference_name]
      catalog_list = context.portal_catalog(portal_type=fabric_item_portal_type,title=title)
      if len(catalog_list)>0:
        error_message += localizer.erp5_ui.gettext("Warning the item %s already exists.") % (title)

  if error_message=="":
    for input in input_list:
      my_quantity = input[new_quantity_name]
      # first check if needed if quantity compatible with parent_item
      if my_container.getPortalType() == fabric_item_portal_type :
        context.log('remaining quantity', my_container.getRemainingQuantity())
        if input[new_quantity_name] >= my_container.getRemainingQuantity() :
          my_quantity = None
      if my_quantity is not None :
        counter += 1

        if context.getPortalType() in cell_portal_type_list :
          if context.getDestinationValue() is None:
            error_message = localizer.erp5_ui.gettext("Warning select a destination.")
            break

        if context.getPortalType() == fabric_item_portal_type :
          if input[new_net_width_name] in ['',None]:
            input[new_net_width_name] = my_container.getLaizeUtile()
          if input[new_source_reference_name] in ['',None]:
            input[new_source_reference_name] = my_container.getSourceReference()
          if input[new_bath_name] in ['',None]:
            input[new_bath_name] = my_container.getBainTeinture()
          if input[new_comment_name] in ['',None]:
            input[new_comment_name] = my_container.getComment()

        # look if the item does not already exist
        title = input[new_source_reference_name]
        new_item = my_container.newContent(portal_type = fabric_item_portal_type,
                                                  quantity = input[new_quantity_name],
                                                  net_width = input[new_net_width_name],
                                                  source_reference = input[new_source_reference_name],
                                                  title = title,
                                                  grouping_reference = input[new_bath_name],
                                                  comment = input[new_comment_name],)

        if context.getPortalType() in cell_portal_type_list :
          new_item.edit(resource = context.getResource(),
                                      #destination = context.getDestination(),
                                      variation_category_list = context.getVariationCategoryList())
        created_item_list.append(new_item)

    # sort item by their bath
    bath_dict = {}
    bath = ''
    for item in created_item_list:
      bath = str(item.grouping_reference)
      if bath in bath_dict:
        bath_dict[str(bath)].extend([item])
      else:
        bath_dict[str(bath)] = [item]

    # get or create bath for each fabric item
    bath_container = context.getPortalObject().apparel_bath_module
    resource_uid = context.getResourceUid()
    resource_title = context.getResourceTitle()
    resource = context.getResource()
    variation_category_list = context.getVariationCategoryList()
    bath_object_list = {}
    for bath_title in bath_dict.keys():
      if bath_title != "None":
        bath_list = context.portal_catalog(portal_type=apparel_bath_portal_type, resource_uid=resource_uid, title=bath_title)
        if len(bath_list) > 0:
          for bath in bath_list:
            if bath.getVariationCategoryList() == variation_category_list:
              bath = bath_list
              bath_object = context.portal_catalog.getObject(bath.uid)
              break
        else:
          bath_object = bath_container.newContent(portal_type = apparel_bath_portal_type,
                              title = bath_title,
                              resource = resource,
                              variation_category_list = variation_category_list)
        bath_object_list[bath_title] = bath_object


    movement = context
    # get bath on root movement
    aggregate_list = movement.getAggregateValueList()
    movement_bath = "None"
    for item in aggregate_list:
      if item.getPortalType() == apparel_bath_portal_type:
        movement_bath = item.getTitle()
        break
    # must call splitQuantity to create new movement foreach new bath
    context.updateAppliedRule()
    movement_list = []
    for bath in bath_dict.keys():
      if bath != movement_bath:
        quantity = 0
        context.log('bath', bath)
        items = bath_dict[bath]
        # get quantity for new movement
        for item in items:
          quantity += item.quantity
        # create new movement
        if bath != "None":
          apparel_bath_list = [bath_object_list[bath].getRelativeUrl()]
        else:
          apparel_bath_list = [""]
        new_movement = context.portal_simulation.solveMovement(movement, None, 'SplitQuantity', additional_parameters={'aggregate_list':apparel_bath_list}, start_date=start_date, stop_date=stop_date, quantity=quantity)
        movement_list.append(new_movement[0].getRelativeUrl())
    # update root movement if require
    if movement_bath in bath_dict:
      items = bath_dict[movement_bath]
      quantity = 0
      for item in items:
        quantity += item.quantity
      movement.edit(quantity=quantity)

    delivery_list = [context.getExplanationValue().getRelativeUrl()]
    delivery = context.getExplanationValue()
    # update line on packing list
    order = context.getCausalityValue()
    applied_rule = order.getCausalityRelatedValue(portal_type="Applied Rule")
    order_portal_type = order.getPortalType()
    if order_portal_type == 'Sale Order':
        delivery_builder = order.portal_deliveries.sale_packing_list_builder
    elif order_portal_type == 'Purchase Order':
        delivery_builder = order.portal_deliveries.purchase_packing_list_builder
    explanation_uid_list = [order.getUid(),context.getUid()]
    delivery_builder.build(explanation_uid=explanation_uid_list, movement_relative_url_list=movement_list, delivery_relative_url_list=delivery_list)
    lines = delivery.objectValues()
    # udpate aggregate list on cells
    variation_text = context.getVariationText()
    for line in lines:
      if line.getResourceUid() == resource_uid:
        # get bath from line
        line_aggregate_list = line.getAggregateValueList()
        has_bath = 0
        for item in line_aggregate_list:
          if item.getPortalType() == apparel_bath_portal_type:
            has_bath = 1
            line_bath = item.getTitle()
        if not has_bath:
          line_bath = "None"
        # update aggregate list on cell
        cells = line.objectValues()
        for cell in cells:
          if cell.getVariationText() == variation_text:
            # update aggregate list with items
            cell_aggregate_list = cell.getAggregateValueList()
            if line_bath in bath_dict:
              # new items on cell
              cell_item = bath_dict[line_bath]
              cell_aggregate_list.extend(cell_item)
              cell.setAggregateValueList(cell_aggregate_list)
            # update quantity
            total_quantity = sum([x.getQuantity() for x in cell_aggregate_list])
            if cell.getPortalType() in inventory_cell_portal_type_list:
              cell.setMappedValuePropertyList(['inventory','price'])
              cell.edit(inventory=total_quantity)
            elif cell.getPortalType() in delivery_cell_portal_type_list:
              cell.setMappedValuePropertyList(['quantity','price'])
              cell.edit(quantity=total_quantity)


except FormValidationError as validation_errors:
  redirect_url = '%s/view?%s' % ( context.absolute_url()
                                  , 'portal_status_message=%s' % localizer.erp5_ui.gettext("input failed.")
                                  )
else:
  if error_message != '':
    redirect_url = '%s/view?%s' % ( context.absolute_url()
                                  , 'portal_status_message=%s' % error_message
                                  )
  else:
    redirect_url = '%s/view?%s' % ( context.absolute_url()
                                  , 'portal_status_message=%s' % (localizer.erp5_ui.gettext(" %s items created.") % (counter))
                                  )

request[ 'RESPONSE' ].redirect( redirect_url )
