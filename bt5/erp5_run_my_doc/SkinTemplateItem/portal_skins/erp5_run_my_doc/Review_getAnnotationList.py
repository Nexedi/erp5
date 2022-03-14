"""
  Fetches Commentaries to display them in a listbox
"""
from Products.ERP5Type.Document import newTempBase
annotation_list = context.getAnnotation().split('\n')

element_list = []
relative_url =  context.getRelativeUrl()
counter = 0
if len(annotation_list) > 0 and annotation_list[0] != "":
  for annotation in annotation_list:
    annotation_item = annotation[1:-1].split("},{")
    if len(annotation_item) == 5:
      comment, locator, context_url, author, color = annotation_item
    else:
      comment = "Failed to process: %s" % annotation
      locator, context_url, author, color = "", "", "", ""
    element_list.append(newTempBase(context.getPortalObject(), relative_url,
                   title = comment,
                   uid = str(counter),
                   int_index = 0,
                   locator = locator,
                   context_url = context_url,
                   color = color,
                   author = author
                 ))
    counter += 1

for sorted_element in sort_on:
  # pylint:disable=cell-var-from-loop
  element_list = sorted(element_list, key = lambda x: x.getProperty(sorted_element[0]), reverse = sorted_element[1] == 'descending')

return element_list
