#! /usr/bin/env python

##############################################################################
#
# Yoshinori OKUJI <yo@nexedi.com>
#
# Copyright (C) 2004 Nexedi SARL
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. ?See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA ?02111-1307, USA.
#
##############################################################################

SBALANCE_VERSION = '4.0'

import sys
import getopt
import socket
import os
import threading
import time
from select import select
import re

if not hasattr(socket, 'setdefaulttimeout'):
  raise RuntimeError, 'Your Python interpreter is too old. Please upgrade it.'

class ClientInfo: pass

class Balancer:
  def __init__(self, port, server_list, bind = '', connect_timeout = 5, select_timeout = None,
               debug = 0, foreground = 0, packet_dump = 0):
    """
      Initialize the basic status.
    """
    self.port = port
    self.server_list = server_list
    self.bind = bind
    self.connect_timeout = connect_timeout
    self.select_timeout = select_timeout
    self.debug = debug
    self.foreground = foreground
    self.packet_dump = packet_dump

    # Make a socket to listen.
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.socket.bind((self.bind, self.port))
    self.socket.listen(5)

    # Make shared information and a lock for it.
    self.lock = threading.Lock()
    self.next_server = 0
    self.sticked_server_dict = {}
    self.disabled_server_dict = {}

    # Daemonize itself.
    if not self.foreground:
      self.daemonize()

  def daemonize(self):
    """
      Make myself a daemon.
    """
    pid = os.fork()
    if pid > 0:
      sys.exit()
    os.chdir('/')
    os.setsid()
    os.umask(0)
    pid = os.fork()
    if pid > 0:
      sys.exit()
    f = open('/dev/null', 'w+')
    os.dup2(f.fileno(), sys.stdin.fileno())
    os.dup2(f.fileno(), sys.stdout.fileno())
    os.dup2(f.fileno(), sys.stderr.fileno())

  def run(self):
    try:
      # Make a thread for expiration of old sticky entries.
      if self.debug:
        print "Starting an expiring daemon thread"
      t = threading.Thread(target=Balancer.expire, args=(self,))
      t.setDaemon(1)
      t.start()

      if self.debug:
        print "Beginning the mail loop to accept clients"
      while 1:
        conn, addr = self.socket.accept()
        if self.debug:
          print "New connection from %s" % str(addr)
        t = threading.Thread(target=Balancer.handleClient, args=(self, conn, addr))
        t.start()
    finally:
      self.socket.close()

  def expire(self):
    while 1:
      time.sleep(60)
      try:
        self.lock.acquire()
        cur_time = time.clock()
        count_dict = {}
        expired_server_list = []
        for key,value in self.sticked_server_dict.items():
          if cur_time > value.atime + 60 * 10:
            expired_server_list.append(key)
          else:
            if value.addr in count_dict:
              count_dict[value.addr] += 1
            else:
              count_dict[value.addr] = 1
        for key in expired_server_list:
          if self.debug:
            print "Expiring %s" % str(key)
          del self.sticked_server_dict[key] # Expire this entry.
        # Find the max and the min.
        max = -1
        min = len(self.sticked_server_dict) + 1
        for addr,count in count_dict.items():
          if count > max:
            max = count
            max_addr = addr
          if count < min:
            min = count
            min_addr = addr
        # If the max is significantly greater than the min, move some clients.
        if max > min + 1:
          num = max - min
          for key,value in self.sticked_server_dict.items():
            if value.addr == max_addr:
              if self.debug:
                print "Moving %s from %s to %s" % (str(key), str(max_addr), str(min_addr))
              value.addr = min_addr
              num -= 1
              if num <= 0:
                break
        # Enable old entries in disabled servers.
        enabled_server_list = []
        for addr,ctime in self.disabled_server_dict.items():
          if cur_time > ctime + 60 * 3:
            enabled_server_list.append(addr)
        for addr in enabled_server_list:
          if self.debug:
            print 'Enabling %s again' % addr
          del self.disabled_server_dict[addr]
      finally:
        self.lock.release()

  def getSignature(self, s):
    """
      Try to find out a signature. Depend on Zope and CookieCrumbler in CMFCore.
    """
    if s[:3] == 'GET' or s[:3] == 'PUT' or s[:4] == 'PUSH':
      # This looks like a HTTP request.
      header_end = s.find('\r\n\r\n')
      if header_end < 0:
        return None
      s = s[:header_end]
      m = re.search('\r\nAuthorization:\s*(.+)', s, re.IGNORECASE)
      if m:
        return s[m.start(1):m.end(1)]
      m = re.search('\r\nCookie:.*__ac=\"(.+)\"', s, re.IGNORECASE)
      if m:
        return s[m.start(1):m.end(1)]
    return None

  def handleClient(self, conn, addr):
    """
      Choose a server and do a proxy job.
    """
    server_conn = None
    try:
      # Make a new socket.
      server_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      server_conn.settimeout(self.connect_timeout)

      # Need to read the first some bytes to get a signature.
      size = 4096
      buf = ""
      while size > 0:
        iwtd, owtd, ewtd = select([conn], [], [], 0.1)
        if len(iwtd) == 0: break
        data = conn.recv(size)
        size -= len(data)
        buf += data
      signature = self.getSignature(buf)

      # Choose a server.
      try:
        self.lock.acquire()
        addr = None
        if signature is not None and signature in self.sticked_server_dict:
          addr = self.sticked_server_dict[signature].addr
          start_index = self.server_list.index(addr)
        else:
          addr = self.server_list[self.next_server]
          start_index = self.next_server
        self.next_server = start_index + 1
        if self.next_server == len(self.server_list):
          self.next_server = 0
      finally:
        self.lock.release()

      index = start_index
      while 1:
        # Check if this server is enabled.
        enabled = 1
        try:
          self.lock.acquire()
          if addr in self.disabled_server_dict:
            enabled = 0
        finally:
          self.lock.release()

        if enabled:
          try:
            host, port = addr.split(':')
            port = int(port)
            server_conn.connect((host, port))
            break
          except:
            # Something wrong happened with this server.
            try:
              self.lock.acquire()
              if self.debug:
                print 'Disabling %s' % addr
              cur_time = time.clock()
              self.disabled_server_dict[addr] = cur_time
            finally:
              self.lock.release()

        # Need to find the next server.
        index += 1
        try:
          self.lock.acquire()
          if index >= len(self.server_list):
            index = 0
          addr = self.server_list[index]
        finally:
          self.lock.release()

        if index == start_index:
          # No way.
          if self.debug:
            print 'No available server found.'
          return

      # Register this client if possible.
      if signature:
        try:
          self.lock.acquire()
          if self.debug:
            print 'Registering %s with %s' % (signature, addr)
          cur_time = time.clock()
          if signature in self.sticked_server_dict:
            info = self.sticked_server_dict[signature]
            info.atime = cur_time
            info.addr = addr
          else:
            info = ClientInfo()
            info.atime = cur_time
            info.addr = addr
            self.sticked_server_dict[signature] = info
        finally:
          self.lock.release()

      # Now is the time to play.
      server_conn.settimeout(None)
      server_conn.sendall(buf)
      while 1:
        iwtd, owtd, ewtd = select([server_conn, conn], [], [], self.select_timeout)
        if len(iwtd) == 0:
          return
        if server_conn in iwtd:
          buf = server_conn.recv(4096)
          if len(buf) == 0: return
          conn.sendall(buf)
        if conn in iwtd:
          buf = conn.recv(4096)
          if len(buf) == 0: return
          server_conn.sendall(buf)
    finally:
      conn.close()
      if server_conn is not None: server_conn.close()

