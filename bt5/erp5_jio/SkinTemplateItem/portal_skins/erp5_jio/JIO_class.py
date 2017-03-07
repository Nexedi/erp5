import json
from DateTime import DateTime
from Products.ZSQLCatalog.SQLCatalog import SimpleQuery, ComplexQuery
from Products.ERP5Type.Log import log
portal = context.getPortalObject()

def Task_setProjectTitle(document, project_title):
  project_list = portal.portal_catalog(portal_type="Project", title=project_title)
  project_url = None
  if project_title:
    if len(project_list):
      project = project_list[0].getObject()
    else:
      project = portal.project_module.newContent(title=project_title)
    project_url = project.getRelativeUrl()
  #portal.person_module.log("Task_setProjectTitle, project", project_url)
  document.setSourceProject(project_url)

def convertTaskReportStateToJioState(state):
  # portal.person_module.log("state =========>", state)
  map = {
    "comfirmed": "Comfirmed",
    "started": "Started",
    "stopped": "Completed",
    "draft": "Draft"
  };
  return state if map.get(state) is None else map[state]

def changeTaskReportState(document, state):
  state = state.lower()
  current_state = document.getSimulationState()
  if state == "comfirmed":
    if current_state == "draft":
      document.confirm()
    return
  if state == "started":
    if current_state in ["draft", "confirmed"]:
      document.start()
    if current_state == "stopped":
      document.restart()
    return
  if state == "completed":
    if current_state in ["draft", "confirmed", "started"]:
      document.stop()
    return

def camelCaseToUnderscores(string):
  result = ""
  tmp = ""
  for char in string:
    if char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
      tmp += char
    elif tmp != "":
      tmp = tmp[:-1].lower() + "_" + tmp[-1].lower()
      if tmp[0] != "_":
        tmp = "_" + tmp
      result += tmp + char
      tmp = ""
    else:
      result += char
  if result[0] == '_' and string[0] != '_': return result[1:]
  return result

def underscores_to_camel_case(string):
    return reduce(lambda v, s: v + s.title(), string.split("_"))

def dictGetKeyFromValue(obj, value, *args):
  for k, v in obj.items():
    if v == value:
      return k
  if len(args) == 0:
    raise ValueError('value not found')
  return args[0]

def UTF8DeepJsonEncoder(obj):
  # string -> unicode -> str
  if isinstance(obj, unicode):
    return obj.encode("UTF-8")
  # array -> list
  if isinstance(obj, list):
    for i in xrange(len(obj)):
      obj[i] = UTF8DeepJsonEncoder(obj[i])
    return obj
  # object -> dict
  if isinstance(obj, dict):
    for k, v in obj.items():
      v = UTF8DeepJsonEncoder(v)
      del obj[k]
      obj[UTF8DeepJsonEncoder(k)] = v
    return obj
  # number (int) -> int, long
  # true -> True
  # false -> False
  # null -> None
  return obj

def json_loads(string):
  return UTF8DeepJsonEncoder(json.loads(string))

def jsonDeepCopy(json_dict):
  "Clones the JSON object in deep and returns the clone"
  return json_loads(json.dumps(json_dict))

class FakeDocument():
  def getObject(self): return self
  def hasProperty(self, property_id): return False


class JioErp5Only():
  def getDocumentAttachment(self, metadata_json):
    tool.checkMetadata(metadata_json)
    try: document = tool.getDocumentFromUrl(metadata_json.get("_id"))
    except ValueError: raise LookupError("Missing document")
    except KeyError: raise LookupError("Missing document")
    raise KeyError("Missing attachment")

  def getDocumentMetadata(self, metadata_json):
    tool.checkMetadata(metadata_json)
    try: document = tool.getDocumentFromUrl(metadata_json.get("_id"))
    except ValueError: raise LookupError("Missing document")
    except KeyError: raise LookupError("Missing document")
    document_dict = tool.getDocumentProperties(document)
    tool.stringifyDictDateValue(document_dict)
    document_dict["workflow_history"] = [v for v in document.workflow_history]
    return document_dict


