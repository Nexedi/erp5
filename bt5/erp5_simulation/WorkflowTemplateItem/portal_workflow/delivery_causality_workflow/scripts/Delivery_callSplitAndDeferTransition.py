delivery = state_change['object']

stop_date = state_change.kwargs['stop_date']
start_date = state_change.kwargs['start_date']

listbox = state_change['kwargs'].get('listbox')
split_movement_list = []
if listbox is not None:
  for line in listbox:
    url = line['listbox_key']
    choice = line['choice']
    if choice == 'SplitAndDefer':
      split_movement_list.append(delivery.restrictedTraverse(url))

delivery.splitAndDefer(split_movement_list=split_movement_list,
                       start_date=start_date,
                       stop_date=stop_date,
                       comment='')
