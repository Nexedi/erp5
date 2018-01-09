counter = 0

for value in context.contentValues():
  counter = counter + int(value.getQuantity())

return counter