class JioGeneric():
  "Processes generic jIO requests"
  def __init__(self):
    self.simple_conversion_dict = {
      "content_type": "format",
      "portal_type": "type",
      "contributor_list": "contributor",
      "subject_list": "subject",
      "categories_list": "category",
      "creation_date": "created",
      "modification_date": "modified",
      "start_date": "start",
      "stop_date": "stop"
    }
    # order deny, allow
    # deny from all
    self.allowed_property_id_list = ["title", "short_title", "description",
                                     "language", "reference", "version", "project",
                                     "format", "type", "start", "stop", "state",
                                     "effective_date", "expiration_date",
                                     "contributor", "subject", "category"]
    self.type_attachment_key = {
      "Web Page": "text_content",
      "Image": "data"
    }
    self.allowed_portal_type_list = ["Task Report"]
    # self.local_attachment_key = "local_attachment_dict"

  def getDocumentAttachment(self, metadata_json):
    tool.checkMetadata(metadata_json)
    try: document = tool.getDocumentFromUrl(metadata_json.get("_id"))
    except AttributeError: raise ValueError("Bad document id")
    except (ValueError, KeyError): raise LookupError("Missing document")
    document_dict = tool.getDocumentProperties(document)
    attachment_key = self.type_attachment_key.get(document.getPortalType())
    if metadata_json.get("_attachment") == "body" and \
      attachment_key in document_dict:
      data = document_dict[attachment_key]
      if data is not None:
        return data
    # elif document_dict.get(self.local_attachment_key) is not None and \
    #      metadata_json.get("_attachment") in \
    #      document_dict.get(self.local_attachment_key):
    #   return document_dict[self.local_attachment_key][
    #     metadata_json["_attachment"]]["data"]
    raise KeyError("Missing attachment")

  def getDocumentMetadata(self, metadata_json):
    tool.checkMetadata(metadata_json)
    try: document = tool.getDocumentFromUrl(metadata_json.get("_id"))
    except AttributeError: raise ValueError("Bad document id")
    except ValueError: raise LookupError("Missing document")
    except KeyError: raise LookupError("Missing document")
    document_dict = tool.getDocumentProperties(document)
    real_document_dict = {}
    # get attachments metas
    attachment_key = self.type_attachment_key.get(document.getPortalType())
    if attachment_key is not None and \
      document_dict.get(attachment_key) is not None:
      real_document_dict["_attachments"] = tool.dictFusion(
        real_document_dict.get("_attachments"), {
          "body": {
            "length": len(document_dict[attachment_key]),
            "content_type": document_dict.get("content_type")
          }
        }
      )
    # if document_dict.get(self.local_attachment_key) is not None:
    #   tmp = {}
    #   for k, v in document_dict[self.local_attachment_key].items():
    #     tmp[k] = {
    #       "length": len(document_dict[self.local_attachment_key][k]["data"]),
    #       "content_type": document_dict[self.local_attachment_key][k][
    #         "content_type"]
    #     }
    #   real_document_dict["_attachments"] = tool.dictFusion(
    #     real_document_dict.get("_attachments"), tmp);
    while True:
      try: k, v = document_dict.popitem()
      except KeyError: break
      if v is None or (
          isinstance(v, (tuple, list, str, unicode)) and len(v) == 0):
        continue
      if k in self.simple_conversion_dict:
        k = self.simple_conversion_dict.get(k)
      if k in self.allowed_property_id_list:
        if isinstance(v, DateTime):
          v = v.ISO8601()
        if k == attachment_key:
          real_document_dict["_attachments"] = {
            "body": {
              "length": len(v)
            }
          }
        elif k == "category" and isinstance(v, list):
          # specific process for relation metadata_key
          relation_list = []
          for i, s in enumerate(v):
            if s.startswith("follow_up/"):
              relation_list.append(v.pop(i))
          if len(relation_list) > 0:
            real_document_dict["relation"] = relation_list
        real_document_dict[k] = v
    real_document_dict["_id"] = metadata_json["_id"]
    real_document_dict["date"] = document.getCreationDate().ISO8601()
    real_document_dict["created"] = document.getCreationDate().ISO8601()
    real_document_dict["modified"] = document.getModificationDate().ISO8601()
    real_document_dict["type"] = document.getPortalType()
    # HARD CODE for task report documents
    if document.getPortalType() == "Task Report":
      real_document_dict["state"] = convertTaskReportStateToJioState(document.getSimulationState())
      real_document_dict["project"] = document.getSourceProjectTitle()
      if real_document_dict["project"] == None: del real_document_dict["project"]
    #tool.stringifyDictDateValue(real_document_dict)
    return real_document_dict

  def updateDocumentMetadataEditKw(self, metadata_json,
                                   document=FakeDocument()):
    edit_kw = {}
    while True:
      try: meta_key, meta_value = metadata_json.popitem()
      except KeyError: break
      doc_key = meta_key
      for erp5_key, jio_key in self.simple_conversion_dict.iteritems():
        if jio_key == meta_key:
          doc_key = erp5_key
          break
      if meta_key in self.allowed_property_id_list:
        if meta_value is None and document.hasProperty(doc_key) or \
           meta_value is not None:
          edit_kw[doc_key] = meta_value
        if meta_key == "category" and metadata_json.get("relation") is not None:
          if isinstance(metadata_json["relation"], tuple):
            edit_kw[doc_key] = edit_kw[doc_key] + metadata_json["relation"]
          else:
            edit_kw[doc_key] = edit_kw[doc_key] + (metadata_json["relation"],)
    return edit_kw

  def putDocumentAttachment(self, metadata_json):
    tool.checkMetadata(metadata_json)
    document = tool.getDocumentFromUrl(metadata_json["_id"]).getObject()
    attachment_key = self.type_attachment_key.get(document.getPortalType())
    if metadata_json.get("_attachment") == "body":
      edit_kw = {attachment_key: metadata_json.get("_data")}
      document.edit(**edit_kw)
    else:
      raise ValueError("Unauthorized attachment id")
      # edit_kw = {self.local_attachment_key:
      #            document.getProperty(self.local_attachment_key)}
      # if edit_kw.get(self.local_attachment_key) is None:
      #   edit_kw[self.local_attachment_key] = {}
      # edit_kw[self.local_attachment_key][metadata_json.get("_attachment")] = {
      #   "content_type": metadata_json.get("_mimetype"),
      #   "data": metadata_json.get("_data")}
      # document.edit(**edit_kw)
    return {"id": metadata_json["_id"],
            "attachment": metadata_json.get("_attachment")}

  def putDocumentMetadata(self, metadata_json, overwrite=True):
    hard_code_json = metadata_json.copy();
    doc_id = metadata_json.get("_id")
    document = None
    try: document = tool.getDocumentFromUrl(doc_id)
    except AttributeError: pass
    except ValueError: pass
    except KeyError: pass
    if document is not None:
      if not overwrite:
        raise LookupError("Document already exists")
      # document exists
      document.getObject().edit(
        **self.updateDocumentMetadataEditKw(metadata_json, document=document))
    else:
      # document does not exist
      if "_id" in metadata_json:
        try:
          tool.newDocumentFromUrl(
            metadata_json["_id"],
            self.updateDocumentMetadataEditKw(metadata_json))
        except KeyError: raise KeyError("Bad document id")
      elif "type" in metadata_json:
        try:
          document = tool.newDocumentFromType(
            metadata_json["type"],
            self.updateDocumentMetadataEditKw(metadata_json))
          doc_id = tool.getUrlFromDocument(document)
        except ValueError:
          raise ValueError("Bad type")
      else:
        raise TypeError("Type missing")
    # HARD CODE for task report documents
    #portal.person_module.log("document type ------->", hard_code_json)
    if hard_code_json.get("type") == "Task Report":
      if isinstance(hard_code_json.get("state"), str):
        changeTaskReportState(document, hard_code_json["state"])
      #portal.person_module.log("document type Task Report, metadata project", hard_code_json.get("project"))
      Task_setProjectTitle(document, hard_code_json.get("project"))
    return {"id": doc_id}

  def removeDocument(self, metadata_json):
    tool.checkMetadata(metadata_json)
    try: document = tool.getDocumentFromUrl(metadata_json["_id"])
    except AttributeError: raise ValueError("Bad document id")
    except ValueError: raise LookupError("Missing document")
    except KeyError: raise LookupError("Missing document")
    document_id = document.getId()
    document.getParentValue().manage_delObjects(ids=[document_id])
    return {"id": metadata_json["_id"]}

  def removeAttachment(self, metadata_json):
    tool.checkMetadata(metadata_json)
    try: document = tool.getDocumentFromUrl(metadata_json["_id"])
    except AttributeError: raise ValueError("Bad document id")
    except ValueError: raise LookupError("Missing document")
    except KeyError: raise LookupError("Missing document")
    attachment_key = self.type_attachment_key.get(document.getPortalType())
    if metadata_json.get("_attachment") == "body":
      if document.getTextContent() == None:
        raise LookupError("Missing attachment")
      edit_kw = {attachment_key: None}
      document.edit(**edit_kw)
    else:
      raise ValueError("Unauthorized attachment id")
    return {"id": metadata_json["_id"],
            "attachment": metadata_json.get("_attachment")}

  def parseQuery(self, query_dict):
    def rec(query_dict):
      if query_dict.get("type") == "simple":
        # if query_dict.get("key") not in self.allowed_property_id_list:
        #   return None
        for erp5_key, jio_key in self.simple_conversion_dict.items():
          if query_dict["key"] == jio_key:
            query_dict["key"] = erp5_key
            break
        return SimpleQuery(comparison_operator=query_dict['operator'],
                           **{query_dict['key']: query_dict['value']})
      if query_dict.get("type") == "complex":
        tool.listMapReplace(rec, query_dict['query_list'])
        try:
          while True: query_dict['query_list'].remove(None)
        except ValueError: pass
        return ComplexQuery(logical_operator=query_dict['operator'],
                            *query_dict['query_list'])
      return None
    return rec(query_dict)

  def getAllDocuments(self, option_json):
    response = {"rows":[]}
    kw = {}
    if isinstance(option_json.get('query'), dict):
      kw['query'] = self.parseQuery(option_json["query"])
      kw['query'] = ComplexQuery(
        kw['query'],
        ComplexQuery(
          logical_operator='or',
          *[SimpleQuery(comparison_operator="=", portal_type=x) \
            for x in self.allowed_portal_type_list]
        ),
        comparison_operator='and'
      )
    else:
      kw['query'] = ComplexQuery(
        logical_operator='or',
        *[SimpleQuery(comparison_operator="=", portal_type=x) \
          for x in self.allowed_portal_type_list]
      )

    if isinstance(option_json.get('limit'), list):
      kw['limit'] = tuple(option_json['limit'])

    c = self.simple_conversion_dict
    if isinstance(option_json.get('sort_on'), list):
      for i in range(len(option_json['sort_on'])):
        s = option_json['sort_on'][i]
        option_json['sort_on'][i] = dictGetKeyFromValue(c, s[0], s[0])
      kw['sort_on'] = option_json['sort_on']

    if not isinstance(option_json.get('select_list'), list):
      option_json['select_list'] = []
    if option_json['select_list'] != []:
      id_list = context.portal_catalog.getSQLCatalog().getColumnIds()
      i = len(option_json['select_list']) - 1
      while i >= 0:
        s = option_json['select_list'][i]
        option_json['select_list'][i] = dictGetKeyFromValue(c, s, s)
        if option_json['select_list'][i] not in id_list:
          option_json['select_list'].pop(i)
        i -= 1
    kw['select_list'] = option_json['select_list']
    #portal.person_module.log("catalog ----------===============>", kw);
    for document in context.portal_catalog(**kw):
      url = tool.getUrlFromDocument(document)
      row = {"id": url, "key": url, "value": {}}
      for erp5_meta in option_json['select_list']:
        jio_meta = c.get(erp5_meta, erp5_meta)
        row['value'][jio_meta] = getattr(document, erp5_meta, None)
        if isinstance(row['value'][jio_meta], DateTime):
          row['value'][jio_meta] = row['value'][jio_meta].ISO8601()
      if option_json.get('include_docs') is True:
        row["doc"] = self.getDocumentMetadata({"_id": url})
      response["rows"].append(row)
    response["total_rows"] = len(response["rows"])
    return response

  # def getAllDocuments(self, option_json):
  #   response = {"rows":[]}
  #   editkw = {}
  #   if "query" in option_json:
  #     editkw['query'] = self.parseQuery(option_json["query"])
  #     editkw['query'] = ComplexQuery(
  #       editkw['query'],
  #       ComplexQuery(
  #         logical_operator='or',
  #         *[SimpleQuery(comparison_operator="=", portal_type=x) \
  #           for x in self.allowed_portal_type_list]
  #       ),
  #       comparison_operator='and'
  #     )
  #     # if isinstance(option_json.get('limit'), list):
  #     #   editkw['limit'] = tuple(option_json['limit'])

  #     # if isinstance(option_json.get('select_list'), list):
  #     #   for sub_list in option_json['select_list']:
  #     #     sub_list = tuple(sub_list)
  #     #   editkw['select_list'] = option_json['select_list']

  #     for document in context.portal_catalog(query=query):
  #       url = tool.getUrlFromDocument(document)
  #       row = {"id": url, "key": url, "values": {}}
  #       if option_json.get('include_docs') is True:
  #         row["doc"] = self.getDocumentMetadata({"_id": url})
  #       response["rows"].append(row)
  #   else:
  #     for portal_type in self.allowed_portal_type_list:
  #       for document in context.portal_catalog(portal_type=portal_type):
  #         url = tool.getUrlFromDocument(document)
  #         row = {"id": url, "key": url, "values": {}}
  #         if option_json.get('include_docs') is True:
  #           row["doc"] = self.getDocumentMetadata({"_id": url})
  #         response["rows"].append(row)
  #   response["total_rows"] = len(response["rows"])
  #   return response

  # def getAllDocuments(self, option_json):
  #   response = {"rows":[]}
  #   for portal_type in self.allowed_portal_type_list:
  #     for document in context.portal_catalog(portal_type=portal_type):
  #       url = tool.getUrlFromDocument(document)
  #       row = {"id": url, "key": url, "values": {}}
  #       if option_json.get('include_docs') is True:
  #         row["doc"] = self.getDocumentMetadata({"_id": url})
  #       response["rows"].append(row)
  #   response["total_rows"] = len(response["rows"])
  #   return response