def main():
  kwd = {}
  try:
    opts, args = getopt.getopt(sys.argv[1:], "hvb:t:T:dfps",
                               ["help", "version", "bind=", "connect-timeout=", "select-timeout=", "debug", "foreground", "packet-dump", "sticky"])
  except getopt.GetoptError, msg:
    print msg
    print "Try ``sbalance --help'' for more information."
    sys.exit(2)
  for o, a in opts:
    if o in ("-v", "--version"):
      print "sbalance version %s" % SBALANCE_VERSION
      sys.exit()
    elif o in ("-h", "--help"):
      print '''Usage: sbalace [OPTION...] PORT HOST:[PORT]...
Balance TCP/IP loads with distributed servers.

    -h, --help                display this message and exit
    -v, --version             print version information and exit
    -b, --bind=HOST           accept connections only to a host instead of any
    -t, --connect-timeout=SEC specify the timeout for connect
    -T, --select-timeout=SEC  specify the timeout for select
    -d, --debug               output debugging information
    -f, --foreground          run sbalance in foreground
    -p, --packet-dump         dump packet contents
    -s, --sticky              for backward compatibility

PORT is the port number to listen to. You can specify any number of
pairs of a host and a port.

Report bugs to <yo@nexedi.com>.'''
      sys.exit()
    elif o in ("-b", "--bind"):
      kwd['bind'] = a
    elif o in ("-t", "--connect-timeout"):
      kwd['connect_timeout'] = int(a)
    elif o in ("-T", "--select-timeout"):
      kwd['select_timeout'] = int(a)
    elif o in ("-d", "--debug"):
      kwd['debug'] = 1
    elif o in ("-f", "--foreground"):
      kwd['foreground'] = 1
    elif o in ("-p", "--packet-dump"):
      kwd['packet_dump'] = 1
    elif o in ("-s", "--stickey"):
      pass

  if len(args) < 2:
    print "Too few arguments."
    print "Try ``sbalance --help'' for more information."
    sys.exit(2)

  port = int(args[0])
  server_list = []
  for server in args[1:]:
    if server == '%' or server == '!': continue # For compatibility.
    i = server.find(':')
    if i < 0:
      addr = server + ':' + str(port)
    else:
      addr = server
    server_list.append(addr)
  if len(server_list) < 1:
    print "No server is specified."
    print "Try ``sbalance --help'' for more information."
    sys.exit(2)

  b = Balancer(port, server_list, **kwd)
  b.run()

if __name__ == "__main__":
  main()
