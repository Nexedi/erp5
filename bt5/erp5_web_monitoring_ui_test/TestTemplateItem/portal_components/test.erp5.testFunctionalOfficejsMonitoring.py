##############################################################################
#
# Copyright (c) 2011 Nexedi SARL and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
from __future__ import print_function
import unittest

from Products.ERP5Type.tests.ERP5TypeFunctionalTestCase import ERP5TypeFunctionalTestCase
from six.moves.SimpleHTTPServer import SimpleHTTPRequestHandler
from threading import Thread
from datetime import datetime

import six.moves.socketserver
import tempfile
import shutil
import time
import os
import json

class CustomHTTPRequestHandler(SimpleHTTPRequestHandler):
  def end_headers(self):
    self.send_my_headers()

    SimpleHTTPRequestHandler.end_headers(self)

  def send_respond(self, code=200, content_type='text/html'):
    self.send_response(code)
    self.send_header("Content-type", content_type)
    self.end_headers()

  def send_my_headers(self):
    self.send_header("Access-Control-Allow-Origin", "*")
    self.send_header("Access-Control-Allow-Methods", "HEAD, OPTIONS, GET, POST")
    self.send_header("Access-Control-Allow-Headers", "Overwrite, Destination, Content-Type, Depth, User-Agent, X-File-Size, X-Requested-With, If-Modified-Since, X-File-Name, Cache-Control, Authorization")

  def do_GET(self):
    SimpleHTTPRequestHandler.do_GET(self)

  def do_OPTIONS(self):
    self.send_respond(200)

  def do_HEAD(self):
    self.send_respond()

