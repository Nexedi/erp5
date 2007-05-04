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

"""
RULES

Single arguments:
    - arg:value translates into arg='value' in query
    - quotes are cleared
    - if value contains spaces, punctuation or anything else it has to be put in quotes
    - file is source_reference (original file name)
    - language, version, reference

Multiple arguments:
    - arg:xxx works the same way
    - arg:(xxx,yyy) ORs both
    - arg:all translates into empty tuple, which implies all available values
    - state (simulation_state), type (portal_type)

Everything else is treated as SearchableText
"""

# XXX score:
# pythonicity: high
# obfuscation level: brain-twisting

# how to customize:
# (1) think for two hours
# (2) type for 20 seconds

import re
import sys
sys.path.append('/usr/lib/zope/lib/python/')
from DateTime import DateTime

def dateRangeProc(s):
    """
    process date range (can be given in months or years)
    """
    m=re.match('(\d)([wmy]).*',s)
    try:
        dif=0
        gr=m.groups()
        if gr[1]=='w':dif=int(gr[0])*7
        if gr[1]=='m':dif=int(gr[0])*30
        if gr[1]=='y':dif=int(gr[0])*365
        return ('creation_from',DateTime()-dif)
    except AttributeError, IndexError:
        return ()

# parsing defined here
simulation_states=()
r=re.compile('(\w+:"[^"]+"|\w+:\([^)]+\)|\w+:[\(\),\w/\-.]+)')
filetyper=lambda s:('source_reference','%%.%s' % s)
filestripper=lambda s: ('source_reference',s.replace('"',''))
#addarchived=lambda s: ('simulation_state',simulation_states+('archived',))
state=lambda s:('simulation_state',parsestates(s))
type=lambda s:('portal_type',parsestates(s))
paramsmap=dict(file=filestripper,type=type,reference='reference',filetype=filetyper,state=state,\
        language='language',version='version',created=dateRangeProc)

def parsestates(s):
    print s
    if s=='all':
        return ()
    if s[0]=='(' and s[-1]==')':
        return [i.replace('"','').replace("'","") for i in s[1:-1].split(',') if i!='']
    return s.replace('"','').replace("'","")

def analyze(params):
    params['SearchableText']=''
    params['simulation_state']=simulation_states
    def cutter(s):
        ss=s.split(':')
        if len(ss)==1:
            params['SearchableText']+=ss[0]
        if len(ss)==2:
            try:
                ps=paramsmap.get(ss[0])(ss[1])
                params[ps[0]]=ps[1]
            except TypeError:
                if paramsmap.has_key(ss[0]):
                    params[paramsmap.get(ss[0])]=ss[1]
                else:
                    params[ss[0]]=ss[1]
            except IndexError:
                return
    return cutter

def parseSearchString(searchstring):
    params={}
    l=r.split(searchstring)
    print l
    map(analyze(params),l)
    params['SearchableText']=params['SearchableText'].strip()
    return params

if __name__=='__main__':
    #searchstring='byle cisnie zego file:"ble ble.doc" filetype:doc type:Text poza tym reference:abc-def'
    #searchstring='byle "cisnie zego" state:draft file:"ble ble.doc" type:("Site","Text") poza tym reference:abc-def dupa:kwas/zbita'
    searchstring='byleco created:3mth'
    print parseSearchString(searchstring)
