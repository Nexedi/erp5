request = context.REQUEST

context.log("Should we update?")
context.log("Form data is %s" % request.form.get('cors_origin'))
if not data:
  data = {}
cors_list = data.get('cors', [])
if request.form.get('cors_origin'):
  if not request.form['cors_origin'] in cors_list:
    cors_list.append(request.form['cors_origin'])

origin = context.Base_getRequestHeader("Origin")
if not origin in cors_list:
  cors_list.append(origin)

data['cors'] = cors_list
context.log("data is %s" % data)

return data
