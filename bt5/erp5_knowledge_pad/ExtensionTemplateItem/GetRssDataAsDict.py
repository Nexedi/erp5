from urllib2 import HTTPPasswordMgrWithDefaultRealm, HTTPBasicAuthHandler, \
     build_opener, install_opener, urlopen, HTTPError
from xml.dom.minidom import parse
import md5
from HTMLParser import HTMLParser

def getRssDataAsDict(url, username, password):
  passman = HTTPPasswordMgrWithDefaultRealm()
  passman.add_password(None, url, username, password)
  auth_handler = HTTPBasicAuthHandler(passman)
  opener = build_opener(auth_handler)
  install_opener(opener)
  try:
    file = urlopen(url)
  except IOError , e:
    return {'title': 'Connection problem, please retry later.'}
  except ValueError , e:
   return {'title': 'Please enter a valid Rss or Atom url in the preference form.' }
  except HTTPError , e:
    if hasattr(e, 'code'):
      if e.code == 401:
        return {'title': 'Unauthorized, verify your authentication.' }
      if e.code == 404:
        return {'title': 'Page not found.' }
  except :
    return {'title': 'Fetching Rss failed.' }
  try:
    xmlDoc = parse(file).documentElement
  except :
    return {'title': 'Parsing RSS failed.' }
  if(xmlDoc.tagName.startswith('rss') or xmlDoc.tagName.startswith('rdf') ):
    feed_data = {}
    RSSTitle = None
    if (xmlDoc.getElementsByTagName('title') and xmlDoc.getElementsByTagName('title')[0].parentNode.tagName != 'item'):
      feed_data['title'] = xmlDoc.getElementsByTagName('title')[0].firstChild.nodeValue
    if (xmlDoc.getElementsByTagName('image') and xmlDoc.getElementsByTagName('image')[0].parentNode.tagName != 'item'):
      logo = xmlDoc.getElementsByTagName('image')[0]
      if (logo.getElementsByTagName('url')):
        feed_data['logo'] = logo.getElementsByTagName('url')[0].firstChild.nodeValue
      elif(logo.getElementsByTagName('rdf:resource')):
        feed_data['logo'] = logo.getElementsByTagName('rdf:resource')[0].firstChild.nodeValue
    if (xmlDoc.getElementsByTagName('link') and xmlDoc.getElementsByTagName('link')[0].parentNode.tagName != 'item'):
      feed_data['link'] = xmlDoc.getElementsByTagName('link')[0].firstChild.nodeValue
    item_list = xmlDoc.getElementsByTagName('item')
    feed_data['items'] = []
    for item in item_list:
      message = {}
      message['other_links'] = []
      message['img'] = []
      if(item.getElementsByTagName('title') and item.getElementsByTagName('title')[0].firstChild):
        message['title'] = item.getElementsByTagName('title')[0].firstChild.nodeValue
      if(item.getElementsByTagName('link') and item.getElementsByTagName('link')[0].firstChild):
        message['link'] = item.getElementsByTagName('link')[0].firstChild.nodeValue
      if(item.getElementsByTagName('description') and item.getElementsByTagName('description')[0].firstChild):
        message['content'] = cleanHTML(item.getElementsByTagName('description')[0].firstChild.nodeValue)
      if (item.getElementsByTagName('pubDate') and item.getElementsByTagName('pubDate')[0].firstChild):
        message['date'] = item.getElementsByTagName('pubDate')[0].firstChild.nodeValue
      elif(item.getElementsByTagName('dc:date') and item.getElementsByTagName('dc:date')[0].firstChild):
        message['date'] = item.getElementsByTagName('dc:date')[0].firstChild.nodeValue
      if (item.getElementsByTagName('enclosure')):
        for enclosure in item.getElementsByTagName('enclosure'):
          if (str(enclosure.attributes['type'].nodeValue).find('image') != -1):
            message['img'].append(enclosure.attributes['url'].nodeValue)
          else:
            if (enclosure.attributes.has_key('title')):
              message['other_links'].append('<a href="'+enclosure.attributes['url'].nodeValue+'"target="_blank">'+enclosure.attributes['url'].nodeValue+'</a>')
            else:
              message['other_links'].append('<a href="'+enclosure.attributes['url'].nodeValue+'"target="_blank">'+enclosure.attributes['title'].nodeValue+'</a>')
      message['md5'] = md5.new(str(message)).hexdigest()
      feed_data['items'].append(message)
  elif(xmlDoc.tagName == 'feed'):
    feed_data = {}
    feedTitle = None
    if (xmlDoc.getElementsByTagName('title') and xmlDoc.getElementsByTagName('title')[0].parentNode.tagName != 'entry'):
      feed_data['title'] = xmlDoc.getElementsByTagName('title')[0].firstChild.nodeValue
    if (xmlDoc.getElementsByTagName('icon') and xmlDoc.getElementsByTagName('icon')[0].parentNode.tagName != 'entry'):
      feed_data['logo'] = xmlDoc.getElementsByTagName('icon')[0].firstChild.nodeValue
    item_list = xmlDoc.getElementsByTagName('entry')
    feed_data['items'] = []
    for item in item_list:
      message = {}
      if(item.getElementsByTagName('title') and item.getElementsByTagName('title')[0].firstChild):
        message['title'] = item.getElementsByTagName('title')[0].firstChild.nodeValue
      message['other_links'] = []
      message['img'] = []
      for link in item.getElementsByTagName('link'):
        if (link.attributes.has_key('rel') and link.attributes.get('rel').nodeValue == 'alternate'):
          message['link'] = link.attributes['href'].nodeValue
        elif (link.attributes.has_key('type') and link.attributes.get('type').nodeValue.find('image') != -1):
          message['img'].append(link.attributes['href'].nodeValue)
        else:
          if (link.attributes.has_key('title')):
            message['other_links'].append('<a href="'+link.attributes['href'].nodeValue+'" target="_blank">'+link.attributes['title'].nodeValue+'</a>')
          else:
            message['other_links'].append('<a href="'+link.attributes['href'].nodeValue+'"target="_blank">'+link.attributes['href'].nodeValue+'</a>')
      if (item.getElementsByTagName('content') and item.getElementsByTagName('content')[0].firstChild):
        message['content'] = stringConstructor(item.getElementsByTagName('content')[0])
      elif (item.getElementsByTagName('summary') and item.getElementsByTagName('summary')[0].firstChild):
        message['content'] = stringConstructor(item.getElementsByTagName('summary')[0])
      if (item.getElementsByTagName('updated') and item.getElementsByTagName('updated')[0].firstChild):
        message['date'] = item.getElementsByTagName('updated')[0].firstChild.nodeValue
      elif (item.getElementsByTagName('modified') and item.getElementsByTagName('modified')[0].firstChild):
        message['date'] = item.getElementsByTagName('modified')[0].firstChild.nodeValue
      message['md5'] = md5.new(str(message)).hexdigest()
      feed_data['items'].append(message)
  else:
    return {'title': 'This reader can\'t read this feed'}
  return feed_data


