#! /usr/bin/env python
#
# this script is looking the file called "path"
# then it try to get every url inside the file
# path.
#
# If you want it to work, you have to create an
# user per each thread, so if you want 3 threads,
# you have to create in zope the following users
# with the following passwords :
# user: user0    password: user0
# user: user1    password: user1
# user: user2    password: user2

from __future__ import print_function
from threading import Thread
from time import sleep
from urllib import addinfourl
from six.moves.urllib.parse import splithost
from six.moves.urllib.parse import splituser
from six.moves.urllib.parse import unquote
from six.moves.urllib.parse import splittype
import string

from six.moves.urllib.request import FancyURLopener
from six.moves.http_cookies import SimpleCookie

def main():
  max_thread = 7  # The number of thread we want by the same time
  file =  open('path','r')
  list_url = []
  while 1:
    line = file.readline()
    if line == '':
      break
    list_url += [line]

  threads = []
  checker = []
  threads = []
  for i in range(0,max_thread):
    checker += [Checker()]
  i = 0
  request_number = 0
  while i < len(list_url):
    sleep(1)
    if len(threads) < max_thread:
      # We must provide an authentication parameter such as __ac_name
      url = '//user%i:user%i@localhost:9673%s?__ac_name=user%s&__ac_password=user%s' % \
                (i,i,list_url[i][:-1],i,i)
      threads += [Thread(target=checker[len(threads)].CheckUrl,kwargs={'url':url})]
      threads[len(threads)-1].start()
      request_number += 1
      i+=1
      print("thread: %i request: %i url: %s" % (i,request_number,url))
    else:
      for t in range(0,max_thread):
        if threads[t].isAlive() == 0:
          url = '//user%i:user%i@localhost:9673%s?__ac_name=user%s&__ac_password=user%s' % \
               (t,t,list_url[i][:-1],t,t)
          threads[t] = Thread(target=checker[t].CheckUrl,kwargs={'url':url})
          threads[t].start()
          i+=1
          request_number += 1
          print("thread: %i request: %i url: %s" % (i,request_number,url))
          break


class URLOpener(FancyURLopener):

    '''Overrides the http implementation so that it sends and receives
    cookie headers.'''

    cookies = SimpleCookie()

    def open_http(self, url, data=None):
        """Use HTTP protocol."""
        import six.moves.http_client
        user_passwd = None
        if type(url) is type(""):
            host, selector = splithost(url)
            if host:
                user_passwd, host = splituser(host)
                host = unquote(host)
            realhost = host
        else:
            host, selector = url
            urltype, rest = splittype(selector)
            url = rest
            user_passwd = None
            if urltype.lower() != 'http':
                realhost = None
            else:
                realhost, rest = splithost(rest)
                if realhost:
                    user_passwd, realhost = splituser(realhost)
                if user_passwd:
                    selector = "%s://%s%s" % (urltype, realhost, rest)
        if not host: raise IOError('http error', 'no host given')
        if user_passwd:
            import base64
            auth = base64.encodebytes(user_passwd).strip()
        else:
            auth = None
        h = six.moves.http_client.HTTP(host)
        if data is not None:
            h.putrequest('POST', selector)
            h.putheader('Content-type', 'application/x-www-form-urlencoded')
            h.putheader('Content-length', '%d' % len(data))
        else:
            h.putrequest('GET', selector)
        for cookie in self.cookies.items():
            h.putheader('Cookie', '%s=%s;' % cookie)

        if auth: h.putheader('Authorization', 'Basic %s' % auth)
        if realhost: h.putheader('Host', realhost)
        for args in self.addheaders: h.putheader(*args)
        h.endheaders()
        if data is not None:
            h.send(data + '\r\n')
        errcode, errmsg, headers = h.getreply()
        if headers and 'set-cookie' in headers:
            cookies = headers.getallmatchingheaders('set-cookie')
            for cookie in cookies: self.cookies.load(cookie)

        fp = h.getfile()
        if errcode == 200:
            return addinfourl(fp, headers, "http:" + url)
        else:
            if data is None:
                return self.http_error(url, fp, errcode, errmsg, headers)
            else:
                return self.http_error(url, fp, errcode, errmsg, headers, data)


class Checker(URLOpener):

  # This seems necessary for exceptions
  type = 'http'

  def CheckUrl(self, url=None):
    try:
      thread = Thread(target=self.SearchUrl,args=(url,))
      thread.start()
      while thread.isAlive():
        sleep(0.5)
      print("Connection to %s went fine" % url)
    except IOError as err:
      (errno, strerror) = err.args
      print("Can't connect to %s because of I/O error(%s): %s" % (url, errno, strerror))

  def SearchUrl(self, url=None):
    try:
      conn = self.open_http(url)
    except IOError as err:
      (errno, strerror) = err.args
      print("Can't connect to %s because of I/O error(%s): %s" % (url, errno, strerror))


  def raise_error(self, error_key, field):
    raise IOError(error_key, field)



if __name__ == '__main__':
    main()

