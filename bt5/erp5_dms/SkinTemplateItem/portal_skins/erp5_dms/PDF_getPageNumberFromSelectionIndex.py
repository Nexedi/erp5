content_information = context.getContentInformation()
number_of_pages = int(content_information.get('Pages', 1))
max = number_of_pages - 1
selection_index = int(selection_index)

if selection_index > max:
  return max
elif -max > selection_index:
  return 0
elif selection_index < 0:
  return max + selection_index + 1
else:
  return selection_index
