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

from cStringIO import StringIO

from ZPublisher.HTTPRequest import HTTPRequest
from ZPublisher.HTTPResponse import HTTPResponse
from ZPublisher.Iterators import IUnboundStreamIterator
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.BTreeData import BTreeData


# like Testing.makerequest, but
#
#   1. always redirects stdout to stringio,
#   2. stdin content can be specified and is processed,
#   3. returns actual request object (not wrapped portal).
#
# see also: Products.CMFCore.tests.test_CookieCrumbler.makerequest()
# TODO makerequest() is generic enough and deserves moving to testing utils
def makerequest(environ=None, stdin=''):
  stdout = StringIO()
  stdin  = StringIO(stdin)
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
  def method_func(environ=None, stdin=''):
    if environ is None:
      environ = {}
    environ.setdefault('REQUEST_METHOD', method_name)
    return makerequest(environ, stdin)
  method_func.func_name = method_name
  return method_func

# requests
get = request_function('GET')
put = request_function('PUT')


# FIXME Zope translates 308 to 500
# https://github.com/zopefoundation/Zope/blob/2.13/src/ZPublisher/HTTPResponse.py#L223
# https://github.com/zopefoundation/Zope/blob/2.13/src/ZPublisher/HTTPResponse.py#L64
R308 = 500



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
    assert type(result) is str
    assert type(body) is str
    # - result corresponds to the content returned as a string;
    # - body corresponds to the content returned inside a stream iterator.
    # We can't have both at the same time.
    assert not(bool(result) == bool(body) == True)

    # request -> method to call
    method_name = request['REQUEST_METHOD']
    if method_name == 'GET':
      method_name = 'index_html'
    method = getattr(document, method_name)

    ret = method (request, request.RESPONSE, **kw)
    # like in ZPublisher - returned RESPONSE means empty
    if ret is request.RESPONSE:
      ret = ''
    elif IUnboundStreamIterator.providedBy(ret):
      ret = ''.join(ret)
    self.assertEqual(status, request.RESPONSE.getStatus())
    for h,v in header_dict.items():
      rv = request.RESPONSE.getHeader(h)
      self.assertEqual(v, rv, '%s: %r != %r' % (h, v, rv))
    if result:
      self.assertEqual(ret, result)
    elif body:
      self.assertEqual(ret, body)
    else:
      self.assertEqual(ret, '')

  # basic tests for working with BigFile via its public interface
  def testBigFile_01_Basic(self):
    big_file_module = self.getPortal().big_file_module
    f = big_file_module.newContent(portal_type='Big File')
    check = lambda *args: self.checkRequest(f, *args)


    # after creation file is empty and get(0-0) returns 416
    self.assertEqual(f.getSize(), 0)
    self.assertEqual(f.getData(), '')

                                             #  result body status headers
    check(get(), {'format': 'raw'},                 '', '', 200, {'Content-Length': '0'})
    check(put({'Content-Range': 'bytes */*'}),{},   '', '',R308, {                                  'Range': 'bytes 0--1'})  # XXX 0--1 ok?
    check(get({        'Range': 'bytes=0-0'}),{},   '', '', 416, {'Content-Length': '0',    'Content-Range': 'bytes */0'})


    # append empty chunk - the same
    f._appendData('')
    self.assertEqual(f.getSize(), 0)
    self.assertEqual(f.getData(), '')

    check(get(), {'format': 'raw'},                 '', '', 200, {'Content-Length': '0'})
    check(put({'Content-Range': 'bytes */*'}),{},   '', '',R308, {                                  'Range': 'bytes 0--1'})  # XXX 0--1 ok?
    check(get({        'Range': 'bytes=0-0'}),{},   '', '', 416, {                          'Content-Range': 'bytes */0'})


    # append 1 byte - file should grow up and get(0-0) returns 206
    f._appendData('x')
    self.assertEqual(f.getSize(), 1)
    self.assertEqual(f.getData(), 'x')

    check(get(), {'format': 'raw'},                 '', 'x', 200, {'Content-Length': '1'})
    check(put({'Content-Range': 'bytes */*'}),{},   '', '', R308, {                                'Range': 'bytes 0-0'})
    check(get({        'Range': 'bytes=0-0'}),{},   '', 'x', 206, {'Content-Length': '1',  'Content-Range': 'bytes 0-0/1'})


    # append another 2 bytes and try to get whole file and partial contents
    f._appendData('yz')
    self.assertEqual(f.getSize(), 3)
    self.assertEqual(f.getData(), 'xyz')

    check(get(), {'format': 'raw'},                 '', 'xyz',  200, {'Content-Length': '3'})
    check(put({'Content-Range': 'bytes */*'}),{},   '', '',    R308, {                                'Range': 'bytes 0-2'})
    check(get({        'Range': 'bytes=0-0'}),{},   '', 'x'  ,  206, {'Content-Length': '1',  'Content-Range': 'bytes 0-0/3'})
    check(get({        'Range': 'bytes=1-1'}),{},   '',  'y' ,  206, {'Content-Length': '1',  'Content-Range': 'bytes 1-1/3'})
    check(get({        'Range': 'bytes=2-2'}),{},   '',   'z',  206, {'Content-Length': '1',  'Content-Range': 'bytes 2-2/3'})
    check(get({        'Range': 'bytes=0-1'}),{},   '', 'xy' ,  206, {'Content-Length': '2',  'Content-Range': 'bytes 0-1/3'})
    check(get({        'Range': 'bytes=1-2'}),{},   '',  'yz',  206, {'Content-Length': '2',  'Content-Range': 'bytes 1-2/3'})
    check(get({        'Range': 'bytes=0-2'}),{},   '', 'xyz',  206, {'Content-Length': '3',  'Content-Range': 'bytes 0-2/3'})

    # append via PUT with range
    check(put({'Content-Range': 'bytes 3-4/5', 'Content-Length': '2'}, '01'),{},  '', '', 204, {})
    self.assertEqual(f.getSize(), 5)
    self.assertEqual(f.getData(), 'xyz01')
    check(get(), {'format': 'raw'},                 '', 'xyz01',200, {'Content-Length': '5'})
    check(put({'Content-Range': 'bytes */*'}),{},   '', '',    R308, {                                'Range': 'bytes 0-4'})
    check(get({        'Range': 'bytes=0-4'}),{},   '', 'xyz01',206, {'Content-Length': '5',  'Content-Range': 'bytes 0-4/5'})
    check(get({        'Range': 'bytes=1-3'}),{},   '',  'yz0' ,206, {'Content-Length': '3',  'Content-Range': 'bytes 1-3/5'})
    check(get({        'Range': 'bytes=1-2'}),{},   '',  'yz'  ,206, {'Content-Length': '2',  'Content-Range': 'bytes 1-2/5'})
    check(get({        'Range': 'bytes=2-2'}),{},   '',   'z'  ,206, {'Content-Length': '1',  'Content-Range': 'bytes 2-2/5'})

    # replace whole content via PUT without range
    # (and we won't exercise GET with range routinely further)
    check(put({'Content-Length': '3'}, 'abc'),{},  '', '', 204, {})
    self.assertEqual(f.getSize(), 3)
    self.assertEqual(f.getData(), 'abc')
    check(get(), {'format': 'raw'},                 '', 'abc',  200, {'Content-Length': '3'})
    check(put({'Content-Range': 'bytes */*'}),{},   '', '',    R308, {                                'Range': 'bytes 0-2'})

    # append via PUT with range (again)
    check(put({'Content-Range': 'bytes 3-7/8', 'Content-Length': '5'}, 'defgh'),{},  '', '', 204, {})
    self.assertEqual(f.getSize(), 8)
    self.assertEqual(f.getData(), 'abcdefgh')
    check(get(), {'format': 'raw'},                 '', 'abcdefgh', 200, {'Content-Length': '8'})
    check(put({'Content-Range': 'bytes */*'}),{},   '', '',        R308, {                            'Range': 'bytes 0-7'})

    # append via ._appendData()  (again)
    f._appendData('ij')
    self.assertEqual(f.getSize(), 10)
    self.assertEqual(f.getData(), 'abcdefghij')
    check(get(), {'format': 'raw'},                 '', 'abcdefghij', 200, {'Content-Length': '10'})
    check(put({'Content-Range': 'bytes */*'}),{},   '', '',          R308, {                          'Range': 'bytes 0-9'})

    # make sure PUT with incorrect/non-append range is rejected
    check(put({'Content-Range': 'bytes 10-10/10', 'Content-Length': '1'}, 'k'),{}, '', '', 400, {'X-Explanation': 'Total size unexpected'})
    self.assertEqual(f.getData(), 'abcdefghij')
    check(put({'Content-Range': 'bytes 10-10/11', 'Content-Length': '2'}, 'k'),{}, '', '', 400, {'X-Explanation': 'Content length unexpected'})
    self.assertEqual(f.getData(), 'abcdefghij')
    check(put({'Content-Range': 'bytes 8-8/10',   'Content-Length': '1'}, '?'),{}, '', '', 400, {'X-Explanation': 'Can only append data'})
    check(put({'Content-Range': 'bytes 9-9/10',   'Content-Length': '1'}, '?'),{}, '', '', 400, {'X-Explanation': 'Can only append data'})
    check(put({'Content-Range': 'bytes 9-10/11',  'Content-Length': '2'},'??'),{}, '', '', 400, {'X-Explanation': 'Can only append data'})
    check(put({'Content-Range': 'bytes 11-11/12', 'Content-Length': '1'}, '?'),{}, '', '', 400, {'X-Explanation': 'Can only append data'})

    # TODO test 'If-Range' with GET
    # TODO test multiple ranges in 'Range' with GET


  # test BigFile's .data property can be of several types and is handled
  # properly and we can still get data and migrate to BTreeData transparently
  # (called from under testBigFile_02_DataVarious driver)
  def _testBigFile_02_DataVarious(self):
    # BigFile's .data can be:
    # str       - because data comes from Data property sheet and default value is ''
    # None      - because it can be changed
    # BTreeData - because it is scalable way to work with large content
    #
    # str can be possibly non-empty because we could want to transparently
    # migrate plain File documents to BigFiles.
    #
    # make sure BigFile correctly works in all those situations.

    big_file_module = self.getPortal().big_file_module
    f = big_file_module.newContent(portal_type='Big File')
    check = lambda *args: self.checkRequest(f, *args)

    # after creation .data is ''  (as per default from Data property sheet)
    _ = f._baseGetData()
    self.assertIsInstance(_, str)
    self.assertEqual(_, '')

    # make sure we can get empty content through all ways
    # (already covered in testBigFile_01_Basic, but still)
    self.assertEqual(f.getSize(), 0)
    self.assertEqual(f.getData(), '')
    check(get(), {'format': 'raw'},                 '', '', 200, {'Content-Length': '0'})
    check(put({'Content-Range': 'bytes */*'}),{},   '', '',R308, {                                'Range': 'bytes 0--1'})  # XXX 0--1 ok?
    check(get({        'Range': 'bytes=0-0'}),{},   '', '', 416, {'Content-Length': '0',  'Content-Range': 'bytes */0'})


    # set .data to non-empty str and make sure we can get content through all ways
    f._baseSetData('abc')
    _ = f._baseGetData()
    self.assertIsInstance(_, str)
    self.assertEqual(_, 'abc')
    self.assertEqual(f.getSize(), 3)
    self.assertEqual(f.getData(), 'abc')
    check(get(), {'format': 'raw'},                 'abc', '',    200, {'Content-Length': '3'})
    check(put({'Content-Range': 'bytes */*'}),{},   ''   , '',   R308, {                                'Range': 'bytes 0-2'})
    check(get({        'Range': 'bytes=0-2'}),{},   ''   , 'abc', 206, {'Content-Length': '3',  'Content-Range': 'bytes 0-2/3'})

    # and .data should remain str after access (though later this could be
    # changed to transparently migrate to BTreeData)
    _ = f._baseGetData()
    self.assertIsInstance(_, str)
    self.assertEqual(_, 'abc')


    # on append .data should migrate to BTreeData
    f._appendData('d')
    _ = f._baseGetData()
    self.assertIsInstance(_, BTreeData)
    self.assertEqual(f.getSize(), 4)
    self.assertEqual(f.getData(), 'abcd')
    check(get(), {'format': 'raw'},                 '', 'abcd', 200, {'Content-Length': '4'})
    check(put({'Content-Range': 'bytes */*'}),{},   '', '',    R308, {                                'Range': 'bytes 0-3'})
    check(get({        'Range': 'bytes=0-3'}),{},   '', 'abcd', 206, {'Content-Length': '4',  'Content-Range': 'bytes 0-3/4'})



    # change .data to None and make sure we can still get empty content
    # NOTE additionally to ._baseSetData(None), ._setData(None) also sets
    #      .size=0 which is needed for correct BigFile bases operation.
    #
    #      see ERP5.Document.File._setSize() for details.
    f._setData(None)
    # NOTE still '' because it is default value specified in Data property
    #      sheet for .data field
    _ = f._baseGetData()
    self.assertIsInstance(_, str)
    self.assertEqual(_, '')
    # but we can change property sheet default on the fly
    # XXX ( only for this particular getter _baseGetData -
    #       - because property type information is not stored in one place,
    #       but is copied on getter/setter initialization - see Getter/Setter
    #       in ERP5Type.Accessor.Base )
    # NOTE this change is automatically reverted back in calling helper
    self.assertIsInstance(f._baseGetData._default, str)
    self.assertEqual(f._baseGetData._default, '')
    f._baseGetData.im_func._default = None  # NOTE not possible to do on just f._baseGetData
    self.assertIs(f._baseGetData._default, None)
    self.assertIs(f._baseGetData(), None)   # <- oops

    self.assertEqual(f.getSize(), 0)
    self.assertIs   (f.getData(), None)
    check(get(), {'format': 'raw'},                 '', '', 200, {'Content-Length': '0'})
    check(put({'Content-Range': 'bytes */*'}),{},   '', '',R308, {                                'Range': 'bytes 0--1'})  # XXX 0--1 ok?
    check(get({        'Range': 'bytes=0-0'}),{},   '', '', 416, {'Content-Length': '0',  'Content-Range': 'bytes */0'})


    # on append .data should become BTreeData
    f._appendData('x')
    _ = f._baseGetData()
    self.assertIsInstance(_, BTreeData)
    self.assertEqual(f.getSize(), 1)
    self.assertEqual(f.getData(), 'x')
    check(get(), {'format': 'raw'},                 '', 'x',    200, {'Content-Length': '1'})
    check(put({'Content-Range': 'bytes */*'}),{},   '', '',    R308, {                                'Range': 'bytes 0-0'})
    check(get({        'Range': 'bytes=0-3'}),{},   '', 'x',    206, {'Content-Length': '1',  'Content-Range': 'bytes 0-0/1'})



  # helper to call _testBigFile_02_DataVarious() and restore .data._default
  def testBigFile_02_DataVarious(self):
    big_file_module = self.getPortal().big_file_module
    f = big_file_module.newContent(portal_type='Big File')

    # Data property sheet specifies .data default to ''
    _ = f._baseGetData()
    self.assertIsInstance(_, str)
    self.assertEqual(_, '')

    # NOTE obtaining getter is not possible via BigFile._baseGetData
    g = f._baseGetData.im_func
    self.assertIsInstance(g._default, str)
    self.assertEqual(g._default, '')

    try:
      self._testBigFile_02_DataVarious()

    # restore ._baseGetData._default and make sure restoration really worked
    finally:
      g._default = ''
      f._baseSetData(None)    # so that we are sure getter returns class defaults
      _ = f._baseGetData()
      self.assertIsInstance(_, str)
      self.assertEqual(_, '')



  # TODO write big data to file and ensure it still works
