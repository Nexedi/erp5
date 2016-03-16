catalog_kw = {'select_dict': {'quantity':'stock.quantity'}, 'stock.quantity': '!=0' }
return context.ERP5Site_checkCatalogTable(
  active_process=context.newActiveProcess().getPath(),
  activity_count=activity_count,
  bundle_object_count=bundle_object_count,
  catalog_kw=catalog_kw,
  property_override_method_id='ERP5Site_getStockTableFilterDict',
  **kw)
