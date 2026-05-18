from Products.ERP5Type.Utils import str2bytes

# For legacy reasons (dating back Py2), `data` is actually `text_content`
data = str2bytes(data)

return context.PostModule_createHTMLPost(
  source_reference=source_reference,
  data=data,
  follow_up=follow_up,
  predecessor=predecessor,
)
