vcard_string_list = []
first_name = context.getFirstName()
last_name = context.getLastName()
tel = context.getDefaultTelephoneTelephoneNumber()

parameters_FN = ''
parameters_N = ''

try:
  first_name.encode('utf-8')
except:
  parameters_FN = ';ENCODING=QUOTED-PRINTABLE;CHARSET=UTF-8'

try:
  last_name.encode('utf-8')
except:
  parameters_N = ';ENCODING=QUOTED-PRINTABLE;CHARSET=UTF-8'

append = vcard_string_list.append
append('BEGIN:VCARD\n')
append('VERSION:2.1\n')
if first_name not in (None, ''):
  append('FN%s:%s\n' % (parameters_FN, first_name))
if last_name not in (None, ''):
  if parameters_N == '':
    parameters = parameters_FN
  else:
    parameters = parameters_N
  append('N%s:%s;%s;;;\n' % (parameters, last_name, first_name))
else:
  append('N%s:;%s;;;\n' % (parameters_N, first_name)) #if there is no last name, we put first name another time
if tel not in (None, ''):
  append('TEL:%s\n' % tel)
append('END:VCARD')

return "".join(vcard_string_list)
