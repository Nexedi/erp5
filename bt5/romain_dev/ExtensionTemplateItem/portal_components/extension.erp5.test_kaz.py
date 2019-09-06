
def getObjectByOid(self, oid):#XXXYYY
  ob = self._p_jar[oid]
  #return ob
  result = [ob.__class__,]
  n = 1
  for k,v in ob.iteritems():
    result.append((k, k.__class__,v, v.__class__))
    n += 1
    if n > 100:
      break
  return result