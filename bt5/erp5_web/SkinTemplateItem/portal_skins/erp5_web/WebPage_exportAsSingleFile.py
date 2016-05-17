"""
Export the web page and its components to a single (m)html file.

`format` parameter could also be "mhtml".

TODO: export same components into one mhtml attachment if possible.
"""

from zExceptions import Unauthorized
from base64 import b64encode, b64decode
portal = context.getPortalObject()

mhtml_message = {
  "subtype": "related",
  "param_list": [("type", "text/html")],
  "header_dict": {"From": "<Saved by ERP5>", "Subject": "Untitled"},
  "attachment_list": [],
}

def main():
  # check if portal type is web page ?
  data = context.getTextContent("").decode("utf-8")
  data = "".join([handleHtmlPart(part) for part in parseHtml(data)])
  if format == "mhtml":
    mhtml_message["header_dict"]["Subject"] = context.getTitle() or "Untitled"  # XXX translate ?
    mhtml_message["attachment_list"].insert(0, {
      "mime_type": "text/html",
      "encoding": "quopri",
      "add_header_list": [("Content-Location", context.absolute_url())],
      "data": str(data.encode("utf-8")),
    })
    res = context.Base_formatAttachmentListToMIMEMultipartString(**mhtml_message)
    if REQUEST is not None:
      REQUEST.RESPONSE.setHeader("Content-Type", "multipart/related")
      REQUEST.RESPONSE.setHeader("Content-Disposition", 'attachment;filename="%s-%s-%s.mhtml"' % (
        context.getReference("untitled").replace('"', '\\"'),
        context.getVersion("001").replace('"', '\\"'),
        context.getLanguage("en").replace('"', '\\"'),
      ))  # XXX is there a generate filename script ?
      #REQUEST.RESPONSE.write(res)
    return res
  return data

def handleHtmlTag(tag, attrs):
  #if tag == "base": and "href" in attrs:  # should not exist in safe-html
  #  NotImplemented
  if tag == "object":
    for i in range(len(attrs)):
      if attrs[i][0] == "data":
        attrs[i] = attrs[i][0], handleImageSource(attrs[i][1])
  elif tag == "img":
    for i in range(len(attrs)):
      if attrs[i][0] == "src":
        attrs[i] = attrs[i][0], handleImageSource(attrs[i][1])
  elif tag == "link" and anny(attrs, key=lambda a: a[0] == "rel" and a[1] == "stylesheet"):
    for i in range(len(attrs)):
      if attrs[i][0] == "href":
        attrs[i] = attrs[i][0], replaceFromDataUri(handleCssHref(attrs[i][1]), replaceCssUrl)
  elif tag == "style":
    # for style tags, next data will always be the entire text until </style>
    on_next_data[0] = replaceCssUrl
  elif tag == "script":  # and not anny(attrs, key=lambda a: a[0] == "type" and a[1] != "application/javascript" and a[1] != "text/javascript"):
    if allow_script:
      for i in range(len(attrs)):
        if attrs[i][0] == "src":
          attrs[i] = attrs[i][0], handleJsSource(attrs[i][1])
    else:
      # for script tag, next data will always be the entire text until </script>
      on_next_data[0] = lambda d: ""
  else:
    for i in range(len(attrs)):
      if attrs[i][0] == "href" or attrs[i][0] == "src":
        attrs[i] = attrs[i][0], makeHrefAbsolute(attrs[i][1])
  return tag, attrs

on_next_data = [None]
def handleHtmlPart(part):
  tipe = part[0]
  if tipe in ("starttag", "startendtag"):
    tag, attrs = handleHtmlTag(part[1], part[2])
    #tag, attrs = part[1], part[2]
    attrs_str = " ".join(["%s=\"%s\"" % (escapeHtml(k), escapeHtml(v or "")) for k, v in attrs])
    return "<%s%s%s>" % (tag, " " + attrs_str if attrs_str else "", " /" if tipe == "startendtag" else "")
  if tipe == "endtag":
    return "</%s>" % part[1]
  if tipe == "data":
    if on_next_data[0] is None:
      return part[1]
    tmp = on_next_data[0](part[1])  # "on_next_data[0] is not callable (not-callable)" -> if not None, it is callable
    on_next_data[0] = None
    return tmp
  if tipe == "entityref":
    return "&%s;" % part[1]
  if tipe == "charref":
    return "&#%s;" % part[1]
  if tipe == "comment":
    return "<!--%s-->" % part[1]
  if tipe in ("decl", "unknown_decl"):
    return "<!%s>" % part[1]
  if tipe == "pi":
    return "<?%s>" % part[1]

