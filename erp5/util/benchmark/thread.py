##############################################################################
#
# Copyright (c) 2011 Nexedi SA and Contributors. All Rights Reserved.
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

import threading
import time
import requests

class TestThread(threading.Thread):

  def __init__(self, process_manager, command, log):
    threading.Thread.__init__(self)
    self.process_manager = process_manager
    self.command = command
    self.log = log
  
  def run(self):
    self.process_manager.spawn(*self.command)

class TestMetricThread(threading.Thread):

  def __init__(self, metric_url, log, stop_event, interval=60):
    threading.Thread.__init__(self)
    self.metric_url = metric_url
    self.log = log
    self.interval = interval
    self.stop_event = stop_event
    self.metric_list = []

  def run(self):
    while(not self.stop_event.is_set()):
      self.stop_event.wait(-time.time() % self.interval)
      response = requests.get(self.metric_url)
      if response.status_code == 200:
        self.metric_list.append(response.text)
  
  def getMetricList(self):
    return self.metric_list



