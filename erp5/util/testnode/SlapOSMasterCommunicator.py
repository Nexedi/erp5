import json
import httplib
import urlparse
import time

TIMEOUT = 30

# TODO: News-> look list to get last news... (and not the first of the list)

class SlapOSMasterCommunicator(object):
  """
  Communication with slapos Master using Hateoas.
  
  collection: collection of data (hosting_subscription, instance, software_release...)
  hosting_subscription: result of a request
  instance(s): instance(s) related to an hosting_subscription

  usage: ex:
    # Try to reuse same communicator, because initilization step may takes a lot of time
    # due to listing of all instances (alive or not) related to the specified slapOS account.
    communicator = SlapOSMasterCommunicator()
    
    # Print news related to 'TestScalability_21423104630420' all instances
    instance_link_list =  communicator._getRelatedInstanceLink('TestScalability_21423104630420')
    for instance_link in instance_link_list:
      news = communicator.getNewsFromInstanceLink(instance_link)
      print news['news']
  """
  def __init__(self, certificate_path, key_path, log,
                     url):
    # Create connection
    api_scheme, api_netloc, api_path, api_query, api_fragment = urlparse.urlsplit(url)
    self.log = log
    self.certificate_path = certificate_path
    self.key_path = key_path
    self.url = url
    self.connection = self._getConnection(self.certificate_path, self.key_path, self.url)
    # Get master
    master_link = {'href':api_path,'type':"application/vnd.slapos.org.hal+json; class=slapos.org.master"}
    master = self._curl(master_link)
    self.person_link = master['_links']['http://slapos.org/reg/me']
    # Get person related to specified key/certificate provided
    person = self._curl(self.person_link)
    self.personnal_collection_link = person['_links']['http://slapos.org/reg/hosting_subscription']
    # Get collection (of hosting subscriptions)
    collection = self._curl(self.personnal_collection_link)
    # XXX: This part may be extremly long (because here no hosting subscriptions
    # has been visited)
    self.hosting_subcriptions_dict = {}
    self.visited_hosting_subcriptions_link_list = []
    self.log("SlapOSMasterCommunicator will read all hosting subscriptions entries, "
             "it may take several time...")
    self._update_hosting_subscription_informations()
    
  def _getConnection(self,certificate_path, key_path, url):
    api_scheme, api_netloc, api_path, api_query, api_fragment = urlparse.urlsplit(url)
    #self.log("HTTPS Connection with: %s, cert=%s, key=%s" %(api_netloc,key_path,certificate_path))
    return httplib.HTTPSConnection(api_netloc, key_file=key_path, cert_file=certificate_path, timeout=TIMEOUT)

  def _curl(self, link):
    """
    'link' must look like : {'href':url,'type':content_type}
    """
    # Set timeout
    import socket
    socket.setdefaulttimeout(1.0*TIMEOUT)
    
    api_scheme, api_netloc, api_path, api_query, api_fragment = urlparse.urlsplit(link['href'])
    max_retry = 10
    # Try to use existing conection
    try:
      self.connection.request(method='GET', url=api_path, headers={'Accept': link['type']}, body="")
      response = self.connection.getresponse()
      return json.loads(response.read())
    # Create and use new connection
    except:
      retry = 0
      # (re)Try several time to use new connection
      while retry < max_retry:
        try:
          self.connection = self._getConnection(self.certificate_path, self.key_path, self.url)
          self.connection.request(method='GET', url=api_path, headers={'Accept': link['type']}, body="")
          response = self.connection.getresponse()
          return json.loads(response.read())
        except:
          self.log("SlapOSMasterCommunicator: Connection failed..")
          retry += 1
          time.sleep(10)
    self.log("SlapOSMasterCommunicator: All connection attempts failed after %d try.." %max_retry)
    raise ValueError("SlapOSMasterCommunicator: Impossible to use connection")
        
  def _update_hosting_subscription_informations(self):
    """
    Add all not already visited hosting_subcription
    # Visit all hosting subscriptions and fill a dict containing all
    # new hosting subscriptions. ( like: {hs1_title:hs1_link, hs2_title:hs2_link, ..} )
    # and a list of visited hosting_subsciption ( like: [hs1_link, hs2_link, ..] )
    """
    collection = self._curl(self.personnal_collection_link)
    # For each hosting_subcription present in the collection
    for hosting_subscription_link in collection['_links']['item']:
      if hosting_subscription_link not in self.visited_hosting_subcriptions_link_list:
        hosting_subscription = self._curl(hosting_subscription_link)
        self.hosting_subcriptions_dict.update({hosting_subscription['title']:hosting_subscription_link})
        self.visited_hosting_subcriptions_link_list.append(hosting_subscription_link)
  
  def _getRelatedInstanceLink(self, hosting_subscription_title):
    """
    Return a list of all related instance_url from an hosting_subscription_title
    """
    # Update informations
    self._update_hosting_subscription_informations()
    # Get specified hosting_subscription
    hosting_subscription_link = self.hosting_subcriptions_dict[hosting_subscription_title]
    hosting_subscription = self._curl(hosting_subscription_link)
    assert(hosting_subscription_title == hosting_subscription['title'])
    # Get instance collection related to this hosting_subscription
    instance_collection_link = hosting_subscription['_links']['http://slapos.org/reg/instance']
    instance_collection = self._curl(instance_collection_link)
    related_instance_link_list = []
    # For each instance present in the collection
    for instance in instance_collection['_links']['item']:
      related_instance_link_list.append(instance)
    return related_instance_link_list

  def getNewsFromInstanceLink(self, instance_link):
      instance = self._curl(instance_link)
      news_link = instance['_links']['http://slapos.org/reg/news']
      return self._curl(news_link)

  def isHostingSubsciptionStatusEqualTo(self, hosting_subscription_title, excepted_news_text):
    """
    Return True if all related instance state are equal to status,
    or False if not or if there is are no related instances.
    """
    related_instance_link_list = _getRelatedInstanceLink(hosting_subscription_title)
    # For each instance present in the collection
    for instance_link in related_instance_link_list:
      news = self.getNewsFromInstanceLink(instance_link)
      if excepted_news_text != news['news'][0]['text']:
        return False
    return len(related_instance_link_list) > 0

  def isInstanceReady(self, instance_link, status):
    """
    Return True if instance status and instance news text ~looks corresponding.
    ( use the matching of 'correctly' and 'Instance' and status )
    """
    # XXX: SlapOS Master doesn't store any "news" about slave instances. Assume true.
    if self._curl(instance_link)['slave']:
      return True
    text = self.getNewsFromInstanceLink(instance_link)['news'][0]['text']
    return ('Instance' in text) and ('correctly' in text) and (status in text)

  # check if provided 'status' = status
  def isHostingSubscriptionReady(self, hosting_subscription_title, status):
    """
    Return True if all instance status and instance news text ~looks corresponding.
    ( use the matching of 'correctly' and 'Instance' and status ).
    """
    instance_link_list = self._getRelatedInstanceLink(hosting_subscription_title)
    for instance_link in instance_link_list:
      if not self.isInstanceReady(instance_link, status):
        return False
    return len(instance_link_list) > 0
    
  def isRegisteredHostingSubscription(self, hosting_subscription_title):
    """
    Return True if the specified hosting_subscription is present on SlapOSMaster
    """
    self._update_hosting_subscription_informations()
    if self.hosting_subcriptions_dict.get(hosting_subscription_title):
      return True
    return False

  def getHostingSubscriptionDict(self):
    """
    Return the dict of hosting subcription.
    """
    return self.hosting_subcriptions_dict

  def getHostingSubscriptionInformationDict(self, title):
    """
    Return a dict with informations about Hosting subscription
    """
    related_instance_link_list = self._getRelatedInstanceLink(title)
    related_instance_link = None
    # Get root instance
    for link in related_instance_link_list:
      instance = self._curl(link)
      if title == instance['title']:
        related_instance_link = link
        break
    # Return information dict
    if related_instance_link:
      related_instance = self._curl(related_instance_link)
      return {
        'title': related_instance['title'],
        'status': related_instance['status'],
        'software_url': related_instance['_links']['http://slapos.org/reg/release'],
        'software_type': related_instance['software_type'],
        'computer_guid': related_instance['sla']['computer_guid']
      }
    else:
      return None
  