# XXX parse CSS or JS are may be not needed because web pages should not contain such
# a thing. Only the renderer layout should include them. As a result, every CSS and JS
# should be publicly reachable so that any browser (or htmltopdf converters) may get
# them and process them as usual.

def handleCssHref(href):
  return handleHref(href)

def handleJsSource(href):
  return handleHref(href)

def handleHref(href):
  if href.startswith("data:"):
    return href
  try:
    o = traverseHref(href)
  except (KeyError, Unauthorized):
    return handleLinkedData("text/html", "", href)  # XXX return 404 html page
  return handleHrefObject(o, href)

def handleImageSource(src):
  if src.startswith("data:"):
    return src
  try:
    o = traverseHref(src)
  except (KeyError, Unauthorized):
    return handleLinkedData(bad_image_mime_type, bad_image_data, src)
  return handleImageSourceObject(o, src)

def replaceCssUrl(data):
  parts = context.Base_parseCssForUrl(data)
  data = ""
  for part in parts:
    if part[0] == "url":
      url = part[2]
      if url.startswith("data:"):
        data += part[1]
      else:
        data += handleImageSource(part[2])
    else:
      data += part[1]
  return data

def handleImageSourceObject(o, src):
  if hasattr(o, "convert"):
    search = parseUrlSearch(extractUrlSearch(src))
    format_kw = {}
    for k, x in search:
      if k == "format" and x is not None:
        format_kw["format"] = x
      elif k == "display" and x is not None:
        format_kw["display"] = x
    if format_kw:
      mime, data = o.convert(**format_kw)
      return handleLinkedData(mime, data, src)

  return handleHrefObject(o, src, default_mimetype=bad_image_mime_type, default_data=bad_image_data)

def handleHrefObject(o, src, default_mimetype="text/html", default_data=""):  # XXX default_data should return 404 html page
  # handle File portal_skins/folder/file.png
  # XXX handle portal_skin parameter ?
  if hasattr(o, "getContentType"):
    mime = o.getContentType("")
    if mime:
      # XXX if mime is video return 404 ?
      data = getattr(o, "getData", lambda: str(o))() or ""
      if isinstance(data, unicode):
        data = data.encode("utf-8")
      return handleLinkedData(mime, data, src)
    return handleLinkedData(default_mimetype, default_data, src)

  # handle Object.view
  # XXX handle url query parameters !!
  if not hasattr(o, "getPortalType") and callable(o):
    mime, data = "text/html", o()
    if isinstance(data, unicode):
      data = data.encode("utf-8")
    return handleLinkedData(mime, data, src)

  return handleLinkedData(default_mimetype, default_data, src)

bad_image_data_url = ("data:image/png;base64," +  # little image showing cannot load image
                      "iVBORw0KGgoAAAANSUhEUgAAABEAAAATCAIAAAD5x3GmAAACWklEQVQokZWSX0hTcRTHz/" +
                      "3TunMmMyxrQUzEPQSCFEI0fCi0HmSKdsUGg3q2h5I99dj7bE8Nw6cwLDb3kO7JP5m6h0TE" +
                      "CmYQjJYgpaPc7q67+93de04P0zvnQ+CP78Pvdzgfzjnf3+GICE55+NMCACACACKOj49rmv" +
                      "afvNHRUZ4/KkBEjLFQKJRTjXyRTqigUSwWI6JQKGSaJhEREQ8ApmkCgFrif+8bJ7RfMAGA" +
                      "MRYMBsPhMCLWzFPUUdVI1cjjEj0usXLXdLJ6sTCx2jIBAd1otVVe11vPbKT1iqeJRMLKKp" +
                      "fLVYaoChxGEAwDbt0ZsNs4ABAEbiLyoqYOEax/ZyfsYmX4q5iCAABQd1aoen3UGmDt/zod" +
                      "/EWnuJczcgcIABzHu91um81W9YCI8Jga6rirqUV41O9pQqeDR6J6iRvs7VUeDFQZJCKEih" +
                      "DxfINemIioq4ms7GtrwkaH4KovZ2WfujLL1/SGiIgZZSmavj2Veto0GYXO7vzawo7saztX" +
                      "3JF9+bUF6Oyu8YAAtnLvNrJBAOPb7lbkizQyPZuWfX8+LeTaG00NHDe7r8Rmju0oQaawVA" +
                      "Eqga+/Xkc+B1vexDSJzx+AJvEtk1FDEHjLAEXfXdt7ZgEA0H754UjH2GZgWFGR2UVFxc3A" +
                      "sIh4yDDGFjPPdfxhAdea/Y87xpJy//bqnN3b05XK2r0928n55P2+w3kMw9CXmy/AE4u5Fw" +
                      "h89A/tLM9d6urxTr9/G4/74zMfBvt+rsxzRKTruqIojNUsgSRJB+vrqVcv705Fc8ViqVSS" +
                      "JMnpcMz5h/4B1Qxz9NOjZCgAAAAASUVORK5CYII=")  # XXX hardcoded
