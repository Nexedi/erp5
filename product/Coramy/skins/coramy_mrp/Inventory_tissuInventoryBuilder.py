## Script (Python) "Inventory_tissuInventoryBuilder"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=product_reference_list=[], supplier_list=[]
##title=Add Lines to an Inventory
##
inventory_line_portal_type = "Inventory MP Line"
product_list = []

if len(product_reference_list) > 0 :
  product_list += product_reference_list
  supplier_list = ['']

elif len(supplier_list) > 0 :
  product_raw_list = context.Resource_sqlResourceSupplierSearch(supplier_title_list=supplier_list)
  for product_item in product_raw_list :
    product_list.append(product_item.title)

if len(product_list) > 0 :
  # build the inventory
  inventory_module = context.getPortalObject().inventaire_mp
  for supplier in supplier_list :
    # create inventory
    new_inventory_id = str(inventory_module.generateNewId())
    my_categories = ['destination/site/Stock_MP/Gravelines','destination_section/group/Coramy']
    context.portal_types.constructContent(type_name = 'Inventory MP',
          container = inventory_module,
          id = new_inventory_id,
          description = supplier,
          start_date = DateTime(),
          categories = my_categories)
    inventory =  inventory_module[new_inventory_id]

for line_product in product_list :

  new_id = str(inventory.generateNewId())
  inventory.portal_types.constructContent(type_name=inventory_line_portal_type,
                                                          container=inventory,
                                                          id=new_id)
  inventory_line =  inventory[new_id]
  resource_list = context.portal_catalog(id=line_product, portal_type='Tissu')
  if len(resource_list) > 0:
    resource_value = resource_list[0].getObject()
    if resource_value is not None:

      if resource_value.getPortalType() == 'Tissu' :
        my_variation_base_category_list = ['coloris']
      else :
        my_variation_base_category_list = []

      inventory_line.edit(description=line_product ,
                                  resource_value = resource_value,
                                  variation_base_category_list = my_variation_base_category_list)
      my_variation_category_list = []
      for category_tuple in inventory_line.getVariationRangeCategoryItemList() :
        my_variation_category_list.append(category_tuple[0])
      inventory_line.setVariationCategoryList(my_variation_category_list)

  else:
    inventory_line.edit(description=line_product)
