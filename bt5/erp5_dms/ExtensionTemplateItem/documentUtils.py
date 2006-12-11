import zipfile, cStringIO, re
import xmlrpclib, base64
from Products.CMFCore.utils import getToolByName

def extractContent(data):
  cs=cStringIO.StringIO()
  cs.write(data)
  try:
    z=zipfile.ZipFile(cs)
  except zipfile.BadZipfile:
    cs.close()
    return ''
  s=z.read('content.xml')
  cs.close()
  z.close()
  return s

def convertToOdf(self,name,data):
  sp=mkProxy(self)
  kw=sp.run_convert(name,base64.encodestring(data))
  odf=base64.decodestring(kw['data'])
  return odf

def mkProxy(self):
  pref=getToolByName(self,'portal_preferences')
  adr=pref.getPreferredDmsOoodocServerAddress()
  nr=pref.getPreferredDmsOoodocServerPortNumber()
  if adr is None or nr is None:
    raise Exception('you should set conversion server coordinates in preferences')
  sp=xmlrpclib.ServerProxy('http://%s:%d' % (adr,nr),allow_none=True)
  return sp

def generateFile(self,name,data,format):
  sp=mkProxy(self)
  kw=sp.run_generate(name,data,None,format)
  res=base64.decodestring(kw['data'])
  return res

def getAttrFromFilename(self,fname):
  rx_parse=re.compile(self.portal_preferences.getPreferredDmsFilenameRegexp())
  m=rx_parse.match(fname)
  if m is None:
    return {}
  return m.groupdict()



# vim: syntax=python shiftwidth=2 
