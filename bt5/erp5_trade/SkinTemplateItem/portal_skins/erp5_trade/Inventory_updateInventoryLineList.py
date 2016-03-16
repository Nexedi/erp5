listbox, kw = context.Delivery_updateFastInputLineList(line_portal_type="Inventory Line",
                                                        supply_cell_portal_type="Sale Supply Cell",
                                                        listbox=listbox,
                                                        no_inventory=True,
                                                        **kw)
return context.Inventory_viewInventoryFastInputDialog(listbox=listbox,**kw)
