## Script (Python) "Container_fastInput"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=form_id='',selection_index=None,selection_name='',dialog_category='object_exchange',quantity=0,container_type='',gross_weight=0,listbox=None,cancel_url='',next_container_int_index=1
##title=
##
# first we build a dict of desired container lines
# key of dict : id of resource
# item of dict : tuples (resource_value, variation_category_list, quantity)
delivery = context
next_container_number = next_container_int_index

desired_lines = {}
for relative_url, listitem in listbox.items() :
  container_quantity = listitem['container_quantity']
  if container_quantity :
    listitem_value = context.restrictedTraverse(relative_url)
    if listitem_value is not None :
      my_resource = listitem_value.getResourceValue()
      if my_resource is not None :
        if my_resource.getRelativeUrl() in desired_lines.keys() :
          desired_lines[my_resource.getRelativeUrl()].append((listitem_value.getVariationCategoryList(), container_quantity))
        else :
          desired_lines[my_resource.getRelativeUrl()] = [(listitem_value.getVariationCategoryList(), container_quantity)]

# we build 'quantity' containers 
for colis_nb in range(quantity) :

  new_container_id = 'c'+str(next_container_number)
  # we use container_type to know which are the resource (and variation) of the container
  container_type_item_list = container_type.split('/')
  container_resource_url = '/'.join(container_type_item_list[0:2])
  cointainer_resource_variation = 'variante/'+container_type
  context.portal_types.constructContent(type_name = 'Container',
                                        container = delivery,
                                        int_index = next_container_number,
                                        serial_number = "%06d%04d" % (int(delivery.getId()),next_container_number),
                                        resource = container_resource_url,
                                        variation_base_category_list = ['variante'],
                                        variation_category_list = [cointainer_resource_variation],
                                        gross_weight = gross_weight,
                                        id = new_container_id,
                                        )
  next_container_number += 1
  container = delivery[new_container_id]
  container.flushActivity(invoke=1)

  # print container label
  container.Container_printMetoLabel()

  # now build container_lines
  for key in desired_lines.keys() :
    new_container_line_id = str(container.generateNewId())

    # compute variation_base_category_list and variation_category_list for this line
    line_variation_base_category_dict = {}
    line_variation_category_list = []

    for my_tuple in desired_lines[key] :

      for variation_item in my_tuple[0] :
        if not variation_item in line_variation_category_list :
          line_variation_category_list.append(variation_item)
          variation_base_category_items = variation_item.split('/')
          if len(variation_base_category_items) > 0 :
            line_variation_base_category_dict[variation_base_category_items[0]] = 1

      line_variation_base_category_list = line_variation_base_category_dict.keys()

    # construct new content (container_line)
    my_resource_url = key
    context.portal_types.constructContent(type_name = 'Container Line',
                                        container = container,
                                        id = new_container_line_id,
                                        resource = my_resource_url,
                                        variation_base_category_list = line_variation_base_category_list,
                                        variation_category_list = line_variation_category_list
                                        )
    container_line = container[new_container_line_id]

    # set target_quantities in container_lines
    container_cell_list = container_line.contentValues()
    for my_tuple in desired_lines[key] :
      quantity_updated = 0
      for container_cell in container_cell_list :
        if container_cell.test(context.asContext(categories=my_tuple[0])) :
          container_cell.setTargetQuantity(my_tuple[1])
          container_cell.flushActivity(invoke=1)
          quantity_updated = 1
          break
      # if no cell according to variation_category_list was found
      # or no variation at all, we update the container_line
      if not quantity_updated :
        container_line.setTargetQuantity(my_tuple[1])
        container_line.flushActivity(invoke=1)

  # update target_quantities on delivery_lines or cells
  container.edit()

redirect_url = '%s/%s?selection_name=%s&dialog_category=%s&form_id=%s&cancel_url=%s&%s' % ( context.absolute_url()
                            , 'Container_fastInputForm'
                            , selection_name
                            , dialog_category
                            , form_id
                            , cancel_url
                            , 'portal_status_message=%s+colis+créé(s)' % quantity
                            )

context.REQUEST[ 'RESPONSE' ].redirect( redirect_url )
