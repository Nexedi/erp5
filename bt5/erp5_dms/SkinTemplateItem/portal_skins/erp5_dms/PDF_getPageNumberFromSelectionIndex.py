content_information = context.getContentInformation()
number_of_pages = int(content_information.get('Pages', 1))
max_ = number_of_pages - 1
selection_index = int(selection_index)

if selection_index > max_:
  return max_
elif -max_ > selection_index:
  return 0
elif selection_index < 0:
  return max_ + selection_index + 1
else:
  return selection_index
