#!/usr/bin/python
# coding=UTF-8
import httplib
import urllib,urllib2, os
import cStringIO
import string
import socket
import time
from optparse import OptionParser
from lxml import etree
parser = etree.XMLParser(remove_blank_text=True)

class OptionParser(OptionParser):

    def check_required (self, opt):
      option = self.get_option(opt)

      # Assumes the option's 'default' is set to None!
      if getattr(self.values, option.dest) is None:
          self.error("%s option not supplied" % option)


cmd_parser = OptionParser()
cmd_parser.add_option("--host", help="address of this small server (typically, it's the ip of this computer)")
cmd_parser.add_option("--publication", help="address of the publication (e.g. http://localhost:9080/erp5Serv)")
cmd_parser.add_option("-p", "--port", type="int", help="port used by this server (default is 1234)", default=1234)

(options, args) = cmd_parser.parse_args()

cmd_parser.check_required("--publication")
cmd_parser.check_required("--host")



#CONFIGURATION SECTION

#address of this small server :
#Host = '192.168.242.247'
Host = options.host

#address of the publication :
#publication_url = 'http://localhost:9080/erp5Serv'
publication_url = options.publication

#address use to transmit the message received from the external client :
to_url = publication_url+"/portal_synchronizations/readResponse"

#port of this server :
#Port = 1234
Port = options.port

#address of the this server :
syncml_server_url = 'http://%s:%s' % (Host, Port)

#socket :
sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # reuse the same socket
                                                        # if already open

#END CONFIGURATION SECTION

CRLF = "\015\012"
#in unix, it's the same as \r\n, and on windows, it's the same as \n (\r on mac)
#this octal constant just increase a little this application portability




def nodeToString(node):
  """
  return an xml string corresponding to the node
  """
  return etree.tostring(node, encoding='utf-8')

def xml2wbxml(xml):
  """
  convert xml string to wbxml using a temporary file
  """
  import os

  # XXX we must check at the begining if xml2wbxml is installed
  # it seems that now there is a python biding for this : pywbxml
  f = open('/tmp/xml2wbxml', 'w')
  f.write(xml)
  f.close()
  os.system('/usr/bin/xml2wbxml -o /tmp/xml2wbxml /tmp/xml2wbxml')
  f = open('/tmp/xml2wbxml', 'r')
  wbxml = f.read()
  f.close()
  return wbxml

def wbxml2xml(wbxml):
  """
  convert wbxml string to xml using a temporary file
  """
  import os
  f = open('/tmp/wbxml2xml', 'w')
  f.write(wbxml)
  f.close()
  os.system('/usr/bin/wbxml2xml -o /tmp/wbxml2xml /tmp/wbxml2xml')
  f = open('/tmp/wbxml2xml', 'r')
  xml = f.read()
  f.close()
  return xml

def hexdump(raw=''):
  """
  print raw in readable format without broke the terminal output !
  """
  buf = ""
  line = ""
  start = 0
  done = False
  while not done:
      end = start + 16
      max = len(raw)
      if end > max:
          end = max
          done = True
      chunk = raw[start:end]
      for i in xrange(len(chunk)):
          if i > 0:
              spacing = " "
          else:
              spacing = ""
          buf += "%s%02x" % (spacing, ord(chunk[i]))
      if done:
          for i in xrange(16 - (end % 16)):
              buf += "   "
      buf += "  "
      for c in chunk:
          val = ord(c)
          if val >= 33 and val <= 126:
              buf += c
          else:
              buf += "."
      buf += "\n"
      start += 16
  return buf

def getClientUrl(text):
  """
  find the client url in the text and return it
  """
  document = etree.XML(text, parser=parser)
  # XXX this xpath expression have to be rewrited in a generic way to handle
  # namspace
  client_url = '%s' % document.xpath('string(//SyncHdr/Source/LocURI)')
  # client_url = '%s' % document.xpath('string(//syncml:SyncHdr/syncml:Source/syncml:LocURI)', namespaces={'syncml':'SYNCML:SYNCML1.2'})
  return client_url 

def sendResponse(text, to_url, client_url):
  """
  send the message receive from the external client to erp5 server
  """
  result = None
  opener = urllib2.build_opener()
  urllib2.install_opener(opener)
  to_encode = {}

  print '\nsendResponse...'

  text = wbxml2xml(text)
  text = text.replace(syncml_server_url, publication_url)
  text = text.replace(client_url, syncml_server_url)

  print "text = ",text
  to_encode['text'] = text
  to_encode['sync_id'] = 'Person'
  headers = {'Content-type': 'application/vnd.syncml+xml'}

  encoded = urllib.urlencode(to_encode)
  data=encoded
  request = urllib2.Request(url=to_url, data=data)

  try:
    result = urllib2.urlopen(request).read()
  except socket.error, msg:
    print 'error, url:%s ,data : %s'%(to_url, data)
  except urllib2.URLError, msg:
    print "sendResponse, can't open url : %s" % to_url

  return result


def main():
  sock.bind((Host,Port))
  # we just listen to one and unique connection 
  sock.listen(1)

  text = ''
  # the script stop here until a client connect to him 
  print 'wait for a client connection...'
  client, address = sock.accept()
  print "the host ",address," is connected."
  while 1:
    print('\n\nwait for message ...')
    msg = client.recv(1024) # we receive 1024 caracter max
    if not msg: # if we receive nothing
      break 
    elif not msg.startswith('POST'):
      text = text + msg
      if text.endswith('\x01\x01'):
        client_url = getClientUrl(wbxml2xml(text))
        response = sendResponse(text=text, to_url=to_url, client_url=client_url)
        if response:
          response = response.replace(syncml_server_url, client_url)
          response = response.replace(publication_url, syncml_server_url)
          print "\nresponse = \n",response
          response = xml2wbxml(response)
          print "response send to the phone :\n", hexdump(response)
          date_to_print = time.strftime("%a, %d %b %Y %H:%M:%S GMT")
          head = CRLF.join((
              "HTTP/1.1 200 OK",
              "Date: %s GMT" % date_to_print,
              "Server: myPythonServer",
              "Content-Length: %s" % len(response),
              "Content-Type: application/vnd.syncml+wbxml",
              ))
          message = "%s%s%s%s" % (head, CRLF, CRLF, response)
          #here it's necessary to have 2 CRLF, for more details 
          #see http://www.w3.org/Protocols/rfc2616/rfc2616.html
          client.send(message)
        text=''
    else:
      print "this message is a POST header."
  sock.close()

if __name__ == "__main__":
  main()
