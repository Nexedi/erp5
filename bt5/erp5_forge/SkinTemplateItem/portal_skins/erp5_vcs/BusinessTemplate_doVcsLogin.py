context.getVcsTool().setLogin(auth, user, password)

import json
commit_dict = json.loads(commit_json)
return context.restrictedTraverse(commit_dict['caller'].encode())(commit_json=commit_json)
