## Script (Python) "Folder_search"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=form_id=''
##title=Paste objects to a folder from the clipboard
##
REQUEST=context.REQUEST
return getattr(context,form_id)(REQUEST)