class HTMLCleaner(HTMLParser):
  def __init__(self):
    HTMLParser.__init__(self)
    self.html = ''
    self.script = 0
  def handle_starttag(self, tag, attrs):
    if tag !='script' and tag !='input' and tag !='button' :
      self.html += '<'+tag+' '
      for attr in attrs:
        if not attr[0].startswith('on'):
          self.html += attr[0]+'=' +attr[1]+' '
      if tag=='a':
        self.html += 'target="_blank" '
      self.html += '>'
    else:
      self.script = 1
  def handle_data(self, data):
    if not self.script:
      self.html += data
  def handle_charref(self, name):
    self.html += '&#'+name+';'
  def handle_entityref(self, name):
    self.html += '&'+name+';'
  def handle_endtag(self, tag):
    if tag !='script' and tag !='input' and tag !='button' :
      self.html += '</'+tag+'>'
    else:
      self.script = 0
  def handle_startendtag(self, tag, attrs):
    if tag !='script' and tag !='input' and tag !='button' :
      self.html += '<'+tag+' '
      for attr in attrs:
        if not attr[0].startswith('on'):
          self.html += attr[0]+'=' +attr[1]+' '
      self.html += '/>'

def cleanHTML(string):
  html = ''
  parser= HTMLCleaner()
  parser.feed(string)
  return parser.html

def stringConstructor(domItem):
  string = ''
  for item in domItem.childNodes:
    if item.nodeType == 3:
      string = string + item.nodeValue
    elif item.nodeType == 1 and item.tagName != 'script' and item.tagName != 'input' and item.tagName != 'button':
      string = string + '<' + item.tagName + ' '
      if item.attributes:
        for att in item.attributes.items():
          if(not att[0].startswith('on')):
            string = string + att[0] + '=' + att[1] + ' '
      if item.tagName == 'a':
        string = string + 'target="_blank" '
      string = string + '>'
      string = string + stringConstructor(item)
      string = string + '</' + item.tagName + '>'
  return string
