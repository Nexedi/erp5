brain_list = []
transaction_dict = {}
transaction_dict['title'] = parameter_dict['title']
transaction_dict['id'] = parameter_dict['id']
transaction_dict['reference'] = parameter_dict['id']
transaction_dict['start_date'] = parameter_dict['start_date']
#transaction_dict['stop_date'] = parameter_dict['stop_date']

brain_list = [brain(context=context,
	      object_type=context.getDestinationObjectType(),
              **transaction_dict),]


return brain_list
