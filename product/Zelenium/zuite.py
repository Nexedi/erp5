""" Classes:  Zuite

Zuite instances are collections of Zelenium test cases.

$Id$
"""
import glob
import logging
import os
import re
from urllib import unquote
import zipfile
import StringIO
import types

from zope.interface import implements

from AccessControl.SecurityInfo import ClassSecurityInfo
from App.class_init import InitializeClass
from App.Common import package_home
from App.config import getConfiguration
from App.ImageFile import ImageFile
from App.special_dtml import DTMLFile
from DateTime.DateTime import DateTime
from OFS.Folder import Folder
from OFS.Image import File
from OFS.OrderedFolder import OrderedFolder
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from interfaces import IZuite
from permissions import ManageSeleniumTestCases
from permissions import View

logger = logging.getLogger('event.Zelenium')

_NOW = None   # set only for testing

_PINK_BACKGROUND = re.compile('bgcolor="#ffcfcf"')

_EXCLUDE_NAMES = ( 'CVS', '.svn', '.objects' )

#winzip awaits latin1
_DEFAULTENCODING = 'latin1'


def _getNow():
    if _NOW is not None:
        return _NOW

    return DateTime()

_WWW_DIR = os.path.join( package_home( globals() ), 'www' )

#
#   Selenium support files.
#
_SUPPORT_DIR = os.path.join( package_home( globals() ), 'selenium' )
_SUPPORT_FILES = {}

def _makeFile(filename, prefix=None, id=None):

    if prefix:
        path = os.path.join( prefix, filename )
    else:
        path = filename

    if id is None:
        id = os.path.split( path )[ 1 ]

    return File( id=id, title='', file=open(path).read() )


def registerFiles(directory, prefix):
    for filename in os.listdir(directory):
        ignored, extension = os.path.splitext(filename)

        if extension.lower() in ('.js', '.html', '.css', '.png'):
            _SUPPORT_FILES['%s_%s' % (prefix, filename)] = _makeFile( filename, prefix=directory)

_MARKER = object()


def _recurseFSTestCases( result, prefix, fsobjs ):

    test_cases = dict( [ ( x.getId(), x )
                            for x in fsobjs.get( 'testcases', () ) ] )
    subdirs = fsobjs.get( 'subdirs', {} )

    for name in fsobjs.get( 'ordered', [] ):

        if name in test_cases:
            test_case = test_cases[ name ]
            name = test_case.getId()
            path = '/'.join( prefix + ( name, ) )
            result.append( { 'id' : name
                            , 'title' : test_case.title_or_id()
                            , 'url' : path
                            , 'path' : path
                            , 'test_case' : test_case
                            } )

        if name in subdirs:
            info = subdirs[ name ]
            _recurseFSTestCases( result
                               , prefix + ( name, )
                               , info
                               )

