def productionOrderBuilder(self):

  context = self

  # Delete all proposed orders
  for o in context.portal_catalog(simulation_state = "auto_planned", parent_uid=[context.ordre_fabrication.getUid()]) :
    realo = o.getObject()
    realo.aq_parent._delObject(o.id)

  # Empty Zero Stock
  for mid in  context.portal_simulation.zero_stock.contentIds():
    context.portal_simulation.zero_stock._delObject(mid)

  # Expand Zero Stock as many times as needed (1 or 2 for the Coramy case)
  # for i in range(0,1):
  context.portal_simulation.zero_stock.expand()

  # Collect movements in Zero Stock applied rule
  zs_movement_list = context.portal_simulation.zero_stock.contentValues()

  # keep only movements with a Modele resource
  movement_list = []
  for movement in zs_movement_list :
    try :
      if movement.getResourceValue().getPortalType() == 'Modele' :
        movement_list.append(movement)
    except :
      pass

  # Parse movements into a root group
  root_group = context.movementCollect(movement_list)

  # Now build orders
  order_list = []
  for path_group in root_group.group_list :
    if path_group.destination.find('site/Stock_PF') >=0 :
      # Build a Production Order
      delivery_module = context.ordre_fabrication
      delivery_type = 'Production Order'
      delivery_line_type = delivery_type + ' Line'
      delivery_cell_type = 'Delivery Cell'
    else:
      # Build a Purchase Order
      delivery_module = context.commande_achat
      delivery_type = 'Purchase Order'
      delivery_line_type = delivery_type + ' Line'
      delivery_cell_type = 'Delivery Cell'
    # we create a new delivery for each DateGroup
    for date_group in path_group.group_list :

      for resource_group in date_group.group_list :

        # Create a new production Order for each resource (Modele)
        modele_url_items = resource_group.resource.split('/')
        modele_id = modele_url_items[len(modele_url_items)-1]
        try :
          modele_object = context.getPortalObject().modele[modele_id]
        except :
          modele_object = None
        if modele_object is not None :
          of_description = modele_id+' '+modele_object.getDefaultDestinationTitle('')
        else :
          of_description = modele_id

        new_delivery_id = str(delivery_module.generateNewId())
        context.portal_types.constructContent(type_name = delivery_type,
                                            container = delivery_module,
                                            id = new_delivery_id,
                                            target_start_date = date_group.start_date,
                                            target_stop_date = date_group.stop_date,
                                            start_date = date_group.start_date,
                                            stop_date = date_group.stop_date,
                                            source = path_group.source,
                                            destination = path_group.destination,
                                            source_section = path_group.source_section,
                                            destination_section = path_group.destination_section,
                                            description = of_description,
                                            title = "Auto Planned"
                                          )
        delivery = delivery_module[new_delivery_id]
        # the new delivery is added to the order_list
        order_list.append(delivery)

        # Create each delivery_line in the new delivery

        new_delivery_line_id = str(delivery.generateNewId())
        context.portal_types.constructContent(type_name = delivery_line_type,
        container = delivery,
        id = new_delivery_line_id,
        resource = resource_group.resource,
        )
        delivery_line = delivery[new_delivery_line_id]

        line_variation_category_list = []
        line_variation_base_category_dict = {}

        # compute line_variation_base_category_list and
        # line_variation_category_list for new delivery_line
        for variant_group in resource_group.group_list :
          for variation_item in variant_group.category_list :
            if not variation_item in line_variation_category_list :
              line_variation_category_list.append(variation_item)
              variation_base_category_items = variation_item.split('/')
              if len(variation_base_category_items) > 0 :
                line_variation_base_category_dict[variation_base_category_items[0]] = 1

        # update variation_base_category_list and line_variation_category_list for delivery_line
        line_variation_base_category_list = line_variation_base_category_dict.keys()
        delivery_line.setVariationBaseCategoryList(line_variation_base_category_list)
        delivery_line.setVariationCategoryList(line_variation_category_list)

        # IMPORTANT : delivery cells are automatically created during setVariationCategoryList

        # update target_quantity for each delivery_cell
        for variant_group in resource_group.group_list :
          object_to_update = None
          # if there is no variation of the resource, update delivery_line with quantities and price
          if len(variant_group.category_list) == 0 :
            object_to_update = delivery_line
          # else find which delivery_cell is represented by variant_group
          else :
            categories_identity = 0
            for delivery_cell in delivery_line.contentValues(filter={'portal_type':'Delivery Cell'}) :
              if len(variant_group.category_list) == len(delivery_cell.getVariationCategoryList()) :
                for category in delivery_cell.getVariationCategoryList() :
                  if not category in variant_group.category_list :
                    break
                else :
                  categories_identity = 1

              if categories_identity :
                object_to_update = delivery_cell
                break

          # compute target_quantity, quantity and price for delivery_cell or delivery_line and
          # build relation between simulation_movement and delivery_cell or delivery_line
          if object_to_update is not None :
            cell_target_quantity = 0
            for movement in variant_group.movement_list :
              cell_target_quantity += movement.getConvertedTargetQuantity()

              # update every simulation_movement
              # we do not set delivery_value and target dates and quantity
              movement.edit(target_quantity = movement.getTargetQuantity(),
                            target_start_date = movement.getTargetStartDate(),
                            target_stop_date = movement.getTargetStopDate())

            object_to_update.edit(target_quantity = cell_target_quantity,
                                  quantity = cell_target_quantity,)

  # Look at result
  # return map(lambda x:x.getRelativeUrl(), order_list)
  for order in order_list:
    order.autoPlan()
    order.purchase_order_apply_condition()

  request = context.REQUEST
  redirect_url = '%s/view?%s' % ( context.absolute_url()
                                  , 'portal_status_message=%s+propositions+OF+créés.' % len(order_list)
                                  )

  request[ 'RESPONSE' ].redirect( redirect_url )
