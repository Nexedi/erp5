context.getVcsTool().setLogin(auth, user, password)

import json
commit_dict = json.loads(commit_json)
context.log('BusinessTemplate_doVcsLogin\ndict %s' % str(commit_dict))
return context.restrictedTraverse(commit_dict['caller'].encode())(commit_json=commit_json)# XXX**commit_dict['caller_kw'])