class Zuite( OrderedFolder ):
    """ TTW-manageable browser test suite

    A Zuite instance is an ordered folder, whose 'index_html' provides the
    typical "TestRunner.html" view from Selenium.  It generates the
    "TestSuite.html" view from its 'objectItems' list (which allows the
    user to control ordering), selecting File and PageTemplate objects
    whose names start with 'test'.
    """
    meta_type = 'Zuite'

    manage_options = ( OrderedFolder.manage_options
                     + ( { 'label' : 'Zip', 'action' : 'manage_zipfile' },
                       )
                     )

    implements(IZuite)

    test_case_metatypes = ( 'File'
                          , 'Page Template'
                          )
    filesystem_path = ''
    filename_glob = ''
    testsuite_name = ''
    _v_filesystem_objects = None
    _v_selenium_objects = None

    _properties = ( { 'id' : 'test_case_metatypes'
                    , 'type' : 'lines'
                    , 'mode' : 'w'
                    }
                  , { 'id' : 'filesystem_path'
                    , 'type' : 'string'
                    , 'mode' : 'w'
                    }
                  , { 'id' : 'filename_glob'
                    , 'type' : 'string'
                    , 'mode' : 'w'
                    }
                  , { 'id' : 'testsuite_name'
                    , 'type' : 'string'
                    , 'mode' : 'w'
                    }
                  )

    security = ClassSecurityInfo()
    security.declareObjectProtected( View )

    security.declareProtected( ManageSeleniumTestCases, 'manage_main' )
    manage_main = DTMLFile( 'suiteMain', _WWW_DIR )

    security.declareProtected( View, 'index_html' )
    index_html = PageTemplateFile( 'suiteView', _WWW_DIR )

    security.declareProtected( View, 'test_suite_html' )
    test_suite_html = PageTemplateFile( 'suiteTests', _WWW_DIR )

    security.declareProtected( View, 'splash_html' )
    splash_html = PageTemplateFile( 'suiteSplash', _WWW_DIR )

    security.declareProtected( View, 'test_prompt_html' )
    test_prompt_html = PageTemplateFile( 'testPrompt', _WWW_DIR )

    security.declareProtected(ManageSeleniumTestCases, 'manage_zipfile')
    manage_zipfile = PageTemplateFile( 'suiteZipFile', _WWW_DIR )


    def __getitem__( self, key, default=_MARKER ):

        if key in self.objectIds():
            return self._getOb( key )

        if key in _SUPPORT_FILES.keys():
            return _SUPPORT_FILES[ key ].__of__( self )

        proxy = _FilesystemProxy( key
                                , self._listFilesystemObjects()
                                ).__of__( self )

        localdefault = object()

        value = proxy.get( key, localdefault )

        if value is not localdefault:
            return value

        proxy = _FilesystemProxy( key
                                , self._listSeleniumObjects()
                                ).__of__( self )

        value = proxy.get( key, default )

        if value is not _MARKER:
            return value

        raise KeyError, key


    security.declareProtected( View, 'listTestCases' )
    def listTestCases( self, prefix=() ):
        """ Return a list of our contents which qualify as test cases.
        """
        result = []
        self._recurseListTestCases(result, prefix, self)
        return result

    def _recurseListTestCases( self, result, prefix, ob ):
        for tcid, test_case in ob.objectItems():
            if isinstance( test_case, self.__class__ ):
                result.extend( test_case.listTestCases(
                                        prefix=prefix + ( tcid, ) ) )
            elif test_case.isPrincipiaFolderish:
                self._recurseListTestCases(result, prefix+(tcid,), test_case)
            elif test_case.meta_type in self.test_case_metatypes:
                path = '/'.join( prefix + ( tcid, ) )
                result.append( { 'id' : tcid
                               , 'title' : test_case.title_or_id()
                               , 'url' : path
                               , 'path' : path
                               , 'test_case' : test_case
                               } )

        fsobjs = self._listFilesystemObjects()

        _recurseFSTestCases( result, prefix, fsobjs )


    security.declareProtected(ManageSeleniumTestCases, 'getZipFileName')
    def getZipFileName(self):
        """ Generate a suitable name for the zip file.
        """
        now = _getNow()
        now_str = now.ISO()[:10]
        return '%s-%s.zip' % ( self.getId(), now_str )


    security.declareProtected(ManageSeleniumTestCases, 'manage_getZipFile')
    def manage_getZipFile( self
                         , archive_name=None
                         , include_selenium=True
                         , RESPONSE=None
                         ):
        """ Export the test suite as a zip file.
        """
        if archive_name is None or archive_name.strip() == '':
            archive_name = self.getZipFileName()

        bits = self._getZipFile( include_selenium )

        if RESPONSE is None:
            return bits

        RESPONSE.setHeader('Content-type', 'application/zip')
        RESPONSE.setHeader('Content-disposition',
                            'inline;filename=%s' % archive_name )
        return bits


    security.declareProtected(ManageSeleniumTestCases, 'manage_createSnapshot')
    def manage_createSnapshot( self
                             , archive_name=None
                             , include_selenium=True
                             , RESPONSE=None
                             ):
        """ Save the test suite as a zip file *in the zuite*.
        """
        if archive_name is None or archive_name.strip() == '':
            archive_name = self.getZipFileName()

        archive = File( archive_name
                      , title=''
                      , file=self._getZipFile( include_selenium )
                      )
        self._setObject( archive_name, archive )

        if RESPONSE is not None:
            RESPONSE.redirect( '%s/manage_main?manage_tabs_message=%s'
                              % ( self.absolute_url()
                                , 'Snapshot+added'
                                ) )


    security.declarePublic('postResults')
    def postResults(self, REQUEST):
        """ Record the results of a test run.

        o Create a folder with properties representing the summary results,
          and files containing the suite and the individual test runs.

        o REQUEST will have the following form fields:

          result -- one of "failed" or "passed"

          totalTime -- time in floating point seconds for the run

          numTestPasses -- count of test runs which passed

          numTestFailures -- count of test runs which failed

          numCommandPasses -- count of commands which passed

          numCommandFailures -- count of commands which failed

          numCommandErrors -- count of commands raising non-assert errors

          suite -- Colorized HTML of the suite table

          testTable.<n> -- Colorized HTML of each test run
        """
        completed = DateTime()
        result_id = 'result_%s' % completed.strftime( '%Y%m%d_%H%M%S.%f' )
        self._setObject( result_id, ZuiteResults( result_id ) )
        result = self._getOb( result_id )
        rfg = REQUEST.form.get
        reg = REQUEST.environ.get

        result._updateProperty( 'completed'
                              , completed
                              )

        result._updateProperty( 'passed'
                              , rfg( 'result' ).lower() == 'passed'
                              )

        result._updateProperty( 'finished'
                              , rfg( 'finished' ).lower() == 'true'
                              )

        result._updateProperty( 'time_secs'
                              , float( rfg( 'totalTime', 0 ) )
                              )

        result._updateProperty( 'tests_passed'
                              , int( rfg( 'numTestPasses', 0 ) )
                              )

        result._updateProperty( 'tests_failed'
                              , int( rfg( 'numTestFailures', 0 ) )
                              )

        result._updateProperty( 'commands_passed'
                              , int( rfg( 'numCommandPasses', 0 ) )
                              )

        result._updateProperty( 'commands_failed'
                              , int( rfg( 'numCommandFailures', 0 ) )
                              )

        result._updateProperty( 'commands_with_errors'
                              , int( rfg( 'numCommandErrors', 0 ) )
                              )

        result._updateProperty( 'user_agent'
                              , reg( 'HTTP_USER_AGENT', 'unknown' )
                              )

        result._updateProperty( 'remote_addr'
                              , reg( 'REMOTE_ADDR', 'unknown' )
                              )

        result._updateProperty( 'http_host'
                              , reg( 'HTTP_HOST', 'unknown' )
                              )

        result._updateProperty( 'server_software'
                              , reg( 'SERVER_SOFTWARE', 'unknown' )
                              )

        result._updateProperty( 'product_info'
                              , self._listProductInfo()
                              )

        result._setObject( 'suite.html'
                         , File( 'suite.html'
                               , 'Test Suite'
                               , unquote( rfg( 'suite' ) )
                               , 'text/html'
                               )
                         )

        test_ids = [ x for x in REQUEST.form.keys()
                        if x.startswith( 'testTable' ) ]
        test_ids.sort()

        for test_id in test_ids:
            body = unquote( rfg( test_id ) )
            result._setObject( test_id
                             , File( test_id
                                   , 'Test case: %s' % test_id
                                   , body
                                   , 'text/html'
                                   ) )
            testcase = result._getOb( test_id )

            # XXX:  this is silly, but we have no other metadata.
            testcase._setProperty( 'passed'
                                 , _PINK_BACKGROUND.search( body ) is None
                                 , 'boolean'
                                 )


    #
    #   Helper methods
    #
    security.declarePrivate('_listFilesystemObjects')
    def _listFilesystemObjects( self ):
        """ Return a mapping of any filesystem objects we "hold".
        """
        if ( self._v_filesystem_objects is not None and
             not getConfiguration().debug_mode ):
            return self._v_filesystem_objects

        if not self.filesystem_path:
            return { 'testcases' : (), 'subdirs' : {} }

        path = os.path.abspath( self.filesystem_path )

        self._v_filesystem_objects = self._grubFilesystem( path )
        return self._v_filesystem_objects

    security.declarePrivate('_listSeleniumObjects')
    def _listSeleniumObjects( self ):
        """ Return a mapping of any filesystem objects we "hold".
        """
        if ( self._v_selenium_objects is not None and
             not getConfiguration().debug_mode ):
            return self._v_selenium_objects

        self._v_selenium_objects = self._grubFilesystem(_SUPPORT_DIR)
        return self._v_selenium_objects

    security.declarePrivate('_grubFilesystem')
    def _grubFilesystem( self, path ):

        info = { 'testcases' : (), 'subdirs' : {} }

        # Look for a specified test suite
        # or a '.objects' file with an explicit manifiest
        manifest = os.path.join( path, self.testsuite_name or '.objects' )

        if os.path.isfile( manifest ):
            filenames = filter(None,[ x.strip() for x in open( manifest ).readlines() ])

        elif self.filename_glob:
            globbed = glob.glob( os.path.join( path, self.filename_glob ) )
            filenames = [ os.path.split( x )[ 1 ] for x in globbed ]

        else:   # guess
            filenames = [ x for x in os.listdir( path )
                                if x not in _EXCLUDE_NAMES ]
            filenames.sort()

        info[ 'ordered' ] = filenames

        for name in filenames:

            fqfn = os.path.join( path, name )

            if os.path.isfile( fqfn ):
                testcase = _makeFile( fqfn )
                info[ 'testcases' ] += ( testcase, )

            elif os.path.isdir( fqfn ):
                info[ 'subdirs' ][ name ] = self._grubFilesystem( fqfn )

            else:

                logger.warning(
                    '%r was neither a file nor directory and so has been ignored',
                    fqfn
                    )

        return info


    security.declarePrivate('_getFilename')
    def _getFilename(self, name):
        """ Convert 'name' to a suitable filename, if needed.
        """
        if '.' not in name:
            return '%s.html' % name

        return name


    security.declarePrivate( '_getZipFile' )
    def _getZipFile( self, include_selenium=True ):
        """ Generate a zip file containing both tests and scaffolding.
        """
        stream = StringIO.StringIO()
        archive = zipfile.ZipFile( stream, 'w' )


        def convertToBytes(body):
            if isinstance(body, types.UnicodeType):
                return body.encode(_DEFAULTENCODING)
            else:
                return body

        archive.writestr( 'index.html'
                        , convertToBytes(self.index_html( suite_name='testSuite.html' ) ) )

        test_cases = self.listTestCases()

        paths = { '' : [] }

        def _ensurePath( prefix, element ):
            elements = paths.setdefault( prefix, [] )
            if element not in elements:
                elements.append( element )

        for info in test_cases:
            # ensure suffixes
            path = self._getFilename( info[ 'path' ] )
            info[ 'path' ] = path
            info[ 'url' ] = self._getFilename( info[ 'url' ] )

            elements = path.split( os.path.sep )
            _ensurePath( '', elements[ 0 ] )

            for i in range( 1, len( elements ) ):
                prefix = '/'.join( elements[ : i ] )
                _ensurePath( prefix, elements[ i ] )

        archive.writestr( 'testSuite.html'
                        , convertToBytes(self.test_suite_html( test_cases=test_cases ) ) )

        for pathname, filenames in paths.items():

            if pathname == '':
                filename = '.objects'
            else:
                filename = '%s/.objects' % pathname

            archive.writestr( convertToBytes(filename)
                            , convertToBytes(u'\n'.join( filenames ) ) )

        for info in test_cases:
            test_case = info[ 'test_case' ]

            if getattr( test_case, '__call__', None ) is not None:
                body = test_case()  # XXX: DTML?
            else:
                body = test_case.manage_FTPget()

            archive.writestr( convertToBytes(info[ 'path' ])
                            , convertToBytes(body) )

        if include_selenium:

            for k, v in _SUPPORT_FILES.items():
                archive.writestr( convertToBytes(k),
                       convertToBytes(v.__of__(self).manage_FTPget() ) )

        archive.close()
        return stream.getvalue()

    security.declarePrivate('_listProductInfo')
    def _listProductInfo( self ):
        """ Return a list of strings of form '%(name)s %(version)s'.

        o Each line describes one product installed in the Control_Panel.
        """
        result = []
        cp = self.getPhysicalRoot().Control_Panel
        products = cp.Products.objectItems()
        products.sort()

        for product_name, product in products:
            version = product.version or 'unreleased'
            result.append( '%s %s' % ( product_name, version ) )

        return result


