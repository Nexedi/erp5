import commands
kw['portal_type'] = ('PDF')
result_list = [x.getObject() for x in context.portal_catalog(**kw)]

result=[]
for x in result_list:
  if x.getParentValue() == context:
    result.append(x)
result_list = result




# get the merged pdf
merged_pdf = context.mergePDF(result_list)


request = context.REQUEST
response = request.RESPONSE

filename = '%s.%s' % (('all_attached_files', 'pdf'))
response.setHeader('Content-disposition', 'attachment; filename="%s"' % filename)
response.setHeader('Content-type', 'appplication/pdf')

return merged_pdf
