foo = context.foo_module.contentValues(portal_type='Foo')[0].getObject()
foo.Foo_view.listbox.ListBox_setPropertyList(
      field_title = 'Foo Lines',
      field_list_method = 'objectValues',
      field_portal_types = 'Foo Line | Foo Line',
      field_stat_method = 'portal_catalog',
      field_stat_columns = 'quantity | Foo_statQuantity',
      field_editable = 1,
      field_columns = 'id|ID\ntitle|Title\nquantity|Quantity\nstart_date|Date',
      field_editable_columns = '',
      field_search_columns = 'id|ID\ntitle|Title\nquantity|Quantity\nstart_date|Date',)

return 'Set Successfully.'
