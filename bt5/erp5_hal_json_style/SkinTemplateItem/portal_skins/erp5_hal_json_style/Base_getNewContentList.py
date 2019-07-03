translate = context.Base_translateString

result_list = [(translate(x), 'add %s' % x) for x in context.getVisibleAllowedContentTypeList()]

# Template
document_template_list = context.getDocumentTemplateList()
if document_template_list:
  result_list.append(('-- %s --' % translate('Templates'), None))
  for document_template in document_template_list:
    result_list.append((document_template.getTitle(), 'template %s' % document_template.getRelativeUrl()))

return result_list
