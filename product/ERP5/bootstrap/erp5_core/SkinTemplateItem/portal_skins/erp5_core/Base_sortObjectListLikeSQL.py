def generic_sort(a,b):
  result = 0
  for k,v in sort_order:
    a_value = a.getProperty(k)
    b_value = b.getProperty(k)
    result = cmp(a_value,b_value)
    if result:
      if v in ('DESC', 'desc', 'descending', 'reverse'):
        return -result
      else:
        return result
  return result 

unordered_list = [x.getObject() for x in unordered_list]
unordered_list.sort(generic_sort)
return unordered_list