class TestZeleniumCore(ERP5TypeFunctionalTestCase):
  foreground = 0
  run_only = "web_monitoring_ui_zuite"
  base_url = 'http://localhost:5378'
  instance_list = []
  httpd = None
  httpd_is_alive = False
  root_title = "TEST Instance Tree"

  def start_httpd_server(self, root_folder):
    self.httpd = six.moves.socketserver.TCPServer(('localhost', 5378), CustomHTTPRequestHandler)
    self.httpd.timeout = 2
    os.chdir(root_folder)
    #self.httpd.serve_forever()
    while self.httpd_is_alive:
      self.httpd.handle_request()

    self.httpd = None

  def afterSetUp(self):
    ERP5TypeFunctionalTestCase.afterSetUp(self)

    self.http_root_dir = tempfile.mkdtemp()
    print("Serving files on http from %r" % self.http_root_dir)

    self.generateMonitoringInstanceTree()
    self.httpd_is_alive = True
    thread = Thread(target=self.start_httpd_server, args=(self.http_root_dir,))
    thread.daemon = True
    thread.start()

  def beforeTearDown(self):
    self.httpd_is_alive = False
    # Wait for httpd server stop
    time.sleep(3)
    if os.path.exists(self.http_root_dir):
      shutil.rmtree(self.http_root_dir)
    ERP5TypeFunctionalTestCase.beforeTearDown(self)

  def getBusinessTemplateList(self):
    return (
      'erp5_ui_test',
      'erp5_web_monitoring',
      'erp5_ui_test_core',
      )

  def generateInstanceDirectory(self, name):
    root_dir = os.path.join(self.http_root_dir, name)
    public_http_dir = os.path.join(root_dir, 'public')
    private_http_dir = os.path.join(root_dir, 'private')
    webdav_http_dir = os.path.join(root_dir, 'share')
    os.mkdir(root_dir)
    os.mkdir(public_http_dir)
    os.mkdir(private_http_dir)
    os.mkdir(webdav_http_dir)

    webdav_public_dir = os.path.join(webdav_http_dir, 'public')
    webdav_private_dir = os.path.join(webdav_http_dir, 'private')

    os.symlink(public_http_dir, webdav_public_dir)
    os.symlink(private_http_dir, webdav_private_dir)

    instance = dict(
      title=name,
      public_dir=public_http_dir,
      private_dir=private_http_dir,
      url=self.base_url + '/' + name
    )
    self.instance_list.append(instance)
    return instance

  def generatePromiseResult(self, instance, status='OK', amount=1):
    now_time = time.time()
    start_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

    for i in range(0, amount):
      title = 'test_promise_%s' % i
      result_dict = {
        "status": status,
        "change-time": now_time,
        "instance_tree": self.root_title,
        "title": title,
        "start-date": start_date,
        "instance": instance['title'],
        "_links": {
          "monitor": {
            "href": "%s/share/private/" % instance['url']
          }
        },
        "message": "Test Promise ran with status %s" % status,
        "type": "status"
      }
      with open(os.path.join(instance['public_dir'], '%s.json' % title), 'w') as f:
        f.write(json.dumps(result_dict))

  def generateOPMLFile(self, instance, sub_instance_list=[]):
    creation_date = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")
    opml_content = """<?xml version="1.0" encoding="UTF-8"?>
<!-- OPML generated by SlapOS -->
<opml version="1.1">
	<head>
		<title>%(root_title)s</title>
		<dateCreated>%(creation_date)s</dateCreated>
		<dateModified>%(creation_date)s</dateModified>
	</head>
	<body>
	  <outline text="Monitoring RSS Feed list">""" % {
	    "root_title": self.root_title,
	    "creation_date": creation_date
	  }
    opml_content += '\n<outline text="%(title)s" title="%(title)s" type="rss" version="RSS" htmlUrl="%(html_url)s" xmlUrl="%(html_url)s" url="%(global_url)s" />' % {
	    "title": instance['title'],
	    "html_url": '%s/public/feed' % instance['url'],
	    "global_url": "%s/share/private/" % instance['url'],
    }
    for sub_instance in sub_instance_list:
      opml_content += '\n<outline text="%(title)s" title="%(title)s" type="rss" version="RSS" htmlUrl="%(html_url)s" xmlUrl="%(html_url)s" url="%(global_url)s" />' % {
  	    "title": sub_instance['title'],
  	    "html_url": '%s/public/feed' % sub_instance['url'],
  	    "global_url": "%s/share/private/" % sub_instance['url'],
      }

    opml_content += """	  </outline>
  </body>
</opml>"""

    with open(os.path.join(instance['public_dir'], 'feeds'), 'w') as f:
      f.write(opml_content)


  def generateInstanceRssFeed(self, instance):
    promise_list = [name.rstrip('.json')
      for name in os.listdir(instance['public_dir']) if name.endswith('.json')]
    rss_content = """<rss version="2.0">
<channel>
<title>%(instance)s</title>
<link>%(link)s</link>
<description>%(description)s</description>
<lastBuildDate>%(date)s</lastBuildDate>
<docs>http://blogs.law.harvard.edu/tech/rss</docs>""" % {
      "description": self.root_title,
      "link": '%s/public/feed' % instance['url'],
      "instance": instance['title'],
      "date": datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")
    }

    for promise in promise_list:
      item = """<item>
<title>%(title)s</title>
<link>
%(base_url)s/share/private/
</link>
<description>%(description)s</description>
<category>%(status)s</category>
<comments/>
<guid isPermaLink="false">VU5LTk9XTiwgc2xhcHJ1bm5l%(id)s==</guid>
<pubDate>%(date)s</pubDate>
<source url="%(base_url)s/share/public/">%(title)s</source>
</item>""" % {
        "base_url": instance['url'],
        "title": promise,
        "status": "OK",
        "description": "description of %s" % promise,
        "id": int(time.time()),
        "date": datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")
      }

      rss_content += item

    rss_content += """</channel></rss>"""

    with open(os.path.join(instance['public_dir'], 'feed'), 'w') as f:
      f.write(rss_content.replace('\n', ''))

  def generateMonitoringStatusFile(self, instance, status="OK"):
    monitor_dict = {
        "status": status,
        "state": {
          "warning": 0,
          "success": 3,
          "error": 0
        },
        "title": instance['title'],
        "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "data": {
          "process_state": "monitor_process_resource.status",
          "io_resource": "monitor_resource_io.data",
          "state": "monitor_state.data",
          "memory_resource": "monitor_resource_memory.data",
          "process_resource": "monitor_resource_process.data",
          "monitor_process_state": "monitor_resource.status"
        },
        "hosting-title": self.root_title,
        "type": "global",
        "_embedded": {
          "instance": {
            "partition": "slappart1",
            "ipv6": "2001:67c:1254:e:c4::c748",
            "computer": "slaprunner",
            "ipv4": "10.0.165.37",
            "software-release": "http://xxx.yyy.zz/asoftware/software.cfg",
            "software-type": "pull-backup"
          }
        },
        "parameters": [{"title": "demo", "value": "some parameter", "key": ""}],
        "_links": {
          "rss_url": {
            "href": "%s/public/feed" % instance['url']
          },
          "public_url": {
            "href": "%s/share/public/" % instance['url']
          },
          "private_url": {
            "href": "%s/share/private/" % instance['url']
          }
        }
      }

    with open(os.path.join(instance['private_dir'], 'monitor.global.json'), 'w') as f:
      f.write(json.dumps(monitor_dict))
    with open(os.path.join(instance['private_dir'], '_document_list'), 'w') as f:
      f.write("monitor.global")

  def generateMonitoringInstanceTree(self):
    # root instance
    root_instance = self.generateInstanceDirectory("rootInstance")
    self.generatePromiseResult(root_instance, status='OK', amount=5)
    self.generateInstanceRssFeed(root_instance)
    self.generateMonitoringStatusFile(root_instance, status='OK')
    # sub instance1
    sub_instance1 = self.generateInstanceDirectory("subInstance-1")
    self.generatePromiseResult(sub_instance1, status='ERROR', amount=4)
    self.generateInstanceRssFeed(sub_instance1)
    self.generateMonitoringStatusFile(sub_instance1, status='ERROR')
    # sub instance2
    sub_instance2 = self.generateInstanceDirectory("subInstance-2")
    self.generatePromiseResult(sub_instance2, status='OK', amount=7)
    self.generateInstanceRssFeed(sub_instance2)
    self.generateMonitoringStatusFile(sub_instance2, status='OK')

    self.generateOPMLFile(root_instance, [sub_instance1, sub_instance2])

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestZeleniumCore))
  return suite