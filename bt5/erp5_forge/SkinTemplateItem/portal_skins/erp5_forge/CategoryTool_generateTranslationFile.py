"""Return a po file from a spreadsheet of categories."""
from Products.ERP5Type.Document import newTempBase

# Initialise some general variables
detailed_report_result = []
detailed_report_append = detailed_report_result.append
translation_dict = {}
translated_attributes_list = ["title", "description", "short_title"]
import_filename = getattr(import_file, 'filename', '?')
request = container.REQUEST
response = request.RESPONSE

if import_filename=='':
  raise ValueError("You must upload a file")

def addReportLine(error, category, message):
  report_line = newTempBase(context, 'item')
  report_line.edit(field_type=error, field_category=category, field_message=message)    
  detailed_report_append(report_line)

def invalid_category_spreadsheet_handler(message):
  # action taken when an invalid spreadsheet is provided.
  # we *raise* a Redirect, because we don't want the transaction to succeed
  # note, we could make a dialog parameter to allow import invalid spreadsheet:
  context.Base_redirect('view', keep_items={'portal_status_message':message},
                        abort_transaction=True)

category_list_mapping = context.Base_getCategoriesSpreadSheetMapping(import_file,
                                    invalid_spreadsheet_error_handler=invalid_category_spreadsheet_handler)

assert 'error_list' not in category_list_mapping


#Process on each category
for category_list in category_list_mapping.values():
  for category in category_list:
    #Take only needed attributes
    for attribute in translated_attributes_list:
      #Test attribute exist
      if attribute in category and translation_prefix+attribute in category:
        initial_value = category.get(attribute,'').strip().replace('"',"'")
        if initial_value != '':
          translate_value = category.get(translation_prefix+attribute,'').strip().replace('"',"'")
          if translate_value != '':
            if initial_value in translation_dict:
              #Test any duplicate  translation ('car' can't be translated to 'voiture' and 'auto', 
              #user should be choice 'voiture' or 'car')
              if translation_dict[initial_value] != translate_value: 
                message = "'%s' can't be translated by '%s'. It's already translated by '%s'" % (initial_value, translate_value, translation_dict[initial_value])
                addReportLine(error="Duplicate",category=category['path'], message=message)
            else:
              translation_dict[initial_value] = translate_value
          else:
            message = "No translation for attribute " + attribute
            addReportLine(error="No translation",category=category['path'], message=message)  

if len(translation_dict) == 0:
  message = "Empty File"
  addReportLine(error="No Results",category="General", message=message)

if error_report and len(detailed_report_result) > 0:
  context.REQUEST.other['category_import_report'] = detailed_report_result
  return context.CategoryTool_viewImportReport()

#No error, we build the file
po_data = ""
for msgid, msgstr in translation_dict.items():
  po_data += 'msgid "%s"\nmsgstr "%s"\n\n' % (msgid, msgstr)

filename = "%s%s.po" % (translation_prefix,"".join(import_filename.split('.')[:-1]))
document = context.portal_contributions.newContent(data=po_data,
                                                  temp_object=1,
                                                  filename=filename)

response.setHeader('Content-disposition', 'attachment; filename="%s"' % filename)
return document.index_html(request, response, None)
