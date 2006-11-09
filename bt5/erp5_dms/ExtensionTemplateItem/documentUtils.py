import zipfile, cStringIO, re
import xmlrpclib, base64
from Products.CMFCore.utils import getToolByName

rx_atr='([\w]+)###([\w/]+)'
rx_atr=re.compile(rx_atr)

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

def getAttrFromContent(data):
  return dict(rx_atr.findall(extractContent(data)))

def getDoctypeFromContent(data):
  atrs=getAttrFromContent(data)
  return atrs.get('doctype')

def convertToOdf(name,data):
  sp=mkProxy()
  kw=sp.run_convert(name,data)
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



# vim: syntax=python shiftwidth=2 
