# this script creates an inventory for each supplier
# and places all the resource provided by the supplier in this inventory
from DateTime import DateTime
from zLOG import LOG

def Inventory_testBuildInventories(self, item=0,REQUEST=None):
  """
  build inventories
  """
  context=self

  inventory_module = context.inventaire_mp

  my_supplier_item_list = context.Resource_getSupplierItemList()
  my_supplier_title_list = map(lambda x:x[0], my_supplier_item_list)

  LOG('testBuildInventories',0,'supplier: %s' % str(my_supplier_title_list[item]))
  for supplier in my_supplier_title_list[item] :
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

    # create all inventory lines
    inventory.InventoryMP_fastAddLine(product_reference_list=[], supplier_list=[supplier])

