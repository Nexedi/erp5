software_product = sci['object']
request = container.REQUEST

args = str(sci['kwargs']['workflow_method_args'])
software_product.setReference(args)


#if sci['kwargs']['workflow_method_args'] == ('before commit',):
#  foo.setShortTitle("set by interaction workflow")

#if sci['kwargs']['workflow_method_args'] == ('Custom Message',):
#  request.set('portal_status_message', 'Custom Message.')
#  request.set('portal_status_level', 'error')
