# this script creates an inventory for each supplier
# and places all the resource provided by the supplier in this inventory
from DateTime import DateTime
from zLOG import LOG

def Inventory_buildInventories(self, start_at=0,REQUEST=None):
  """
  build inventories
  """
  context=self

  inventory_module = context.inventaire_mp

  my_supplier_item_list = context.Resource_getSupplierItemList()
  my_supplier_title_list = map(lambda x:x[0], my_supplier_item_list)

  #for supplier in my_supplier_title_list[int(start_at):min(int(start_at)+20,len(my_supplier_title_list))] :
  for supplier in my_supplier_title_list:
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
    #try:
    #  inventory.InventoryMP_massiveAddLine(product_reference_list=[], supplier_list=[supplier])
    #except:
    #  LOG('Inventory_buildInventories Error',0,'supplier: %s, ERROR ON id: %s' % (str(supplier),new_inventory_id))

    LOG('Inventory_buildInventories Ok',0,'New inventory created: %s' % str(new_inventory_id))
    get_transaction().commit()


