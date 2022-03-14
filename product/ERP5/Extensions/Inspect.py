# Simple Object Inspector

from builtins import str
def inspect(self):
  return str(self.__dict__)
  #return "type: %s dict:%s" % (type(o), o.__dict__)
  result = ''
  return self.getPhysicalPath()
