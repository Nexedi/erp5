import json

doc = json.loads(context.getData())
AT_KEY_TO_CHANGE = 2
KEY_TO_CHANGE = 0
NEW_KEY_VAL = 1
LIST_OF_NESTED_KEYS = [
  ["layout", "title", "text"],
  ["layout", "xaxis", "title", "text"],
  ["layout", "yaxis", "title", "text"]
]

def nestedKeyExists (key_list, dictionary):
  keyExists = False
  currKey = key_list[0]
  if type(dictionary) == dict:
    if currKey in dictionary:
      smaller_list = key_list[1:]
      if len(smaller_list) == 0:
        keyExists = True
      else:
        return nestedKeyExists(smaller_list, dictionary[currKey])
  return keyExists

def changeKeysInDict(key_list, dictionary):
  if len(key_list) ==  AT_KEY_TO_CHANGE:
      dictionary[key_list[KEY_TO_CHANGE]] = dictionary[key_list[KEY_TO_CHANGE]][key_list[NEW_KEY_VAL]]
  else:
    return changeKeysInDict(key_list[1:], dictionary[key_list[0]])

for i in LIST_OF_NESTED_KEYS:
  if nestedKeyExists(i, doc):
    changeKeysInDict(i, doc)
    
doc['isPlotlyGraph'] = True;
return json.dumps(doc)
