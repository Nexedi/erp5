from Products.PythonScripts.standard import html_quote

result = ''
error_message = None
try:
  result = context.asStrippedHTML()
  if result:
    return result
except Exception as e:
  from erp5.component.module.Log import log
  log("asStrippedHTML", str(e))
  error_message = "%s %s" % (context.Base_translateString("Preview Error:"),
                              str(e))

if error_message is not None:
  return '<div class="error">%s</div>' % html_quote(error_message)

return result
