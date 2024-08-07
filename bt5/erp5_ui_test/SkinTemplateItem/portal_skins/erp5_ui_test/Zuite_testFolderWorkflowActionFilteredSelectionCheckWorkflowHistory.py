"""
Check the worklfow history of several foo objects
"""

from Products.CMFCore.utils import getToolByName

foo_module = context.getPortalObject().foo_module
wtool = getToolByName(context, 'portal_workflow')

result = 'OK'
error_list = []

def assertEqual(a, b, msg=''):
  if a != b:
    if msg:
      error_list.append(msg)
    else:
      error_list.append('%r != %r' % (a, b))

foo_2 = foo_module['2']
assertEqual(foo_2.getSimulationState(), 'draft',
             'Foo 2 state is %s' % foo_2.getSimulationState())


foo_3 = foo_module['3']
assertEqual(foo_3.getSimulationState(), 'validated',
             'Foo 3 state is %s' % foo_3.getSimulationState())
if not error_list:
  assertEqual(
   wtool.getInfoFor(foo_3, 'history', wf_id='foo_workflow')[-2]['comment'],
   'Comment !')

if error_list:
  result = ''.join(error_list)

container.REQUEST.RESPONSE.setHeader('Content-Type', 'text/html')
return '<html><body><span id="result">%s</span></body></html>' % result
