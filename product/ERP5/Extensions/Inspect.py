# Simple Object Inspector

def inspect(self):
  #return "type: %s dict:%s" % (type(o), o.__dict__)
  result = ''
  return self.getPhysicalPath()
