history_list = context.getMovementHistoryList(**kw)
reverse_list = []
for x in history_list:
  try:
    if x.getVisibilityState() == "hidden":
      continue
  except AttributeError:
    pass
  reverse_list.insert(0, x)
return reverse_list
