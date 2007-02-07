import zipfile, cStringIO, re
import xmlrpclib, base64
from Products.CMFCore.utils import getToolByName

def extractContent(data):
  """
  extract text content from ODF data
  directly by unzipping (no need for oood here)
  """
  # XXX probably not used - to really get text content it should
  # strip xml too
  cs = cStringIO.StringIO()
  cs.write(data)
  try:
    z = zipfile.ZipFile(cs)
  except zipfile.BadZipfile:
    cs.close()
    return ''
  s = z.read('content.xml')
  cs.close()
  z.close()
  return s

###### XXX these methods repeat what is in OOoDocument class
# maybe redundant, but we need to access them from Script (Python)

def convertToOdf(self, name, data):
  """
  convert data into ODF format
  to be used in ingestion when we don't yet have an ERP5 object
  to work with (and we for example have to figure out portal_type)
  """
  sp = mkProxy(self)
  kw = sp.run_convert(name,base64.encodestring(data))
  odf = base64.decodestring(kw['data'])
  return odf

def mkProxy(self):
  pref = getToolByName(self,'portal_preferences')
  adr = pref.getPreferredDmsOoodocServerAddress()
  nr = pref.getPreferredDmsOoodocServerPortNumber()
  if adr is None or nr is None:
    raise Exception('you should set conversion server coordinates in preferences')
  sp = xmlrpclib.ServerProxy('http://%s:%d' % (adr,nr), allow_none=True)
  return sp

def generateFile(self, name, data, format):
  sp = mkProxy(self)
  kw = sp.run_generate(name, data, None, format)
  res = base64.decodestring(kw['data'])
  return res

def getAttrFromFilename(self, fname):
  """
  parse file name using regexp specified in preferences
  """
  rx_parse = re.compile(self.portal_preferences.getPreferredDmsFilenameRegexp())
  m = rx_parse.match(fname)
  if m is None:
    return {}
  return m.groupdict()

def getLastWorkflowDate(self, state_name='simulation_state', state=('released','public')):
  '''we can make something more generic out of it
  or JP says "there is an API for it" and we trash this one'''
  for name,wflow in self.workflow_history.items():
    if len(wflow) == 0: continue # empty history
    if wflow[0].get(state_name) is None: continue # not the right one
    for i in range(len(wflow)):
      ch = wflow[-1-i]
      act = ch.get('action', '')
      if act is not None and act.endswith('action'):
        if ch.get(state_name, '') in state:
          return ch['time']
  return 0

# vim: syntax=python shiftwidth=2 
