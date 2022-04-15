""" display value in the cell according to (french) fiscality rules """
context.log(cell_name, cell_value)

if same_type(cell_value, 0) or same_type(cell_value, 0.0) : 
  number = cell_value
  if number == 0 : 
    return ""

  negative = number < 0
  amount = str(abs(number))
  indexes = list(range(len(amount)))
  indexes.reverse()
  string = ''
  count = 0
  for i in indexes :
    if not count % 3 :
      string = ' ' + string
    string = amount[i] + string
    count += 1
  if negative :
    string = "(%s)"%string.strip()
  return string
else :
  return cell_value
