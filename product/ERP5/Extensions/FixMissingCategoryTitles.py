import string

def fixMissingCategoryTitles(self):
  """
    Recursively sets a default title when it's empty or equal to id
    Must be called on CategoryTool
  """
  for base in self.getChildNodes():
    objectlist = base.getCategoryChildValueList()
    for object in objectlist :
      title = object.getTitle()
      id = object.getId()
      if len(title) == 0 or title is None or title == id :
        new_title = string.capwords(id.replace('_', ' '))
        setattr(object, 'title', new_title)
  return 'done'
