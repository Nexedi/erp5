current_owner = context.Item_getCurrentOwnerValue(at_date=at_date)
if current_owner is not None:
  return current_owner.getTitle()
return None
