##############################################################################
#
# Copyright (c) 2007 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets <jp@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the Python Software Foundation License (PSFL)
#
##############################################################################

import urllib2, os, dircache, urllib
from StringIO import StringIO
from urllib2 import FileHandler, url2pathname, mimetypes, mimetools, addinfourl, URLError

class DirectoryFileHandler(FileHandler):
    """
    Extends the file handler to provide an HTML
    representation of local directories. 
    """

    # Use local file or FTP depending on form of URL
    def file_open(self, req):
        url = req.get_selector()
        if url[:2] == '//' and url[2:3] != '/':
            req.type = 'ftp'
            return self.parent.open(req)
        else:
            return self.open_local_file(req)

    # not entirely sure what the rules are here
    def open_local_file(self, req):
        import email.Utils
        host = req.get_host()
        file = req.get_selector()
        localfile = url2pathname(file)
        stats = os.stat(localfile)
        size = stats.st_size
        modified = email.Utils.formatdate(stats.st_mtime, usegmt=True)
        mtype = mimetypes.guess_type(file)[0]
        headers = mimetools.Message(StringIO(
            'Content-type: %s\nContent-length: %d\nLast-modified: %s\n' %
            (mtype or 'text/plain', size, modified)))
        if host:
            host, port = splitport(host)
        if not host or \
           (not port and socket.gethostbyname(host) in self.get_names()):
            try:
              file_list = dircache.listdir(localfile)
              s = StringIO()
              s.write('<html><head><base href="%s"/></head><body>' % 'file:' + file)
              for f in file_list:
                s.write('<p><a href="%s/">%s</a></p>\n' % (urllib.quote(f), f))
              s.write('</body></html>')
              s.seek(0)
              headers = mimetools.Message(StringIO(
                  'Content-type: %s\nContent-length: %d\nLast-modified: %s\n' %
                  ('text/html', size, modified)))
              return addinfourl(s, headers, 'file:' + file)
            except OSError:
              return addinfourl(open(localfile, 'rb'),
                                headers, 'file:'+file)
        raise URLError('file not on local host')
