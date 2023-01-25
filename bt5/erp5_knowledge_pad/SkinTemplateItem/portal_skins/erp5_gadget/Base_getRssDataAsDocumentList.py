from Products.ERP5Type.Document import newTempBase
from Products.ERP5Type.Cache import CachingMethod

request = context.REQUEST
box_relative_url = kw.get('box_relative_url')
selection_name = kw.get('list_selection_name')
portal_selection = getattr(context,'portal_selections')
selection = portal_selection.getSelectionFor(selection_name)

error_mapping_dict = {-1: 'Please enter a valid Rss or Atom url in the preference form.',
                      -2: 'Wrong Rss or Atom url or service temporary down.',
                      -3: 'Unauthorized, verify your authentication.',
                      -4: 'Page not found.',
                      -5: 'Mismatched RSS feed.'}

if box_relative_url:
  box = context.restrictedTraverse(box_relative_url)
  preferences = box.KnowledgeBox_getDefaultPreferencesDict()
else:
  preferences = {}

feed_url = str(preferences.get('preferred_rss_feed',''))
username = str(preferences.get('preferred_username',''))
password = str(preferences.get('preferred_password',''))

Base_getRssDataAsDict = CachingMethod(context.Base_getRssDataAsDict,
                                     (feed_url, username, password), cache_factory='erp5_ui_short')
results = Base_getRssDataAsDict(context, url = feed_url, username = username, password = password)

md5_list = []
message_list = []
items = results.get('items', [])
status = results.get('status', 0)

context.REQUEST.set('rss_status', status)
if status < 0:
  # some error occured show message to user
  request.set('rss_title', context.Base_translateString(error_mapping_dict[status]))
  return []
else:
  # all good
  rss_title = results.get('title','')
  rss_logo = results.get('logo', None)
  if items is not None:
    rss_title = '%s (%s)' %(rss_title, len(items))
  if rss_logo not in ('', None):
    request.set('rss_logo', rss_logo)
  request.set('rss_link', results.get('link',None))
  request.set('rss_gadget_title', rss_title)

for result in items:
  md5_list.append(result['md5'])
  date = context.Base_getDiffBetweenDateAndNow(result.get('date',None))
  message = newTempBase(context, 'item')
  message.edit(field_title = result.get('title','No title'),
            field_date = date,
            field_author = result['author'],
            field_content = result.get('content','No content'),
            field_img = result.get('img',''),
            field_others_links = result.get('other_links',''),
            field_link = result.get('link',''),
            field_md5 = result.get('md5',''))
  message_list.append(message)

return message_list
