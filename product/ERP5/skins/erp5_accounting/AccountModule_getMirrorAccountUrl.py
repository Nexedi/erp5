## Script (Python) "AccountModule_getMirrorAccountUrl"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=brain=None, selection=None
##title=
##
index = selection.getIndex()
name = selection.getName()
object = brain.getObject()
object = object.getDestinationValue()
if object is None:
  url = None
else:
  url = object.absolute_url() + '/view?selection_index=%s&selection_name=%s&reset=1' % (index, name)

return url
