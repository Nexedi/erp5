def currency_cmp(a, b):
  a_type = a[0][0]
  b_type = b[0][0]
  tmp_cmp = cmp(a_type, b_type)
  if tmp_cmp != 0:
    return tmp_cmp
  a_value = int(a[0].split()[2])
  b_value = int(b[0].split()[2])
  tmp_cmp= cmp(b_value, a_value)
  if tmp_cmp != 0:
    return tmp_cmp
  a_year = int(a[1])
  b_year = int(b[1])
  return cmp(a_year, b_year)

list.sort(currency_cmp)
return list