InitializeClass( Zuite )


class ZuiteResults( Folder ):

    security = ClassSecurityInfo()
    meta_type = 'Zuite Results'

    _properties = ( { 'id' : 'test_case_metatypes'
                    , 'type' : 'lines'
                    , 'mode' : 'w'
                    },
                    { 'id' : 'completed'
                    , 'type' : 'date'
                    , 'mode' : 'w'
                    },
                    { 'id' : 'finished'
                    , 'type' : 'boolean'
                    , 'mode' : 'w'
                    },
                    { 'id' : 'passed'
                    , 'type' : 'boolean'
                    , 'mode' : 'w'
                    },
                    { 'id' : 'time_secs'
                    , 'type' : 'float'
                    , 'mode' : 'w'
                    },
                    { 'id' : 'tests_passed'
                    , 'type' : 'int'
                    , 'mode' : 'w'
                    },
                    { 'id' : 'tests_failed'
                    , 'type' : 'int'
                    , 'mode' : 'w'
                    },
                    { 'id' : 'commands_passed'
                    , 'type' : 'int'
                    , 'mode' : 'w'
                    },
                    { 'id' : 'commands_failed'
                    , 'type' : 'int'
                    , 'mode' : 'w'
                    },
                    { 'id' : 'commands_with_errors'
                    , 'type' : 'int'
                    , 'mode' : 'w'
                    },
                    { 'id' : 'user_agent'
                    , 'type' : 'string'
                    , 'mode' : 'w'
                    },
                    { 'id' : 'remote_addr'
                    , 'type' : 'string'
                    , 'mode' : 'w'
                    },
                    { 'id' : 'http_host'
                    , 'type' : 'string'
                    , 'mode' : 'w'
                    },
                    { 'id' : 'server_software'
                    , 'type' : 'string'
                    , 'mode' : 'w'
                    },
                    { 'id' : 'product_info'
                    , 'type' : 'lines'
                    , 'mode' : 'w'
                    },
                  )

    security.declareObjectProtected( View )

    security.declarePublic( 'index_html' )
    index_html = PageTemplateFile( 'resultsView', _WWW_DIR )

    security.declareProtected( View, 'error_icon' )
    error_icon = ImageFile( 'error.gif', _WWW_DIR )

    security.declareProtected( View, 'check_icon' )
    check_icon = ImageFile( 'check.gif', _WWW_DIR )


    def __getitem__( self, key, default=_MARKER ):

        if key in self.objectIds():
            return self._getOb( key )

        if key == 'error.gif':
            return self.error_icon

        if key == 'check.gif':
            return self.check_icon

        if default is not _MARKER:
            return default

        raise KeyError, key

