filter_dict = {}
filter_dict['fixed_price']=1
kw['disable_node'] = 1
return context.Delivery_viewCheckbookInputDialog(model_filter_dict=filter_dict,simulation_state='confirmed',**kw)
