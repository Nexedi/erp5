"""Create objects with given parameters"""
from DateTime import DateTime
if category_list is None:
  category_list = ('a', 'b', 'a/a1', 'a/a2')
big_category_list = ('c1', 'c10', 'c2', 'c20', 'c3', 'c4')

for i in range(start, start + num):
  category = category_list[i % len(category_list)]
  foo = context.newContent(id = str(i), title = 'Title %d' % i, quantity = 10.0 - float(i),
                    foo_category = category, portal_type=portal_type)
  if set_dates:
    foo.setStartDate(DateTime(i, i, i))
  if create_line:
    foo.newContent()
  if big_category_related:
    big_category = big_category_list[i %len(category_list)]
    foo.setFooBigCategory(big_category)

return 'Created Successfully.'
