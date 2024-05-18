# ERP5.Document | Tests for BigFile
#
# Copyright (C) 2015 Nexedi SA and Contributors. All Rights Reserved.
#               Kirill Smelkov <kirr@nexedi.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

import io
from ZPublisher.HTTPRequest import HTTPRequest
from ZPublisher.HTTPResponse import HTTPResponse
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type import IS_ZOPE2
from erp5.component.module.BTreeData import BTreeData


# like Testing.makerequest, but
#
#   1. always redirects stdout to BytesIO,
#   2. stdin content can be specified and is processed,
#   3. returns actual request object (not wrapped portal).
#
# see also: Products.CMFCore.tests.test_CookieCrumbler.makerequest()
# TODO makerequest() is generic enough and deserves moving to testing utils
def makerequest(environ=None, stdin=b''):
  stdout = io.BytesIO()
  stdin  = io.BytesIO(stdin)
  if environ is None:
    environ = {}

  # Header-Name -> HEADER_NAME
  _ = {}
  for k,v in environ.items():
    k = k.replace('-', '_').upper()
    _[k] = v
  environ = _

  response = HTTPResponse(stdout=stdout)
  environ.setdefault('SERVER_NAME',    'foo')
  environ.setdefault('SERVER_PORT',    '80')
  request  = HTTPRequest(stdin, environ, response)
  # process stdin data
  request.processInputs()
  return request

# generate makerequest-like function for http method
def request_function(method_name):
  method_name = method_name.upper()
  def method_func(environ=None, stdin=b''):
    if environ is None:
      environ = {}
    environ.setdefault('REQUEST_METHOD', method_name)
    return makerequest(environ, stdin)
  method_func.func_name = method_name
  return method_func

# requests
get = request_function('GET')
put = request_function('PUT')

if IS_ZOPE2: # BBB Zope2
  # FIXME Zope translates 308 to 500
  # https://github.com/zopefoundation/Zope/blob/2.13/src/ZPublisher/HTTPResponse.py#L223
  # https://github.com/zopefoundation/Zope/blob/2.13/src/ZPublisher/HTTPResponse.py#L64
  R308 = 500
else:
  R308 = 308

