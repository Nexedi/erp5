## Script (Python) "ActivityTool_postError"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=error
##title=
##
context.portal_activities.setTitle(context.portal_activities.title + '\p' + error)
