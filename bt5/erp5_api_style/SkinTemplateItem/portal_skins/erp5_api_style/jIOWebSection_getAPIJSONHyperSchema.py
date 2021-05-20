base_url = context.absolute_url().strip("/") + "/"
data = {
  "$schema": "https://json-schema.org/draft/2019-09/schema",
  "base": base_url,
  "links": [
  ]
}

def generateActionInputSchemaUrl(url):
  _, script = url.rsplit('/', 1)
  return base_url + script + "/getTextContent"

def populateLinks(jio_type, url, action_list):
  result_list = []
  for action in action_list:
    action = action.getObject()
    result_list.append({
      "jio_type": jio_type,
      "href": url,
      "targetSchema": generateActionInputSchemaUrl(action.getActionText()),
      "title": action.getTitle(),
      "method": "POST",
      "curl-example": 'curl -u user:password %s -H "Content-Type: application/json" --data @input.json' % (base_url + url,)
    })
  return result_list
data["links"] = data["links"] + [{
  "jio_type": "get",
  "href": "get/",
  "targetSchema": "get-request-schema.json",
  "title": "Get Document",
  "method": "POST",
  "curl-example": 'curl -u user:password %s -H "Content-Type: application/json" --data @input.json' % (base_url + "get/",)
}]
data["links"] = data["links"] + populateLinks("post", "post/", context.ERP5Site_getAllActionListForAPIPost())
data["links"] = data["links"] + populateLinks("put", "put/", context.ERP5Site_getAllActionListForAPIPut())
data["links"] = data["links"] + populateLinks("allDocs", "allDocs/", context.ERP5Site_getAllActionListForAPIAllDocs())
import json
return json.dumps(
  data,
  indent=2,
)
