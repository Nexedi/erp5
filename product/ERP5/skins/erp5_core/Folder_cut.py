## Script (Python) "Folder_cut"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=form_id,selection_name='',uids=[],listbox_uid=[]
##title=Cut objects from a folder and copy to the clipboard
##
selected_uids = context.portal_selections.updateSelectionCheckedUidList(selection_name,listbox_uid,uids)
uids = context.portal_selections.getSelectionCheckedUidsFor(selection_name)
# make sure nothing is checked after
context.portal_selections.setSelectionCheckedUidsFor(selection_name, [])


REQUEST=context.REQUEST
# do we still need ids ? XXX finish the work here
#if REQUEST.has_key('ids'):
#  context.manage_cutObjects(REQUEST['ids'], REQUEST)
#  return REQUEST.RESPONSE.redirect(context.absolute_url() + '/' + form_id + '/Folder_viewContentList?portal_status_message=Item(s)+Cut.')
#elif REQUEST.has_key('uids'):
if uids != []:
  #context.manage_cutObjects(uids=REQUEST['uids'], REQUEST=REQUEST)
  context.manage_cutObjects(uids=uids, REQUEST=REQUEST)
  return REQUEST.RESPONSE.redirect(context.absolute_url() + '/' + form_id + '?portal_status_message=Item(s)+Cut.')
else:
  return REQUEST.RESPONSE.redirect(context.absolute_url() + '/Folder_viewContentList?portal_status_message=Please+select+one+or+more+items+to+cut+first.')
