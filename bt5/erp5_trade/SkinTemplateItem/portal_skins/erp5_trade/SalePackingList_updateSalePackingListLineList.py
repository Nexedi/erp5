listbox, kw = context.Delivery_updateFastInputLineList(line_portal_type="Sale Packing List Line",
                                                        supply_cell_portal_type="Sale Supply Cell",
                                                        listbox=listbox,
                                                        **kw)

return context.SalePackingList_viewSalePackingListFastInputDialog(listbox=listbox,**kw)
