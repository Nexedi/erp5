
import re

# parsing defined here
r=re.compile('(\w+:"[^"]+"|\w+:[\w\-.]+)')
filetyper=lambda s:('source_reference','%%.%s' % s)
filestripper=lambda s: ('source_reference',s.replace('"',''))
paramsmap=dict(file=filestripper,type='portal_type',reference='reference',filetype=filetyper)

def analyze(params):
    params['SearchableText']=''
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
    return cutter

def parseSearchString(searchstring):
    params={}
    l=r.split(searchstring)
    print l
    map(analyze(params),l)
    return params

if __name__=='__main__':
    #searchstring='byle cisnie zego file:"ble ble.doc" filetype:doc type:Text poza tym reference:abc-def'
    searchstring='byle "cisnie zego" file:"ble ble.doc" type:Text poza tym reference:abc-def'
    print parseSearchString(searchstring)
