# first we build a dict of desired container lines
# key of dict : id of resource
# item of dict : tuples (resource_value, variation_category_list, quantity)
from ZTUtils import make_query
from Products.ERP5Type.ImmediateReindexContextManager import ImmediateReindexContextManager

delivery = context
next_container_number = next_container_int_index

desired_lines = {}
quantity_unit_dict = {}

for listitem in listbox :
  movement_relative_url = listitem['listbox_key']
  container_quantity = listitem['container_quantity']
  if container_quantity :
    movement = context.restrictedTraverse(movement_relative_url)
    if movement is not None:
      resource = movement.getResourceValue()
      if resource is not None:
        quantity_unit_dict[resource.getRelativeUrl()] =\
                                                movement.getQuantityUnit()
        if resource.getRelativeUrl() in desired_lines.keys():
          desired_lines[resource.getRelativeUrl()].append(
                                  (movement.getVariationCategoryList(),
                                  container_quantity))
        else :
          desired_lines[resource.getRelativeUrl()] = [
                                  (movement.getVariationCategoryList(),
                                  container_quantity)]

with ImmediateReindexContextManager() as immediate_reindex_context_manager:
  # we build 'container_count' containers
  for _ in range(container_count):

    new_container_id = 'c'+str(next_container_number)
    # we use container_type to know which are the resource (and variation)
    # of the container
    container = delivery.newContent(
      # Container must be immediately reindexed,
      # in order to see good packed quantity in fast input form
      immediate_reindex=immediate_reindex_context_manager,
      portal_type="Container",
      title=new_container_id,
      int_index=next_container_number,
      serial_number="%06d%04d" % (int(delivery.getId()),
                                  next_container_number),
      resource = container_type,
      gross_weight = gross_weight,
    )

    next_container_number += 1

    # now build container_lines
    for resource_url in desired_lines.keys():

      # compute variation_base_category_list and variation_category_list for this line
      line_variation_base_category_dict = {}
      line_variation_category_list = []

      for variation_category_list, quantity in desired_lines[resource_url]:

        for variation_item in variation_category_list:
          if not variation_item in line_variation_category_list:
            line_variation_category_list.append(variation_item)
            variation_base_category_items = variation_item.split('/')
            if len(variation_base_category_items) > 0:
              line_variation_base_category_dict[variation_base_category_items[0]] = 1

        line_variation_base_category_list = line_variation_base_category_dict.keys()

      # construct new content (container_line)
      new_container_line_id = str(container.generateNewId())
      container_line = container.newContent(
        immediate_reindex=immediate_reindex_context_manager,
        portal_type="Container Line",
        title=new_container_line_id,
        resource=resource_url,
        quantity_unit=quantity_unit_dict[resource_url],
        variation_category_list=line_variation_category_list
      )

      for cell_key, quantity in desired_lines[resource_url]:
        if variation_category_list == []:
          container_line.edit(quantity=quantity)
        else:
          # create a new cell
          base_id = 'movement'
          if not container_line.hasCell(base_id=base_id, *cell_key):
            cell = container_line.newCell(
              immediate_reindex=immediate_reindex_context_manager,
              base_id=base_id,
              portal_type="Container Cell",
              *cell_key
            )
            cell.setCategoryList(cell_key)
            cell.setMappedValuePropertyList(['quantity'])
            cell.setMembershipCriterionCategoryList(cell_key)
            cell.setMembershipCriterionBaseCategoryList(
                                            line_variation_base_category_list)
            cell.edit(quantity=quantity)

url_params = make_query(selection_name=selection_name,
                        dialog_category=dialog_category,
                        form_id=form_id,
                        cancel_url=cancel_url,
                        portal_status_message='%s container(s) created.' %\
                                                                container_count)

redirect_url = '%s/SalePackingList_viewContainerFastInputDialog?%s' %\
                            (context.absolute_url(), url_params)

context.REQUEST[ 'RESPONSE' ].redirect(redirect_url)
