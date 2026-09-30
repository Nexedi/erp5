from Products.PythonScripts.standard import html_quote
return context.asStrippedHTML() or html_quote(context.getTitle())