bad_image_data = b64decode(bad_image_data_url.split(",", 1)[1])  # XXX hardcoded
bad_image_mime_type = "image/png"  # XXX hardcoded

request_protocol = context.REQUEST.SERVER_URL.split(":", 1)[0] + ":"
site_object_dict = {}
for domain, obj in context.ERP5Site_getWebSiteDomainDict().items():
  site_object_dict["//" + domain] = obj
base_url_root_object = portal  # context.getWebSiteValue() if hasattr(context, "getWebSiteValue") else portal
base_url_object = context  # context.getWebSectionValue() if hasattr(context, "getWebSectionValue") else context

def handleLinkedData(mime, data, href):
  if format == "mhtml":
    if href.startswith("https://") or href.startswith("http://"):
      url = href
    elif href.startswith("//"):
      url = request_protocol + href
    elif href.startswith("/"):
      url = base_url_root_object.absolute_url() + href
    else:
      url = base_url_object.absolute_url() + "/" + href
    mhtml_message["attachment_list"].append({
      "mime_type": mime,
      "encoding": "quopri" if mime.startswith("text/") else None,
      "add_header_list": [("Content-Location", url)],
      "data": str(data),
    })
    return url
  else:
    return "data:%s;base64,%s" % (mime, b64encode(data))

def makeHrefAbsolute(href):
  if (href.startswith("https://") or href.startswith("http://") or
      href.startswith("data:") or href.startswith("tel:") or href.startswith("mailto:")):
    return href
  if href.startswith("//"):
    return request_protocol + href
  if href.startswith("/"):
    return base_url_root_object.absolute_url() + href
  return base_url_object.absolute_url() + "/" + href

def traverseHref(url, allow_hash=True):
  url = url.split("?")[0]
  if not allow_hash:
    url = url.split("#")[0]
  if url.startswith("https://") or url.startswith("http://") or url.startswith("//"):  # absolute url possibly on other sites
    # TODO use web site domain properties
    site_url = "/".join(url.split("/")[:3])
    relative_path = url[len(site_url):]
    relative_path = (relative_path[1:] if relative_path[:1] == "/" else relative_path)
    site_object = site_object_dict.get(site_url)
    if site_object is None and url[:1] != "/":
      site_url = "/" + "/".join(url.split("/")[1:3])
      site_object = site_object_dict.get(site_url)
    if site_object is None:
      raise KeyError(relative_path.split("/")[0])
    return site_object.restrictedTraverse(str(relative_path))
  if url.startswith("/"):  # absolute path, relative url
    return base_url_root_object.restrictedTraverse(str(url[1:]))
  # relative url (just use a base url)
  return base_url_object.restrictedTraverse(str(url))

def replaceFromDataUri(data_uri, replacer):
  header, data = data_uri.split(",")
  if "text/css" not in header:
    return data_uri
  is_base64 = False
  if ";base64" in header:
    is_base64 = True
    data = b64decode(data)
  data = replacer(data)
  return "%s,%s" % (header, b64encode(data) if is_base64 else data)

def extractUrlSearch(url):
  url = url.split("?")
  url[0] = ""
  return "?".join(url)

def parseUrlSearch(search):
  if search[:1] == "?":
    search = search[1:]
  result = []
  for part in search.split("&"):
    k = part.split("=")
    v = "=".join(k[1:]) if len(k) else None
    result.append((k[0], v))
  return result

def parseHtml(text):
  return context.Base_parseHtml(text)

def escapeHtml(s):
  return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\"", "&quot;")

def anny(iterable, key=None):
  for i in iterable:
    if key:
      i = key(i)
    if i:
      return True
  return False

return main()
