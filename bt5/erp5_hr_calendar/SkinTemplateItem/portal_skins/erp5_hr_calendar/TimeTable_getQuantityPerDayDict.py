day_dict = {}
for line in context.objectValues():
  day_dict[line.getDayOfWeek()] = line.getQuantity()

return day_dict
