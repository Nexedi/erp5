## Script (Python) "Folder_copy"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=form_id, uids=[], listbox_uid=[],selection_name=''
##title=
##
selected_uids = context.portal_selections.updateSelectionCheckedUidList(selection_name,listbox_uid,uids)
uids = context.portal_selections.getSelectionCheckedUidsFor(selection_name)
# make sure nothing is checked after
context.portal_selections.setSelectionCheckedUidsFor(selection_name, [])


REQUEST=context.REQUEST
# Do we still needs ids ???
#if REQUEST.has_key('ids'):
#  context.manage_copyObjects(ids=REQUEST['ids'], REQUEST=REQUEST, RESPONSE=REQUEST.RESPONSE)
#  return REQUEST.RESPONSE.redirect(context.absolute_url() + '/' + form_id + '?portal_status_message=Item(s)+Copied.')
#elif REQUEST.has_key('uids'):
if uids != []:
  #context.manage_copyObjects(uids=REQUEST['uids'], REQUEST=REQUEST, RESPONSE=REQUEST.RESPONSE)
  context.manage_copyObjects(uids=uids, REQUEST=REQUEST, RESPONSE=REQUEST.RESPONSE)
  return REQUEST.RESPONSE.redirect(context.absolute_url() + '/' + form_id + '?portal_status_message=Item(s)+Copied.')
else:
  return REQUEST.RESPONSE.redirect(context.absolute_url() + '/' + form_id + '?portal_status_message=Please+select+one+or+more+items+to+copy+first.')
