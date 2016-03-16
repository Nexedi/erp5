filter_dict = {}
filter_dict['fixed_price']=1
return context.Delivery_viewCheckbookInputDialog(item_portal_type_list=('Check',),model_filter_dict=filter_dict,**kw)
