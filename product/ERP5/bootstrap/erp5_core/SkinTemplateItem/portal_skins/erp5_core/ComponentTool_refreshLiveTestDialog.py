request = context.REQUEST
if request.get('form', None) is not None:
  context.REQUEST['form']['field_your_text_output']=""
  context.REQUEST['form']['text_output']=""
return context.ComponentTool_viewLiveTestDialog(
  text_output="")
