if context.getCashStatus() == 'to_sort':
  # in this case, resource do not change
  return context.getSource()
else:
  return None
