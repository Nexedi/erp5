def textToP(s):
  return "<p>" + s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("  ", " &nbsp;").replace("\n", "<br/>") + "</p>"

for key in ("text_content", "data"):
  __traceback_info__ = key
  if key in post_edit_kw:
    post_edit_kw[key] = textToP(post_edit_kw[key])

return context.PostModule_createHTMLPost(**post_edit_kw)
