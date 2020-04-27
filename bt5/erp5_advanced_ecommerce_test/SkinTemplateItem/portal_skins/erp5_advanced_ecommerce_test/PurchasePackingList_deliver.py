test_purchase_packing_list = context.purchase_packing_list_module.test_purchase_packing_list
if test_purchase_packing_list.getSimulationState() == 'draft':
  test_purchase_packing_list.confirm()
  test_purchase_packing_list.start()
  test_purchase_packing_list.stop()
  test_purchase_packing_list.deliver()
return 'Done'
