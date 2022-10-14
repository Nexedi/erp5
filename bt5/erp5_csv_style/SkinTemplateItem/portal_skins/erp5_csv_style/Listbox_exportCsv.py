# export_only : allow to disable the uid column and the id of columns
import six
result = ''
request = context.REQUEST

translate = context.getPortalObject().Localizer.erp5_ui.gettext

listboxline_list = context.get_value('default', render_format='list', REQUEST=request)

def encode(value):
  if isinstance(value, bool):
    return '"%s"' % value
  if isinstance(value, six.integer_types + (float,)):
    return str(value)
  else:
    if isinstance(value, str):
      value = value.decode('utf-8')
    else:
      value = str(value)
    return '"%s"' % value.replace('"', '""')

for listboxline in listboxline_list:
  if listboxline.isTitleLine():
    line_result = ''
    line_result2 = ''

    if not export_only:
      listboxline.setListboxLineDisplayListMode(['uid'])  #XXX do not display uid column

    for column_item in listboxline.getColumnItemList():

      column_id = column_item[0]
      column_property = column_item[1]

      if column_id is not None:
        line_result += encode(column_id)
      line_result += str(',')

      if column_property is not None:
        line_result2 += encode(column_property)
      line_result2 += str(',')

    if len(line_result) > 1:
      line_result = line_result[:-1]

    if len(line_result2) > 1:
      line_result2 = line_result2[:-1]

    if not export_only:
      result += line_result+'\n' #XXX do not display id
    result += line_result2+'\n'




  if listboxline.isDataLine():
    line_result = ''

    if not export_only:
      listboxline.setListboxLineDisplayListMode(['uid'])  #XXX do not display uid column

    for column_property in listboxline.getColumnPropertyList():

      if column_property is not None:
        line_result += encode(column_property)
      line_result += str(',')

    if len(line_result) > 1:
      line_result = line_result[:-1]

    result += line_result+'\n'

return result
