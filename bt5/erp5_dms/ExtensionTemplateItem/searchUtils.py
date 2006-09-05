
import re

# parsing defined here
simulation_states=('released','public','submitted')
r=re.compile('(\w+:"[^"]+"|\w+:[\w/\-.]+)')
filetyper=lambda s:('source_reference','%%.%s' % s)
filestripper=lambda s: ('source_reference',s.replace('"',''))
addarchived=lambda s: ('simulation_state',simulation_states+('archived',))
paramsmap=dict(file=filestripper,type='portal_type',reference='reference',filetype=filetyper,archived=addarchived,\
        language='language',version='version')

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
    searchstring='byle "cisnie zego" file:"ble ble.doc" type:Text poza tym reference:abc-def dupa:kwas/zbita'
    print parseSearchString(searchstring)
