request = container.REQUEST

style = request.get('your_portal_skin',
        request.get('field_your_portal_skin',
                              context.getPreferredReportStyle()))

item_list = [('', '')]

from Products.ERP5.Document.Document import ConversionError

try:
  if style == 'ODS':
    return context.Base_getConversionFormatItemList(
         base_content_type='application/vnd.oasis.opendocument.spreadsheet')
  elif style == 'ODT':
    return context.Base_getConversionFormatItemList(
         base_content_type='application/vnd.oasis.opendocument.text')
except ConversionError:
  # OOo server not here, just return empty list
  pass

return item_list