class TestBigFile(ERP5TypeTestCase):
  """Tests for ERP5.Document.BigFile"""

  def getBusinessTemplateList(self):
    """bt5 required to run this tests"""
    return ('erp5_big_file',
               # test runner does not automatically install bt5 dependencies -
               # - next erp5_big_file dependencies are specified manually
               'erp5_dms',
                 'erp5_web',
                 'erp5_ingestion',
                 'erp5_base',
               )[::-1]	# NOTE install order is important


  # check that object (document) method corresponding to request returns
  # result, with expected response body, status and headers
  def checkRequest(self, document, request, kw, result, body, status, header_dict):
    # request -> method to call
    method_name = request['REQUEST_METHOD']
    if method_name == 'GET':
      method_name = 'index_html'
    method = getattr(document, method_name)

    ret = method (request, request.RESPONSE, **kw)
    # like in ZPublisher - returned RESPONSE means empty
    if ret is request.RESPONSE:
      ret = b''
    self.assertEqual(ret,       result)
    self.assertEqual(status,    request.RESPONSE.getStatus())
    for h,v in header_dict.items():
      rv = request.RESPONSE.getHeader(h)
      self.assertEqual(v, rv, '%s: %r != %r' % (h, v, rv))

    # force response flush to its stdout
    request.RESPONSE.write(b'')
    # body and headers are delimited by empty line (RFC 2616, 4.1)
    response_body = request.RESPONSE.stdout.getvalue().split(b'\r\n\r\n', 1)[1]
    self.assertEqual(body, response_body)


  # basic tests for working with BigFile via its public interface
  def testBigFile_01_Basic(self):
    big_file_module = self.getPortal().big_file_module
    f = big_file_module.newContent(portal_type='Big File')
    check = lambda *args: self.checkRequest(f, *args)


    # after creation file is empty and get(0-0) returns 416
    self.assertEqual(f.getSize(), 0)
    self.assertEqual(f.getData(), b'')

                                             #  result body status headers
    check(get(), {'format': 'raw'},                 b'', b'', 200, {'Content-Length': '0'})
    check(put({'Content-Range': 'bytes */*'}),{},   b'', b'',R308, {                                  'Range': 'bytes 0--1'})  # XXX 0--1 ok?
    check(get({        'Range': 'bytes=0-0'}),{},   b'', b'', 416, {'Content-Length': '0',    'Content-Range': 'bytes */0'})


    # append empty chunk - the same
    f._appendData(b'')
    self.assertEqual(f.getSize(), 0)
    self.assertEqual(f.getData(), b'')

    check(get(), {'format': 'raw'},                 b'', b'', 200, {'Content-Length': '0'})
    check(put({'Content-Range': 'bytes */*'}),{},   b'', b'',R308, {                                  'Range': 'bytes 0--1'})  # XXX 0--1 ok?
    check(get({        'Range': 'bytes=0-0'}),{},   b'', b'', 416, {                          'Content-Range': 'bytes */0'})


    # append 1 byte - file should grow up and get(0-0) returns 206
    f._appendData(b'x')
    self.assertEqual(f.getSize(), 1)
    self.assertEqual(f.getData(), b'x')

    check(get(), {'format': 'raw'},                 b'', b'x', 200, {'Content-Length': '1'})
    check(put({'Content-Range': 'bytes */*'}),{},   b'', b'', R308, {                                'Range': 'bytes 0-0'})
    check(get({        'Range': 'bytes=0-0'}),{},   b'', b'x', 206, {'Content-Length': '1',  'Content-Range': 'bytes 0-0/1'})


    # append another 2 bytes and try to get whole file and partial contents
    f._appendData(b'yz')
    self.assertEqual(f.getSize(), 3)
    self.assertEqual(f.getData(), b'xyz')

    check(get(), {'format': 'raw'},                 b'', b'xyz',  200, {'Content-Length': '3'})
    check(put({'Content-Range': 'bytes */*'}),{},   b'', b'',    R308, {                                'Range': 'bytes 0-2'})
    check(get({        'Range': 'bytes=0-0'}),{},   b'', b'x'  ,  206, {'Content-Length': '1',  'Content-Range': 'bytes 0-0/3'})
    check(get({        'Range': 'bytes=1-1'}),{},   b'',  b'y' ,  206, {'Content-Length': '1',  'Content-Range': 'bytes 1-1/3'})
    check(get({        'Range': 'bytes=2-2'}),{},   b'',   b'z',  206, {'Content-Length': '1',  'Content-Range': 'bytes 2-2/3'})
    check(get({        'Range': 'bytes=0-1'}),{},   b'', b'xy' ,  206, {'Content-Length': '2',  'Content-Range': 'bytes 0-1/3'})
    check(get({        'Range': 'bytes=1-2'}),{},   b'',  b'yz',  206, {'Content-Length': '2',  'Content-Range': 'bytes 1-2/3'})
    check(get({        'Range': 'bytes=0-2'}),{},   b'', b'xyz',  206, {'Content-Length': '3',  'Content-Range': 'bytes 0-2/3'})

    # append via PUT with range
    check(put({'Content-Range': 'bytes 3-4/5', 'Content-Length': '2'}, b'01'),{},  b'', b'', 204, {})
    self.assertEqual(f.getSize(), 5)
    self.assertEqual(f.getData(), b'xyz01')
    check(get(), {'format': 'raw'},                 b'', b'xyz01',200, {'Content-Length': '5'})
    check(put({'Content-Range': 'bytes */*'}),{},   b'', b'',    R308, {                                'Range': 'bytes 0-4'})
    check(get({        'Range': 'bytes=0-4'}),{},   b'', b'xyz01',206, {'Content-Length': '5',  'Content-Range': 'bytes 0-4/5'})
    check(get({        'Range': 'bytes=1-3'}),{},   b'',  b'yz0' ,206, {'Content-Length': '3',  'Content-Range': 'bytes 1-3/5'})
    check(get({        'Range': 'bytes=1-2'}),{},   b'',  b'yz'  ,206, {'Content-Length': '2',  'Content-Range': 'bytes 1-2/5'})
    check(get({        'Range': 'bytes=2-2'}),{},   b'',   b'z'  ,206, {'Content-Length': '1',  'Content-Range': 'bytes 2-2/5'})

    # replace whole content via PUT without range
    # (and we won't exercise GET with range routinely further)
    check(put({'Content-Length': '3'}, b'abc'),{},  b'', b'', 204, {})
    self.assertEqual(f.getSize(), 3)
    self.assertEqual(f.getData(), b'abc')
    check(get(), {'format': 'raw'},                 b'', b'abc',  200, {'Content-Length': '3'})
    check(put({'Content-Range': 'bytes */*'}),{},   b'', b'',    R308, {                                'Range': 'bytes 0-2'})

    # append via PUT with range (again)
    check(put({'Content-Range': 'bytes 3-7/8', 'Content-Length': '5'}, b'defgh'),{},  b'', b'', 204, {})
    self.assertEqual(f.getSize(), 8)
    self.assertEqual(f.getData(), b'abcdefgh')
    check(get(), {'format': 'raw'},                 b'', b'abcdefgh', 200, {'Content-Length': '8'})
    check(put({'Content-Range': 'bytes */*'}),{},   b'', b'',        R308, {                            'Range': 'bytes 0-7'})

    # append via ._appendData()  (again)
    f._appendData(b'ij')
    self.assertEqual(f.getSize(), 10)
    self.assertEqual(f.getData(), b'abcdefghij')
    check(get(), {'format': 'raw'},                 b'', b'abcdefghij', 200, {'Content-Length': '10'})
    check(put({'Content-Range': 'bytes */*'}),{},   b'', b'',          R308, {                          'Range': 'bytes 0-9'})

    # make sure PUT with incorrect/non-append range is rejected
    check(put({'Content-Range': 'bytes 10-10/10', 'Content-Length': '1'}, b'k'),{}, b'', b'', 400, {'X-Explanation': 'Total size unexpected'})
    self.assertEqual(f.getData(), b'abcdefghij')
    check(put({'Content-Range': 'bytes 10-10/11', 'Content-Length': '2'}, b'k'),{}, b'', b'', 400, {'X-Explanation': 'Content length unexpected'})
    self.assertEqual(f.getData(), b'abcdefghij')
    check(put({'Content-Range': 'bytes 8-8/10',   'Content-Length': '1'}, b'?'),{}, b'', b'', 400, {'X-Explanation': 'Can only append data'})
    check(put({'Content-Range': 'bytes 9-9/10',   'Content-Length': '1'}, b'?'),{}, b'', b'', 400, {'X-Explanation': 'Can only append data'})
    check(put({'Content-Range': 'bytes 9-10/11',  'Content-Length': '2'},b'??'),{}, b'', b'', 400, {'X-Explanation': 'Can only append data'})
    check(put({'Content-Range': 'bytes 11-11/12', 'Content-Length': '1'}, b'?'),{}, b'', b'', 400, {'X-Explanation': 'Can only append data'})

    # TODO test 'If-Range' with GET
    # TODO test multiple ranges in 'Range' with GET


  # test BigFile's .data property can be of several types and is handled
  # properly and we can still get data and migrate to BTreeData transparently
  # (called from under testBigFile_02_DataVarious driver)
  def _testBigFile_02_DataVarious(self):
    # BigFile's .data can be:
    # bytes       - because data comes from Data property sheet and default value is b''
    # None      - because it can be changed
    # BTreeData - because it is scalable way to work with large content
    #
    # bytes can be possibly non-empty because we could want to transparently
    # migrate plain File documents to BigFiles.
    #
    # make sure BigFile correctly works in all those situations.

    big_file_module = self.getPortal().big_file_module
    f = big_file_module.newContent(portal_type='Big File')
    check = lambda *args: self.checkRequest(f, *args)

    # after creation .data is b''  (as per default from Data property sheet)
    _ = f._baseGetData()
    self.assertIsInstance(_, bytes)
    self.assertEqual(_, b'')

    # make sure we can get empty content through all ways
    # (already covered in testBigFile_01_Basic, but still)
    self.assertEqual(f.getSize(), 0)
    self.assertEqual(f.getData(), b'')
    check(get(), {'format': 'raw'},                 b'', b'', 200, {'Content-Length': '0'})
    check(put({'Content-Range': 'bytes */*'}),{},   b'', b'',R308, {                                'Range': 'bytes 0--1'})  # XXX 0--1 ok?
    check(get({        'Range': 'bytes=0-0'}),{},   b'', b'', 416, {'Content-Length': '0',  'Content-Range': 'bytes */0'})


    # set .data to non-empty str and make sure we can get content through all ways
    f._baseSetData(b'abc')
    _ = f._baseGetData()
    self.assertIsInstance(_, bytes)
    self.assertEqual(_, b'abc')
    self.assertEqual(f.getSize(), 3)
    self.assertEqual(f.getData(), b'abc')
    check(get(), {'format': 'raw'},                 b'abc', b'',    200, {'Content-Length': '3'})
    check(put({'Content-Range': 'bytes */*'}),{},   b''   , b'',   R308, {                                'Range': 'bytes 0-2'})
    check(get({        'Range': 'bytes=0-2'}),{},   b''   , b'abc', 206, {'Content-Length': '3',  'Content-Range': 'bytes 0-2/3'})

    # and .data should remain str after access (though later this could be
    # changed to transparently migrate to BTreeData)
    _ = f._baseGetData()
    self.assertIsInstance(_, bytes)
    self.assertEqual(_, b'abc')


    # on append .data should migrate to BTreeData
    f._appendData(b'd')
    _ = f._baseGetData()
    self.assertIsInstance(_, BTreeData)
    self.assertEqual(f.getSize(), 4)
    self.assertEqual(f.getData(), b'abcd')
    check(get(), {'format': 'raw'},                 b'', b'abcd', 200, {'Content-Length': '4'})
    check(put({'Content-Range': 'bytes */*'}),{},   b'', b'',    R308, {                                'Range': 'bytes 0-3'})
    check(get({        'Range': 'bytes=0-3'}),{},   b'', b'abcd', 206, {'Content-Length': '4',  'Content-Range': 'bytes 0-3/4'})



    # change .data to None and make sure we can still get empty content
    # NOTE additionally to ._baseSetData(None), ._setData(None) also sets
    #      .size=0 which is needed for correct BigFile bases operation.
    #
    #      see ERP5.Document.File._setSize() for details.
    f._setData(None)
    # NOTE still b'' because it is default value specified in Data property
    #      sheet for .data field
    _ = f._baseGetData()
    self.assertIsInstance(_, bytes)
    self.assertEqual(_, b'')
    # but we can change property sheet default on the fly
    # XXX ( only for this particular getter _baseGetData -
    #       - because property type information is not stored in one place,
    #       but is copied on getter/setter initialization - see Getter/Setter
    #       in ERP5Type.Accessor.Base )
    # NOTE this change is automatically reverted back in calling helper
    self.assertIsInstance(f._baseGetData._default, bytes)
    self.assertEqual(f._baseGetData._default, b'')
    f._baseGetData.__func__._default = None  # NOTE not possible to do on just f._baseGetData
    self.assertIs(f._baseGetData._default, None)
    self.assertIs(f._baseGetData(), None)   # <- oops

    self.assertEqual(f.getSize(), 0)
    self.assertIs   (f.getData(), None)
    check(get(), {'format': 'raw'},                 b'', b'', 200, {'Content-Length': '0'})
    check(put({'Content-Range': 'bytes */*'}),{},   b'', b'',R308, {                                'Range': 'bytes 0--1'})  # XXX 0--1 ok?
    check(get({        'Range': 'bytes=0-0'}),{},   b'', b'', 416, {'Content-Length': '0',  'Content-Range': 'bytes */0'})


    # on append .data should become BTreeData
    f._appendData(b'x')
    _ = f._baseGetData()
    self.assertIsInstance(_, BTreeData)
    self.assertEqual(f.getSize(), 1)
    self.assertEqual(f.getData(), b'x')
    check(get(), {'format': 'raw'},                 b'', b'x',    200, {'Content-Length': '1'})
    check(put({'Content-Range': 'bytes */*'}),{},   b'', b'',    R308, {                                'Range': 'bytes 0-0'})
    check(get({        'Range': 'bytes=0-3'}),{},   b'', b'x',    206, {'Content-Length': '1',  'Content-Range': 'bytes 0-0/1'})



  # helper to call _testBigFile_02_DataVarious() and restore .data._default
  def testBigFile_02_DataVarious(self):
    big_file_module = self.getPortal().big_file_module
    f = big_file_module.newContent(portal_type='Big File')

    # Data property sheet specifies .data default to b''
    _ = f._baseGetData()
    self.assertIsInstance(_, bytes)
    self.assertEqual(_, b'')

    # NOTE obtaining getter is not possible via BigFile._baseGetData
    g = f._baseGetData.__func__
    self.assertIsInstance(g._default, bytes)
    self.assertEqual(g._default, b'')

    try:
      self._testBigFile_02_DataVarious()

    # restore ._baseGetData._default and make sure restoration really worked
    finally:
      g._default = b''
      f._baseSetData(None)    # so that we are sure getter returns class defaults
      _ = f._baseGetData()
      self.assertIsInstance(_, bytes)
      self.assertEqual(_, b'')



  # TODO write big data to file and ensure it still works
  # TODO test streaming works in chunks