class JioTool():
  # TODO doc strings

  def listMapReplace(self, function, li):
    """listMapReplace(function, list)

        li = [1, 2, 3]
        listFilter(lambda x: x + 1, li)
        print(li) -> [2, 3, 4]

    """
    for i in range(len(li)):
        li[i] = function(li[i])

  def createBadRequestDict(self, message, reason):
    return {
      "status": 405,
      "statusText": "Bad Request",
      "error": "bad_request",
      "message": message,
      "reason": reason
    }

  def createForbiddenDict(self, message, reason):
    return {
      "status": 403,
      "statusText": "Forbidden",
      "error": "forbidden",
      "message": message,
      "reason": reason
    }

  def createNotFoundDict(self, message, reason):
    return {
      "status": 404,
      "statusText": "Not Found",
      "error": "not_found",
      "message": message,
      "reason": reason
    }

  def createConflictDict(self, message, reason):
    return {
      "status": 409,
      "statusText": "Conflict",
      "error": "conflict",
      "message": message,
      "reason": reason
    }

  def checkMetadata(self, metadata_json):
    "Check if the id of the metadata is good"
    if metadata_json.get("_id") is None or metadata_json.get("_id") == "":
      raise ValueError("Bad document id")

  def getUrlFromDocument(self, document):
    return "/" + context.getPortalObject().\
      getDefaultModule(document.getPortalType()).getId() + "/" + \
      document.getProperty("id")

  def getDocumentFromUrl(self, url):
    "Return an ERP5 document from an url. ex: '/web_page_module/2'"
    url = url.split("/")
    if len(url) != 3 or url[0] != "":
      raise ValueError("Wrong URL")
    url = url[1:]
    return context.getPortalObject()[url[0]][url[1]] # throws KeyError

  def newDocumentFromUrl(self, url, edit_kw={}):
    "Create a new document from an url. ex: '/web_page_module/<num>'"
    url = url.split("/")
    if len(url) < 2 or url[0] != "":
      raise ValueError("Wrong URL")
    try: edit_kw["id"] = int(url[2])
    except ValueError: raise ValueError("Wrong URL")
    return context.getPortalObject()[url[1]].newContent(**edit_kw)

  def newDocumentFromType(self, portal_type, edit_kw={}):
    "Create a new document from a portal_type. ex: 'Web Page'"
    return context.getPortalObject().getDefaultModule(portal_type).\
      newContent(**edit_kw)

  def getDocumentProperties(self, document):
    document = document.getObject()
    document_dict = {}
    for property_definition in document.getPropertyMap():
      property_id = property_definition["id"]
      document_dict[property_id] = document.getProperty(property_id)
    return document_dict

  def jsonUtf8Loads(self, json_str):
    return json_loads(json_str)

  def stringifyDictDateValue(self, obj_dict):
    for k, v in obj_dict.items():
      if isinstance(v, DateTime):
        obj_dict[k] = v.ISO8601()

  def formatMetadataToPut(self, metadata_json):
    for k, v in metadata_json.iteritems():
      if isinstance(v, list):
        metadata_json[k] = tuple(v)
    return metadata_json

  def dictFusion(self, *dict_tuple):
    result = {}
    for dicti in dict_tuple:
      if dicti is not None:
        for k, v in dicti.items():
          result[k] = v
    return result

  def __init__(self, mode="generic"):
    self.mode_dict = {
      "generic": JioGeneric,
      "erp5_only": JioErp5Only
    }
    self.setMode(mode)

  def setMode(self, mode):
    self.jio = self.mode_dict[mode]()

  def getDocumentMetadata(self, metadata_json):
    return self.jio.getDocumentMetadata(metadata_json)

  def getDocumentAttachment(self, metadata_json):
    return self.jio.getDocumentAttachment(metadata_json)

  def putDocumentMetadata(self, metadata_json, overwrite=True, need_id=False):
    metadata = self.formatMetadataToPut(
      jsonDeepCopy(metadata_json))
    if need_id:
      if not isinstance(metadata.get("_id"), str) or metadata.get("_id") == "":
        raise ValueError("Document id needed")
    return self.jio.putDocumentMetadata(metadata, overwrite=overwrite)

  def putDocumentAttachment(self, attachment_json):
    return self.jio.putDocumentAttachment(attachment_json)

  def removeDocument(self, metadata_json):
    return self.jio.removeDocument(metadata_json)

  def removeAttachment(self, metadata_json):
    return self.jio.removeAttachment(metadata_json)

  def getAllDocuments(self, option_json):
    return self.jio.getAllDocuments(option_json)

  def sendSuccess(self, param):
    return json.dumps({"err": None, "response": param})

  def sendError(self, param):
    return json.dumps({"err": param, "response": None})

  # def getDocumentListFromId(self, id):
  #   kw = {"portal_type":"Web Page"}
  #   kw[self.mode["id_key"]] = id
  #   return context.portal_catalog(**kw)

  # def getAllDocsFromDocumentList(self, document_list, include_docs=False):
  #   rows = []
  #   if include_docs is True:
  #     for document in document_list:
  #       id = document.getProperty(self.mode["id_key"])
  #       if id is not None:
  #         rows.append({"id": id, "key": id, "value": {}, "doc": self.getMetadataFromDocument(document)})
  #   else:
  #     for document in document_list:
  #       id = document.getProperty(self.mode["id_key"])
  #       if id is not None:
  #         rows.append({"id": id, "key": id, "value": {}})
  #   return {"total_rows": len(rows), "rows": rows}

  # def setDocumentId(self, document, id):
  #   document.getObject().setProperty(self.mode["id_key"], id)

tool = JioTool(**kw)
return tool
