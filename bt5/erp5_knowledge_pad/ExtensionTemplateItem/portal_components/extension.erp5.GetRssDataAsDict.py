import feedparser, urllib2, socket
from hashlib import md5

def getRssDataAsDict(context, url, username=None, password=None):
  result = {}
  translate = context.Base_translateString
  # no url, no feed to read
  if url in ('', None, 'None',):
    # no URL
    return {'status':-1}
    
  # use authentication or not?
  handlers = []
  if username is not None and password is not None:
    passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
    passman.add_password(None, url, username, password)
    auth_handler = urllib2.HTTPBasicAuthHandler(passman)
    handlers.append(auth_handler)

  # set shorter timeouts and revert default at enf of read  
  default_timeout = socket.getdefaulttimeout()
  socket.setdefaulttimeout(60.0)
  try:
    d = feedparser.parse(url, handlers=handlers)
  finally:
    socket.setdefaulttimeout(default_timeout)

  if d.bozo and isinstance(d.bozo_exception, urllib2.URLError):
    # we have an URL error
    return {'status':-2}
  elif d.bozo:
    # some bozo exceptions can be ignored
    if not isinstance(d.bozo_exception, (
        feedparser.CharacterEncodingOverride,
        feedparser.NonXMLContentType,
      )):
      return {'status': -5}
  if d.status == 401:
    return {'status':-3}
  elif d.status == 404:
    return {'status':-4}

  result['items'] = []
  # some feeds may not provide logo
  if d.feed.get('image', None) is not None:
    result['logo'] = d.feed.image['href']
  result['title'] = d.feed.title
  result['link'] = d.feed.link
  for entry in d.entries:
    entry_dict = {}
    entry_dict['title'] = entry['title']
    entry_dict['link'] = entry['link']
    entry_dict['other_links'] = [x['href'] for x in entry['links']]
    entry_dict['md5'] = md5(entry['link']).hexdigest()
    entry_dict['content'] = entry.get('summary', '')
    entry_dict['date'] = entry.get('updated', None)
    entry_dict['img'] = [x['href'] for x in entry.get('enclosures', [])]
    entry_dict['updated_parsed'] = entry.get('updated_parsed', None)
    result['items'].append(entry_dict)
  # sort by date
  result['items'] = sorted(result['items'], key=lambda k: k['updated_parsed'])
  result['items'].reverse()
  result['status'] = 0
  return result