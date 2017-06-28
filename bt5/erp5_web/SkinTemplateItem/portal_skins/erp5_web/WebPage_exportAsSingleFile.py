"""
Export the web page and its components to a single (m)html file.

see Base_convertHtmlToSingleFile for documentation
"""
# ERP5 web uses format= argument, which is also a python builtin
# pylint: disable=redefined-builtin
data = context.Base_convertHtmlToSingleFile(
  context.getTextContent(""),
  allow_script=allow_script,
  format=format,
  base_url=base_url,
  site_object_dict=site_object_dict,
  title=context.getTitle() or "Untitled",
)
if REQUEST is not None:
  if format == "mhtml":
    REQUEST.RESPONSE.setHeader("Content-Type", "multipart/related")
    REQUEST.RESPONSE.setHeader("Content-Disposition", 'attachment;filename="%s-%s-%s.mhtml"' % (
      context.getReference("untitled").replace('"', '\\"'),
      context.getVersion("001").replace('"', '\\"'),
      context.getLanguage("en").replace('"', '\\"'),
    ))
  else:
    REQUEST.RESPONSE.setHeader("Content-Type", "text/html")
    REQUEST.RESPONSE.setHeader("Content-Disposition", 'attachment;filename="%s-%s-%s.html"' % (
      context.getReference("untitled").replace('"', '\\"'),
      context.getVersion("001").replace('"', '\\"'),
      context.getLanguage("en").replace('"', '\\"'),
    ))
return data
