history_list = context.getMovementHistoryList(**kw)
reverse_list = []
for x in history_list:
  reverse_list.insert(0, x)
return reverse_list
