'''
  this script is just made to have a simple visual render of the paysheet
  calculation
'''

line_dict_list = context.PaySheetTransaction_getLineListAsDict()

title_list = ['Designation\t\t', 'Base', 'Employer Rate', 'Employer Share', 
    'Employee Rate', 'Employee Share']

print '\t\t'.join(title_list)
print ''

def rightPad(string, length):
  string=str(string)
  if len(string)>length:
    return string[:length]
  return string + ' ' * (length - len(string))

for line in line_dict_list:
  string_to_display = []
  string_to_display.append(rightPad(line['title'], 40))
  string_to_display.append(rightPad(line['base'], 16))

  if 'employer_quantity' in line:
    string_to_display.append(rightPad(str(line['employer_price']), 24))
    string_to_display.append(rightPad(str(line['employer_quantity']), 24))
  else:
    string_to_display.append(rightPad(' ', 24))
    string_to_display.append(rightPad(' ', 24))

  if 'employee_quantity' in line:
    string_to_display.append(rightPad(str(line['employee_price']), 24))
    string_to_display.append(rightPad(str(line['employee_quantity']), 24))
  else:
    string_to_display.append(rightPad(' ', 24))
    string_to_display.append(rightPad(' ', 24))

  print ''.join(string_to_display)

return printed
