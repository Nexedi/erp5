import feedparser, md5, urllib2, socket
  
def getRssDataAsDict(self, url, username=None, password=None):
  result = {}
  translate = self.Base_translateString
  # no url, no feed to read
  if url in ('', None, 'None',):
    return {'title':translate('Please enter a valid Rss or Atom url in the preference form.')}
    
  # use authentication or not?
  handlers = []
  if username is not None and password is not None:
    passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
    passman.add_password(None, url, username, password)
    auth_handler = urllib2.HTTPBasicAuthHandler(passman)
    handlers.append(auth_handler)
  
  # set shorter timeouts and revert default at enf of read  
  default_timeout = socket.getdefaulttimeout()
  socket.setdefaulttimeout(10.0)
  d = feedparser.parse(url, handlers=handlers)  
  socket.setdefaulttimeout(default_timeout)    
    
  if d.bozo and isinstance(d.bozo_exception, urllib2.URLError):
    # we have an URL error
    return {'title':translate('Wrong Rss or Atom url or service temporary down.')}
    
  # http status code checks
  if d.status == 401:
    return {'title': translate('Unauthorized, verify your authentication.')}
  elif d.status == 404:
    return {'title': translate('Page not found.')}
  
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
    entry_dict['md5'] = md5.new(entry['link']).hexdigest() 
    entry_dict['content'] = entry['summary']
    entry_dict['date'] = entry['updated']
    entry_dict['img'] = [x['href'] for x in entry.get('enclosures', [])]
    entry_dict['updated_parsed'] = entry['updated_parsed']
    result['items'].append(entry_dict)
  # sort by date
  result['items'] = sorted(result['items'], key=lambda k: k['updated_parsed'])
  result['items'].reverse()
  return result