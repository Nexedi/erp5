ok_types = ("CORAMY Variante Composant", "CORAMY Composant")

def doUpdateAttributes(self):
  #o = self.composant.SY003['21608 bronze']
  #['21608 bronze'].aq_base
  #delattr(o , 'width')
  #return '<p>Test ' + str(hasattr(o , 'width')) \
  #  + str(o.meta_type) \
  #  + str(o.__dict__) \
  #  + '</p>'
  #o.manage_delProperties(ids=('height',))
  #delattr(o, 'height')
  return updateAttributes(self.composant) + '<p>END</p>'

def updateAttributes(self):

  output = ''

  base = self.aq_base
  if hasattr(base, 'width'):
    output += "<p>width %s</p>\n" % self.absolute_url()
    if not hasattr(base, 'base_width'):
      if type(base.width) == type(0.0):
        base.base_width = base.width
    else:
      if type(base.base_width) != type(0.0):
        base.base_width = 0.0
      else:
        base.base_width = 0.0
    base.width = 0.0
    delattr(self, 'width')

  if hasattr(base, 'length'):
    output += "<p>length %s</p>\n" % self.absolute_url()
    if not hasattr(base, 'base_length'):
      if type(base.length) == type(0.0):
        base.base_length = base.length
      else:
        base.base_length = 0.0
    else:
      if type(base.base_length) != type(0.0):
        base.base_length = 0.0
    base.height = 0.0
    delattr(self, 'height')

  if hasattr(base, 'height'):
    output += "<p>height %s</p>\n" % self.absolute_url()
    if not hasattr(base, 'base_height'):
      if type(base.height) == type(0.0):
        base.base_height = base.height
      else:
        base.base_height = 0.0
    else:
      if type(base.base_height) != type(0.0):
        base.base_height = 0.0
    base.height = 0.0
    delattr(base, 'height')

  #try:
  for o in self.objectValues():
      output += updateAttributes(o)
  #except:
  #  pass

  return output
