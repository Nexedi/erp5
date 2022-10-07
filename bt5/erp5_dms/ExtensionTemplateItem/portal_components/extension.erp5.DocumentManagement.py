##############################################################################
#
# Copyright (c) 2006-2007 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import zipfile, cStringIO, re
import six.moves.xmlrpc_client, base64
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
  sp = six.moves.xmlrpc_client.ServerProxy('http://%s:%d' % (adr,nr), allow_none=True)
  return sp

def generateFile(self, name, data, format):  # pylint: disable=redefined-builtin
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
  if not hasattr(self, 'workflow_history'):
    return None
  for wflow in self.workflow_history.values():
    if wflow is None or len(wflow) == 0: continue # empty history
    if wflow[0].get(state_name) is None: continue # not the right one
    for i in range(len(wflow)):
      ch = wflow[-1-i]
      act = ch.get('action', '')
      if act is not None and act.endswith('action'):
        if ch.get(state_name, '') in state:
          return ch['time']
  return None

#############################################################################
# Mail management

def findAddress(txt):
  """
  find email address in a string
  """
  validchars = r'0-9A-Za-z.\-_'
  r=re.compile('[%s]+@[%s]+' % (validchars,validchars))
  m=r.search(txt)
  return m and m.group()

def extractParams(txt):
  """
  extract parameters given in mail body
  We assume that parameters are given as lines of the format:
  name:value
  """
  r = re.compile(r'^([\w_]+):([\w_/]+)$')
  res=[]
  for line in txt.split():
    found=r.findall(line.strip())
    if len(found)==1:
      res.append(found[0])
  return dict(res)
