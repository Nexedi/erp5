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

rx_fileno=re.compile('File No.: *(?P<reference>(?P<group>[A-Za-z-]+)-(?P<project>\d+)-(?P<number>\d+)\.(?P<year>\d{2}))')
rx_classif=re.compile('([A-Z]{1}[a-z]+/[A-Z]{1}[a-z]+)')

def getAttrFromContent(self,data,ptype):
  if ptype!='Memo':return {}
  atrs={}
  if data is None:return {}
  fileno=rx_fileno.search(data)
  if fileno:
    dic=fileno.groupdict()
    atrs['source_project']='project_module/'+dic['project']
    atrs['reference']=dic['reference']
  classif=rx_classif.search(data)
  log=[]
  if classif:
    classif=classif.groups()[0].split('/')
    classif.reverse()
    res=self.portal_catalog(portal_type='Category',title=classif[0])
    for r in res:
      c=r.getObject()
      for x,t in enumerate(classif):
        c=c.aq_parent
        if c.getId()=='classification':
          atrs['classification']='/'.join(r.getRelativeUrl().split('/')[1:])
          break
        if c.getTitle()!=classif[x+1]:
          break
  self.log(atrs)
  return atrs

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
