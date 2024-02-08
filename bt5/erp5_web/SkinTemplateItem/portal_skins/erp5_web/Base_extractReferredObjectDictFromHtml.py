"""
Extract all object referenced by html components

`data` is the html to parse.
`allow_tag_list` is the white list of tag to parse.
  Default is to allow every tag.
`deny_tag_list` is the black list of tag to parse.
  Default is to deny no tag.
`base_url` is the url to use as base url when relative url are found,
  by using it, the script will use `site_object_dict` for each href.
  (Don't forget the ending '/' !)
`site_object_dict` is a dict of (domain, object) used to get the object
  corresponding to the absolute url found. By default the dict returned
  by `context.ERP5Site_getWebSiteDomainDict()` is used.
"""

from zExceptions import Unauthorized
portal = context.getPortalObject()

href_object_dict = {}
if not isinstance(allow_tag_list, (list, tuple)):
  allow_tag_list = None
if not isinstance(deny_tag_list, (list, tuple)):
  deny_tag_list = []

def main(data):
  if isinstance(data, bytes):
    data = data.decode("utf-8")
  for part in context.Base_parseHtml(data):
    handleHtmlPart(part)
  return href_object_dict

def handleHtmlTag(tag, attrs):
  if allow_tag_list is not None:
    if tag not in allow_tag_list:
      return
  if tag in deny_tag_list:
    return
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
  for i in range(len(attrs)):
    if attrs[i][0] == "style":
      handleCss(attrs[i][1])


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
    obj = traverseHref(href, allow_method=False)
  except (KeyError, Unauthorized):
    obj = None
  href_object_dict[href.encode("utf-8")] = obj

def handleCss(data):
  for part in context.Base_parseCssForUrl(data):
    if part[0] == "url":
      handleHref(part[2])

def isHrefAUrl(href):
  if href.startswith("https://") or href.startswith("http://"):
    return True
  split = href.split(":", 1)
  if len(split) == 1:
    return True
  return not split[0].isalpha()

def traverseHref(url, allow_method=True, allow_hash=False):
  base_obj, relative_path = prepareHrefTraverse(url, allow_hash=allow_hash)
  obj = base_obj.restrictedTraverse(relative_path)
  if allow_method or obj is None:
    return obj
  try:
    obj.getUid()
  except AttributeError:
    obj = base_obj.restrictedTraverse("/".join(relative_path.split("/")[:-1]))
  return obj

if site_object_dict is None:
  site_object_dict = context.ERP5Site_getWebSiteDomainDict()
base_url_root_object = getattr(context, "getWebSiteValue", str)() or portal
base_url_object = context

# Resolve base_url by removing everything after the last slash
force_base_url = False
if base_url is not None:
  if base_url.startswith("https://") or base_url.startswith("http://"):
    force_base_url = True
  else:
    raise ValueError("invalid `base_url` argument")
if force_base_url:
  root_url = "/".join(base_url.split("/", 3)[:3])
  if root_url != base_url:
    base_url = "/".join(base_url.split("/")[:-1])
else:
  root_url = base_url_root_object.absolute_url()
  base_url = base_url_object.absolute_url()

base_path = "/"
if base_url_object.getRelativeUrl().startswith(base_url_root_object.getRelativeUrl()):
  base_path = base_url_object.getRelativeUrl()[len(base_url_root_object.getRelativeUrl()):]
  if base_path and not base_path.startswith("/"):
    base_path = "/" + base_path

normalize_kw = {"keep_empty": False, "keep_trailing_slash": False}
def prepareHrefTraverse(href, allow_hash=False):
  url = href.split("?")[0]
  if not allow_hash:
    url = url.split("#")[0]
  if url.startswith("https://") or url.startswith("http://") or url.startswith("//"):  # absolute url possibly on other sites
    site_url = "/".join(url.split("/", 3)[:3])
    domain = url.split("/", 3)[2]
    site_object = site_object_dict[domain]
    relative_path = url[len(site_url):]
    relative_path = (relative_path[1:] if relative_path[:1] == "/" else relative_path)
    relative_path = context.Base_normalizeUrlPathname("/" + relative_path, **normalize_kw)[1:]
    return site_object, str(relative_path)
  if url.startswith("/"):  # absolute path, relative url
    if force_base_url:
      return prepareHrefTraverse(root_url + href, allow_hash=allow_hash)  # use site_domain_dict
    return base_url_root_object, str(context.Base_normalizeUrlPathname(url, **normalize_kw)[1:])
  # relative path
  if force_base_url:
    return prepareHrefTraverse(base_url + "/" + href, allow_hash=allow_hash)  # use site_domain_dict
  return base_url_root_object, str(context.Base_normalizeUrlPathname(base_path + "/" + url, **normalize_kw)[1:])

return main(data)
