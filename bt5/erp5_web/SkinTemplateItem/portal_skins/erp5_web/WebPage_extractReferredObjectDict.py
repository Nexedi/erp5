from zExceptions import Unauthorized
portal = context.getPortalObject()

href_object_dict = {}
def main():
  for part in context.Base_parseHtml(context.getTextContent("").decode("utf-8")):
    handleHtmlPart(part)
  return href_object_dict

def handleHtmlTag(tag, attrs):
  #if tag == "base": and "href" in attrs:  # should not exist in safe-html
  #  NotImplemented
  if tag == "object":
    for i in range(len(attrs)):
      if attrs[i][0] == "data":
        handleHref(attrs[i][1])
  elif tag == "style":
    # for style tags, next data will always be the entire text until </style>
    on_next_data[0] = handleCss
  else:
    for i in range(len(attrs)):
      if attrs[i][0] in ("src", "href"):
        handleHref(attrs[i][1])

on_next_data = [lambda x: x]
def handleHtmlPart(part):
  part_type = part[0]
  if part_type in ("starttag", "startendtag"):
    return handleHtmlTag(part[1], part[2])
  if part_type == "data":
    if on_next_data[0] is None:
      return part[1]
    on_next_data[0](part[1])
    on_next_data[0] = None
    return None

def handleHref(href):
  # handles "base_url/document_module/id"
  # handles "base_url/R-Document.Reference"
  # handles "base_url/R-Document.Reference/view"
  if not isHrefAUrl(href):
    return href
  try:
    o = traverseHref(href, allow_method=False)
  except (KeyError, Unauthorized):
    o = None
  href_object_dict[href] = o

def handleCss(data):
  for part in context.Base_parseCssForUrl(data):
    if part[0] == "url":
      handleHref(part[2])

def isHrefAUrl(href):
  return href.startswith("https://") or href.startswith("http://") or not href.split(":", 1)[0].isalpha()

def traverseHref(url, allow_method=True, allow_hash=False):
  c, r = prepareHrefTraverse(url, allow_hash=allow_hash)
  o = c.restrictedTraverse(r)
  if allow_method or o is None:
    return o
  try:
    o.getUid()
  except AttributeError:
    o = c.restrictedTraverse("/".join(r.split("/")[:-1]))
  return o

site_object_dict = context.ERP5Site_getWebSiteDomainDict()
base_url_root_object = portal
base_url_object = context

def prepareHrefTraverse(url, allow_hash=False):
  url = url.split("?")[0]
  if not allow_hash:
    url = url.split("#")[0]
  if url.startswith("https://") or url.startswith("http://") or url.startswith("//"):  # absolute url possibly on other sites
    site_url = "/".join(url.split("/", 3)[:3])
    domain = url.split("/", 3)[2]
    relative_path = url[len(site_url):]
    relative_path = (relative_path[1:] if relative_path[:1] == "/" else relative_path)
    site_object = site_object_dict.get(domain)
    if site_object is None:
      raise KeyError(relative_path.split("/")[0])
    return site_object, str(relative_path)
  if url.startswith("/"):  # absolute path, relative url
    return base_url_root_object, str(url[1:])
  # relative url (just use a base url)
  return base_url_object, str(url)

return main()
