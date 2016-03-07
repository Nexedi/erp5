listbox, kw = context.Delivery_updateFastInputLineList(line_portal_type="Sale Order Line",
                                                        supply_cell_portal_type="Sale Supply Cell",
                                                        listbox=listbox,
                                                        **kw)

return context.SaleOrder_viewSaleOrderFastInputDialog(listbox=listbox,**kw)
