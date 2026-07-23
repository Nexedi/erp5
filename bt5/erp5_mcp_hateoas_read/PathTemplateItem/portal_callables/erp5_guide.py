import json
portal = context.getPortalObject()
wpm = portal.web_page_module
STATES = ["shared", "released", "published", "shared_alive", "released_alive", "published_alive"]
EMDASH = unichr(8212)

def _u(x):
  if x is None:
    return u""
  if isinstance(x, str):
    return x.decode("utf-8", "replace")
  return x

def find(ref_query):
  return portal.portal_catalog(
    portal_type="Web Page",
    parent_uid=wpm.getUid(),
    reference=ref_query,
    validation_state=STATES,
    sort_on=(("reference", "ascending"),),
  )

# named entity -> unicode codepoint (ASCII source; built via unichr so no
# source-encoding mojibake). Numeric entities are handled generically below.
_NAMED_CP = {
  u"lt": 60, u"gt": 62, u"amp": 38, u"quot": 34, u"apos": 39, u"nbsp": 32,
  u"mdash": 8212, u"ndash": 8211, u"hellip": 8230, u"rarr": 8594, u"larr": 8592,
  u"agrave": 224, u"eacute": 233, u"egrave": 232, u"ecirc": 234, u"ccedil": 231,
  u"ocirc": 244, u"ouml": 246, u"uuml": 252, u"auml": 228, u"szlig": 223,
  u"times": 215, u"divide": 247, u"deg": 176, u"laquo": 171, u"raquo": 187,
  u"ldquo": 8220, u"rdquo": 8221, u"lsquo": 8216, u"rsquo": 8217, u"copy": 169,
  u"reg": 174, u"trade": 8482, u"euro": 8364, u"pound": 163, u"sect": 167,
  u"middot": 183, u"bull": 8226,
}
NAMED = {}
for _k in _NAMED_CP:
  NAMED[_k] = unichr(_NAMED_CP[_k])

BLOCK = (u"p", u"br", u"div", u"h1", u"h2", u"h3", u"h4", u"h5", u"h6", u"ul",
         u"ol", u"tr", u"pre", u"table", u"thead", u"tbody", u"hr", u"blockquote")

def strip_html(txt):
  txt = _u(txt)
  if not txt:
    return u""
  out = []
  i = 0
  n = len(txt)
  while i < n:
    ch = txt[i]
    if ch == u"<":
      j = txt.find(u">", i)
      if j == -1:
        out.append(ch)
        i += 1
        continue
      tag = txt[i + 1:j].strip().lower()
      opening = not tag.startswith(u"/")
      base = tag.lstrip(u"/").split(u" ")[0]
      if base == u"li" and opening:
        out.append(u"\n- ")
      elif base in (u"td", u"th"):
        out.append(u" | ")
      elif base in BLOCK:
        out.append(u"\n")
      i = j + 1
    elif ch == u"&":
      j = txt.find(u";", i)
      if j != -1 and 0 < (j - i) <= 12:
        ent = txt[i + 1:j]
        rep = None
        if ent.startswith(u"#"):
          try:
            num = ent[1:]
            cp = int(num[1:], 16) if num[:1] in (u"x", u"X") else int(num)
            rep = unichr(cp)
          except Exception:
            rep = None
        else:
          rep = NAMED.get(ent)
        if rep is not None:
          out.append(rep)
          i = j + 1
          continue
      out.append(ch)
      i += 1
    else:
      out.append(ch)
      i += 1
  s = u"".join(out)
  while u"\n\n\n" in s:
    s = s.replace(u"\n\n\n", u"\n\n")
  s = u"\n".join([ln.rstrip() for ln in s.split(u"\n")])
  return s.strip()

def render(brain, name):
  obj = brain.getObject()
  raw = _u(obj.getTextContent() or u"")
  ct = _u(obj.getContentType() or u"").lower()
  content = strip_html(raw) if (u"html" in ct) else raw
  if name and u"@@MCPNAME@@" in content:
    content = content.replace(u"@@MCPNAME@@", name)
  title = _u(obj.getTitle()) or _u(brain.getReference())
  return u"## %s\n\n%s" % (title, content)

t = _u(tutorial) if tutorial is not None else u"list"

if t in (u"", u"list"):
  lines = [u"# ERP5 Tutorial Guides", u""]
  for b in find(u"GUIDE-%"):
    ref = _u(b.getReference())
    obj = b.getObject()
    title = _u(obj.getTitle()) or ref
    desc = _u(obj.getDescription())
    line = u"- **%s** %s %s" % (ref, EMDASH, title)
    if desc:
      line += u" %s %s" % (EMDASH, desc)
    lines.append(line)
  lines.append(u"")
  lines.append(u'Use erp5_guide(tutorial="<reference>") to read a guide, e.g. erp5_guide(tutorial="GUIDE-create_person").')
  return u"\n".join(lines)

ref = t if t.startswith(u"GUIDE-") else u"GUIDE-" + t
for b in find(ref):
  if _u(b.getReference()) == ref:
    return render(b, name)

available = sorted([_u(b.getReference()) for b in find(u"GUIDE-%")])
return json.dumps({u"error": u"Unknown tutorial '%s'" % t,
  u"available_tutorials": available,
  u"hint": u'Use erp5_guide(tutorial="list") to see all guides.'}, ensure_ascii=False)
