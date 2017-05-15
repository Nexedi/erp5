##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

import ZServer.HTTPResponse
from ZPublisher.pubevents import PubBeforeStreaming
import tempfile
import thread
from zope.event import notify

tempfile_max_size = 1024**3

def write(self,data):
    """\
    Return data as a stream

    HTML data may be returned using a stream-oriented interface.
    This allows the browser to display partial results while
    computation of a response to proceed.

    The published object should first set any output headers or
    cookies on the response object.

    Note that published objects must not generate any errors
    after beginning stream-oriented output.

    """


    if type(data) is not str:
        raise TypeError('Value must be a string')

    stdout = self.stdout

    if not self._wrote:
        notify(PubBeforeStreaming(self))

        l = self.headers.get('content-length', None)
        if l is not None:
            try:
                if type(l) is str: l = int(l)
                if l > 128000:
                    self._tempfile = tempfile.TemporaryFile()
                    self._templock = thread.allocate_lock()
            except: pass

        self._streaming = 1
        stdout.write(str(self))
        self._wrote = 1

    if not data: return

    if self._chunking:
        data = '%x\r\n%s\r\n' % (len(data),data)

    l = len(data)

    t = self._tempfile
    if t is None or l<200:
        stdout.write(data)
    else:
        b = self._tempstart
        e = b + l
        self._templock.acquire()
        try:
            t.seek(b)
            t.write(data)
        finally:
            self._templock.release()

        if e > tempfile_max_size:
            self._tempstart = 0
            self._tempfile = tempfile.TemporaryFile()
            stdout.write(file_part_producer(t,self._templock,b,e,close_after_more=True), l)
        else:
            self._tempstart = e
            stdout.write(file_part_producer(t,self._templock,b,e), l)


class file_part_producer:
    "producer wrapper for part of a file[-like] objects"
    # match http_channel's outgoing buffer size
    out_buffer_size = 1<<16

    def __init__(self, file, lock, start, end, close_after_more=False):
        self.file=file
        self.lock=lock
        self.start=start
        self.end=end
        self.close_after_more=close_after_more

    def more(self):
        end=self.end
        if not end: return ''
        start=self.start
        if start >= end: return ''

        file=self.file
        size=end-start
        bsize=self.out_buffer_size
        if size > bsize: size=bsize

        self.lock.acquire()
        try:
            file.seek(start)
            data = file.read(size)
        finally:
            self.lock.release()

        if data:
            start=start+len(data)
            if start < end:
                self.start=start
                return data

        self.end=0
        if self.close_after_more:
            self.file.close()
        del self.file

        return data

ZServer.HTTPResponse.ZServerHTTPResponse.write = write