InitializeClass( ZuiteResults )

class _FilesystemProxy( Folder ):

    security = ClassSecurityInfo()

    def __init__( self, id, fsobjs ):

        self._setId( id )
        self._fsobjs = fsobjs

    def __getitem__( self, key ):

        return self.get( key )

    security.declareProtected( View, 'index_html' )
    index_html = PageTemplateFile( 'suiteView', _WWW_DIR )

    security.declareProtected( View, 'test_suite_html' )
    test_suite_html = PageTemplateFile( 'suiteTests', _WWW_DIR )

    security.declareProtected( View, 'get' )
    def get( self, key, default=_MARKER ):

        for tc in self._fsobjs[ 'testcases' ]:
            if tc.getId() == key:
                return tc.__of__( self.aq_parent )

        if key in self._fsobjs[ 'subdirs' ]:
            return self.__class__( key, self._fsobjs[ 'subdirs' ][ key ]
                                 ).__of__( self.aq_parent )

        if key in _SUPPORT_FILES.keys():
            return _SUPPORT_FILES[ key ].__of__( self )

        if default is not _MARKER:
            return default

        raise KeyError, key

    security.declareProtected( View, 'listTestCases' )
    def listTestCases( self, prefix=() ):
        """ Return a list of our contents which qualify as test cases.
        """
        result = []
        _recurseFSTestCases( result, prefix, self._fsobjs )
        return result

InitializeClass( _FilesystemProxy )

#
#   Factory methods
#
manage_addZuiteForm = PageTemplateFile( 'addZuite', _WWW_DIR )

def manage_addZuite(dispatcher, id, title='', REQUEST=None):
    """ Add a new Zuite to dispatcher's objects.
    """
    zuite = Zuite(id)
    zuite.title = title
    dispatcher._setObject(id, zuite)
    zuite = dispatcher._getOb(id)

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect('%s/manage_main'
                                       % zuite.absolute_url() )
