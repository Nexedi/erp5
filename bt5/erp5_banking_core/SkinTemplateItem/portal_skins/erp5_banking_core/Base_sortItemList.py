def sort_title(a,b):
  return cmp(a[0],b[0])

begin = []
if keep_first:
  begin.append(my_list[0])
  my_list = my_list[1:]
my_list.sort(sort_title)
return begin + my_list
