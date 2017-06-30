import urllib2
import json

github_list_url = "https://api.github.com/repos/Nexedi/awesome-free-software/contents/?ref=master"
openhub_key = "1afe873fd46de2cd79292e00728883e727926a513fbf15f86c62821ba296139b"

def getLatestAnalysesAsXml(url):
  if url == None:
    raise Exception("No url parameter provided.")

  url = url.replace("/languages_summary", ".xml").replace("/p/", "/projects/").replace(" ", "")
  response = urllib2.urlopen(url + "?api_key=" + openhub_key)
  return response.read()

def isValidProfileUrl(url):
  return url is not None and url is not "" and "hub" in url

def getOpenHubUrlList():
  item_list = urllib2.urlopen(github_list_url)
  json_list = json.loads(item_list.read())
  request_list = []

  for element in json_list:
    if ".json" in element.title:
      publisher_profile_request = urllib2.urlopen(element.download_url)
      publisher_profile = json.loads(publisher_profile_request.read())
      publisher_software_list = publisher_profile.free_software_list
      if len(publisher_software_list):
        for software in publisher_software_list:
          software_profile_url = software.source_code_profile
          if isValidProfileUrl(software_profile_url):
            if software_profile_url not in request_list:
              request_list.append(software_profile_url)
  return request_list

def fetchOpenHubProfileListAsXml():
  request_list = getOpenHubUrlList()
  return request_list

    