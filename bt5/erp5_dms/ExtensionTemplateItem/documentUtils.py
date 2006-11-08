import zipfile, cStringIO, re

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

# vim: syntax=python shiftwidth=2 
