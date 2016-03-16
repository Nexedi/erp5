priority_dict = {
  1:'Site',
  2:'Group',
}
return priority_dict.get(context.getPriority(), 'User')
