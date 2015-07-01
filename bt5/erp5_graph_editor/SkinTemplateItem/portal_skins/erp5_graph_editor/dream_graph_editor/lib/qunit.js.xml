<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="File" module="OFS.Image"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>_Cacheable__manager_id</string> </key>
            <value> <string>http_cache</string> </value>
        </item>
        <item>
            <key> <string>_EtagSupport__etag</string> </key>
            <value> <string>ts25570623.48</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>qunit.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value>
              <persistent> <string encoding="base64">AAAAAAAAAAI=</string> </persistent>
            </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>71721</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
  <record id="2" aka="AAAAAAAAAAI=">
    <pickle>
      <global name="Pdata" module="OFS.Image"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*!\n
 * QUnit 1.17.1\n
 * http://qunitjs.com/\n
 *\n
 * Copyright jQuery Foundation and other contributors\n
 * Released under the MIT license\n
 * http://jquery.org/license\n
 *\n
 * Date: 2015-01-20T19:39Z\n
 */\n
\n
(function( window ) {\n
\n
var QUnit,\n
\tconfig,\n
\tonErrorFnPrev,\n
\tloggingCallbacks = {},\n
\tfileName = ( sourceFromStacktrace( 0 ) || "" ).replace( /(:\\d+)+\\)?/, "" ).replace( /.+\\//, "" ),\n
\ttoString = Object.prototype.toString,\n
\thasOwn = Object.prototype.hasOwnProperty,\n
\t// Keep a local reference to Date (GH-283)\n
\tDate = window.Date,\n
\tnow = Date.now || function() {\n
\t\treturn new Date().getTime();\n
\t},\n
\tglobalStartCalled = false,\n
\trunStarted = false,\n
\tsetTimeout = window.setTimeout,\n
\tclearTimeout = window.clearTimeout,\n
\tdefined = {\n
\t\tdocument: window.document !== undefined,\n
\t\tsetTimeout: window.setTimeout !== undefined,\n
\t\tsessionStorage: (function() {\n
\t\t\tvar x = "qunit-test-string";\n
\t\t\ttry {\n
\t\t\t\tsessionStorage.setItem( x, x );\n
\t\t\t\tsessionStorage.removeItem( x );\n
\t\t\t\treturn true;\n
\t\t\t} catch ( e ) {\n
\t\t\t\treturn false;\n
\t\t\t}\n
\t\t}())\n
\t},\n
\t/**\n
\t * Provides a normalized error string, correcting an issue\n
\t * with IE 7 (and prior) where Error.prototype.toString is\n
\t * not properly implemented\n
\t *\n
\t * Based on http://es5.github.com/#x15.11.4.4\n
\t *\n
\t * @param {String|Error} error\n
\t * @return {String} error message\n
\t */\n
\terrorString = function( error ) {\n
\t\tvar name, message,\n
\t\t\terrorString = error.toString();\n
\t\tif ( errorString.substring( 0, 7 ) === "[object" ) {\n
\t\t\tname = error.name ? error.name.toString() : "Error";\n
\t\t\tmessage = error.message ? error.message.toString() : "";\n
\t\t\tif ( name && message ) {\n
\t\t\t\treturn name + ": " + message;\n
\t\t\t} else if ( name ) {\n
\t\t\t\treturn name;\n
\t\t\t} else if ( message ) {\n
\t\t\t\treturn message;\n
\t\t\t} else {\n
\t\t\t\treturn "Error";\n
\t\t\t}\n
\t\t} else {\n
\t\t\treturn errorString;\n
\t\t}\n
\t},\n
\t/**\n
\t * Makes a clone of an object using only Array or Object as base,\n
\t * and copies over the own enumerable properties.\n
\t *\n
\t * @param {Object} obj\n
\t * @return {Object} New object with only the own properties (recursively).\n
\t */\n
\tobjectValues = function( obj ) {\n
\t\tvar key, val,\n
\t\t\tvals = QUnit.is( "array", obj ) ? [] : {};\n
\t\tfor ( key in obj ) {\n
\t\t\tif ( hasOwn.call( obj, key ) ) {\n
\t\t\t\tval = obj[ key ];\n
\t\t\t\tvals[ key ] = val === Object( val ) ? objectValues( val ) : val;\n
\t\t\t}\n
\t\t}\n
\t\treturn vals;\n
\t};\n
\n
QUnit = {};\n
\n
/**\n
 * Config object: Maintain internal state\n
 * Later exposed as QUnit.config\n
 * `config` initialized at top of scope\n
 */\n
config = {\n
\t// The queue of tests to run\n
\tqueue: [],\n
\n
\t// block until document ready\n
\tblocking: true,\n
\n
\t// by default, run previously failed tests first\n
\t// very useful in combination with "Hide passed tests" checked\n
\treorder: true,\n
\n
\t// by default, modify document.title when suite is done\n
\taltertitle: true,\n
\n
\t// by default, scroll to top of the page when suite is done\n
\tscrolltop: true,\n
\n
\t// when enabled, all tests must call expect()\n
\trequireExpects: false,\n
\n
\t// add checkboxes that are persisted in the query-string\n
\t// when enabled, the id is set to `true` as a `QUnit.config` property\n
\turlConfig: [\n
\t\t{\n
\t\t\tid: "hidepassed",\n
\t\t\tlabel: "Hide passed tests",\n
\t\t\ttooltip: "Only show tests and assertions that fail. Stored as query-strings."\n
\t\t},\n
\t\t{\n
\t\t\tid: "noglobals",\n
\t\t\tlabel: "Check for Globals",\n
\t\t\ttooltip: "Enabling this will test if any test introduces new properties on the " +\n
\t\t\t\t"`window` object. Stored as query-strings."\n
\t\t},\n
\t\t{\n
\t\t\tid: "notrycatch",\n
\t\t\tlabel: "No try-catch",\n
\t\t\ttooltip: "Enabling this will run tests outside of a try-catch block. Makes debugging " +\n
\t\t\t\t"exceptions in IE reasonable. Stored as query-strings."\n
\t\t}\n
\t],\n
\n
\t// Set of all modules.\n
\tmodules: [],\n
\n
\t// The first unnamed module\n
\tcurrentModule: {\n
\t\tname: "",\n
\t\ttests: []\n
\t},\n
\n
\tcallbacks: {}\n
};\n
\n
// Push a loose unnamed module to the modules collection\n
config.modules.push( config.currentModule );\n
\n
// Initialize more QUnit.config and QUnit.urlParams\n
(function() {\n
\tvar i, current,\n
\t\tlocation = window.location || { search: "", protocol: "file:" },\n
\t\tparams = location.search.slice( 1 ).split( "&" ),\n
\t\tlength = params.length,\n
\t\turlParams = {};\n
\n
\tif ( params[ 0 ] ) {\n
\t\tfor ( i = 0; i < length; i++ ) {\n
\t\t\tcurrent = params[ i ].split( "=" );\n
\t\t\tcurrent[ 0 ] = decodeURIComponent( current[ 0 ] );\n
\n
\t\t\t// allow just a key to turn on a flag, e.g., test.html?noglobals\n
\t\t\tcurrent[ 1 ] = current[ 1 ] ? decodeURIComponent( current[ 1 ] ) : true;\n
\t\t\tif ( urlParams[ current[ 0 ] ] ) {\n
\t\t\t\turlParams[ current[ 0 ] ] = [].concat( urlParams[ current[ 0 ] ], current[ 1 ] );\n
\t\t\t} else {\n
\t\t\t\turlParams[ current[ 0 ] ] = current[ 1 ];\n
\t\t\t}\n
\t\t}\n
\t}\n
\n
\tif ( urlParams.filter === true ) {\n
\t\tdelete urlParams.filter;\n
\t}\n
\n
\tQUnit.urlParams = urlParams;\n
\n
\t// String search anywhere in moduleName+testName\n
\tconfig.filter = urlParams.filter;\n
\n
\tconfig.testId = [];\n
\tif ( urlParams.testId ) {\n
\n
\t\t// Ensure that urlParams.testId is an array\n
\t\turlParams.testId = [].concat( urlParams.testId );\n
\t\tfor ( i = 0; i < urlParams.testId.length; i++ ) {\n
\t\t\tconfig.testId.push( urlParams.testId[ i ] );\n
\t\t}\n
\t}\n
\n
\t// Figure out if we\'re running the tests from a server or not\n
\tQUnit.isLocal = location.protocol === "file:";\n
}());\n
\n
// Root QUnit object.\n
// `QUnit` initialized at top of scope\n
extend( QUnit, {\n
\n
\t// call on start of module test to prepend name to all tests\n
\tmodule: function( name, testEnvironment ) {\n
\t\tvar currentModule = {\n
\t\t\tname: name,\n
\t\t\ttestEnvironment: testEnvironment,\n
\t\t\ttests: []\n
\t\t};\n
\n
\t\t// DEPRECATED: handles setup/teardown functions,\n
\t\t// beforeEach and afterEach should be used instead\n
\t\tif ( testEnvironment && testEnvironment.setup ) {\n
\t\t\ttestEnvironment.beforeEach = testEnvironment.setup;\n
\t\t\tdelete testEnvironment.setup;\n
\t\t}\n
\t\tif ( testEnvironment && testEnvironment.teardown ) {\n
\t\t\ttestEnvironment.afterEach = testEnvironment.teardown;\n
\t\t\tdelete testEnvironment.teardown;\n
\t\t}\n
\n
\t\tconfig.modules.push( currentModule );\n
\t\tconfig.currentModule = currentModule;\n
\t},\n
\n
\t// DEPRECATED: QUnit.asyncTest() will be removed in QUnit 2.0.\n
\tasyncTest: function( testName, expected, callback ) {\n
\t\tif ( arguments.length === 2 ) {\n
\t\t\tcallback = expected;\n
\t\t\texpected = null;\n
\t\t}\n
\n
\t\tQUnit.test( testName, expected, callback, true );\n
\t},\n
\n
\ttest: function( testName, expected, callback, async ) {\n
\t\tvar test;\n
\n
\t\tif ( arguments.length === 2 ) {\n
\t\t\tcallback = expected;\n
\t\t\texpected = null;\n
\t\t}\n
\n
\t\ttest = new Test({\n
\t\t\ttestName: testName,\n
\t\t\texpected: expected,\n
\t\t\tasync: async,\n
\t\t\tcallback: callback\n
\t\t});\n
\n
\t\ttest.queue();\n
\t},\n
\n
\tskip: function( testName ) {\n
\t\tvar test = new Test({\n
\t\t\ttestName: testName,\n
\t\t\tskip: true\n
\t\t});\n
\n
\t\ttest.queue();\n
\t},\n
\n
\t// DEPRECATED: The functionality of QUnit.start() will be altered in QUnit 2.0.\n
\t// In QUnit 2.0, invoking it will ONLY affect the `QUnit.config.autostart` blocking behavior.\n
\tstart: function( count ) {\n
\t\tvar globalStartAlreadyCalled = globalStartCalled;\n
\n
\t\tif ( !config.current ) {\n
\t\t\tglobalStartCalled = true;\n
\n
\t\t\tif ( runStarted ) {\n
\t\t\t\tthrow new Error( "Called start() outside of a test context while already started" );\n
\t\t\t} else if ( globalStartAlreadyCalled || count > 1 ) {\n
\t\t\t\tthrow new Error( "Called start() outside of a test context too many times" );\n
\t\t\t} else if ( config.autostart ) {\n
\t\t\t\tthrow new Error( "Called start() outside of a test context when " +\n
\t\t\t\t\t"QUnit.config.autostart was true" );\n
\t\t\t} else if ( !config.pageLoaded ) {\n
\n
\t\t\t\t// The page isn\'t completely loaded yet, so bail out and let `QUnit.load` handle it\n
\t\t\t\tconfig.autostart = true;\n
\t\t\t\treturn;\n
\t\t\t}\n
\t\t} else {\n
\n
\t\t\t// If a test is running, adjust its semaphore\n
\t\t\tconfig.current.semaphore -= count || 1;\n
\n
\t\t\t// Don\'t start until equal number of stop-calls\n
\t\t\tif ( config.current.semaphore > 0 ) {\n
\t\t\t\treturn;\n
\t\t\t}\n
\n
\t\t\t// throw an Error if start is called more often than stop\n
\t\t\tif ( config.current.semaphore < 0 ) {\n
\t\t\t\tconfig.current.semaphore = 0;\n
\n
\t\t\t\tQUnit.pushFailure(\n
\t\t\t\t\t"Called start() while already started (test\'s semaphore was 0 already)",\n
\t\t\t\t\tsourceFromStacktrace( 2 )\n
\t\t\t\t);\n
\t\t\t\treturn;\n
\t\t\t}\n
\t\t}\n
\n
\t\tresumeProcessing();\n
\t},\n
\n
\t// DEPRECATED: QUnit.stop() will be removed in QUnit 2.0.\n
\tstop: function( count ) {\n
\n
\t\t// If there isn\'t a test running, don\'t allow QUnit.stop() to be called\n
\t\tif ( !config.current ) {\n
\t\t\tthrow new Error( "Called stop() outside of a test context" );\n
\t\t}\n
\n
\t\t// If a test is running, adjust its semaphore\n
\t\tconfig.current.semaphore += count || 1;\n
\n
\t\tpauseProcessing();\n
\t},\n
\n
\tconfig: config,\n
\n
\t// Safe object type checking\n
\tis: function( type, obj ) {\n
\t\treturn QUnit.objectType( obj ) === type;\n
\t},\n
\n
\tobjectType: function( obj ) {\n
\t\tif ( typeof obj === "undefined" ) {\n
\t\t\treturn "undefined";\n
\t\t}\n
\n
\t\t// Consider: typeof null === object\n
\t\tif ( obj === null ) {\n
\t\t\treturn "null";\n
\t\t}\n
\n
\t\tvar match = toString.call( obj ).match( /^\\[object\\s(.*)\\]$/ ),\n
\t\t\ttype = match && match[ 1 ] || "";\n
\n
\t\tswitch ( type ) {\n
\t\t\tcase "Number":\n
\t\t\t\tif ( isNaN( obj ) ) {\n
\t\t\t\t\treturn "nan";\n
\t\t\t\t}\n
\t\t\t\treturn "number";\n
\t\t\tcase "String":\n
\t\t\tcase "Boolean":\n
\t\t\tcase "Array":\n
\t\t\tcase "Date":\n
\t\t\tcase "RegExp":\n
\t\t\tcase "Function":\n
\t\t\t\treturn type.toLowerCase();\n
\t\t}\n
\t\tif ( typeof obj === "object" ) {\n
\t\t\treturn "object";\n
\t\t}\n
\t\treturn undefined;\n
\t},\n
\n
\textend: extend,\n
\n
\tload: function() {\n
\t\tconfig.pageLoaded = true;\n
\n
\t\t// Initialize the configuration options\n
\t\textend( config, {\n
\t\t\tstats: { all: 0, bad: 0 },\n
\t\t\tmoduleStats: { all: 0, bad: 0 },\n
\t\t\tstarted: 0,\n
\t\t\tupdateRate: 1000,\n
\t\t\tautostart: true,\n
\t\t\tfilter: ""\n
\t\t}, true );\n
\n
\t\tconfig.blocking = false;\n
\n
\t\tif ( config.autostart ) {\n
\t\t\tresumeProcessing();\n
\t\t}\n
\t}\n
});\n
\n
// Register logging callbacks\n
(function() {\n
\tvar i, l, key,\n
\t\tcallbacks = [ "begin", "done", "log", "testStart", "testDone",\n
\t\t\t"moduleStart", "moduleDone" ];\n
\n
\tfunction registerLoggingCallback( key ) {\n
\t\tvar loggingCallback = function( callback ) {\n
\t\t\tif ( QUnit.objectType( callback ) !== "function" ) {\n
\t\t\t\tthrow new Error(\n
\t\t\t\t\t"QUnit logging methods require a callback function as their first parameters."\n
\t\t\t\t);\n
\t\t\t}\n
\n
\t\t\tconfig.callbacks[ key ].push( callback );\n
\t\t};\n
\n
\t\t// DEPRECATED: This will be removed on QUnit 2.0.0+\n
\t\t// Stores the registered functions allowing restoring\n
\t\t// at verifyLoggingCallbacks() if modified\n
\t\tloggingCallbacks[ key ] = loggingCallback;\n
\n
\t\treturn loggingCallback;\n
\t}\n
\n
\tfor ( i = 0, l = callbacks.length; i < l; i++ ) {\n
\t\tkey = callbacks[ i ];\n
\n
\t\t// Initialize key collection of logging callback\n
\t\tif ( QUnit.objectType( config.callbacks[ key ] ) === "undefined" ) {\n
\t\t\tconfig.callbacks[ key ] = [];\n
\t\t}\n
\n
\t\tQUnit[ key ] = registerLoggingCallback( key );\n
\t}\n
})();\n
\n
// `onErrorFnPrev` initialized at top of scope\n
// Preserve other handlers\n
onErrorFnPrev = window.onerror;\n
\n
// Cover uncaught exceptions\n
// Returning true will suppress the default browser handler,\n
// returning false will let it run.\n
window.onerror = function( error, filePath, linerNr ) {\n
\tvar ret = false;\n
\tif ( onErrorFnPrev ) {\n
\t\tret = onErrorFnPrev( error, filePath, linerNr );\n
\t}\n
\n
\t// Treat return value as window.onerror itself does,\n
\t// Only do our handling if not suppressed.\n
\tif ( ret !== true ) {\n
\t\tif ( QUnit.config.current ) {\n
\t\t\tif ( QUnit.config.current.ignoreGlobalErrors ) {\n
\t\t\t\treturn true;\n
\t\t\t}\n
\t\t\tQUnit.pushFailure( error, filePath + ":" + linerNr );\n
\t\t} else {\n
\t\t\tQUnit.test( "global failure", extend(function() {\n
\t\t\t\tQUnit.pushFailure( error, filePath + ":" + linerNr );\n
\t\t\t}, { validTest: true } ) );\n
\t\t}\n
\t\treturn false;\n
\t}\n
\n
\treturn ret;\n
};\n
\n
function done() {\n
\tvar runtime, passed;\n
\n
\tconfig.autorun = true;\n
\n
\t// Log the last module results\n
\tif ( config.previousModule ) {\n
\t\trunLoggingCallbacks( "moduleDone", {\n
\t\t\tname: config.previousModule.name,\n
\t\t\ttests: config.previousModule.tests,\n
\t\t\tfailed: config.moduleStats.bad,\n
\t\t\tpassed: config.moduleStats.all - config.moduleStats.bad,\n
\t\t\ttotal: config.moduleStats.all,\n
\t\t\truntime: now() - config.moduleStats.started\n
\t\t});\n
\t}\n
\tdelete config.previousModule;\n
\n
\truntime = now() - config.started;\n
\tpassed = config.stats.all - config.stats.bad;\n
\n
\trunLoggingCallbacks( "done", {\n
\t\tfailed: config.stats.bad,\n
\t\tpassed: passed,\n
\t\ttotal: config.stats.all,\n
\t\truntime: runtime\n
\t});\n
}\n
\n
// Doesn\'t support IE6 to IE9\n
// See also https://developer.mozilla.org/en/JavaScript/Reference/Global_Objects/Error/Stack\n
function extractStacktrace( e, offset ) {\n
\toffset = offset === undefined ? 4 : offset;\n
\n
\tvar stack, include, i;\n
\n
\tif ( e.stacktrace ) {\n
\n
\t\t// Opera 12.x\n
\t\treturn e.stacktrace.split( "\\n" )[ offset + 3 ];\n
\t} else if ( e.stack ) {\n
\n
\t\t// Firefox, Chrome, Safari 6+, IE10+, PhantomJS and Node\n
\t\tstack = e.stack.split( "\\n" );\n
\t\tif ( /^error$/i.test( stack[ 0 ] ) ) {\n
\t\t\tstack.shift();\n
\t\t}\n
\t\tif ( fileName ) {\n
\t\t\tinclude = [];\n
\t\t\tfor ( i = offset; i < stack.length; i++ ) {\n
\t\t\t\tif ( stack[ i ].indexOf( fileName ) !== -1 ) {\n
\t\t\t\t\tbreak;\n
\t\t\t\t}\n
\t\t\t\tinclude.push( stack[ i ] );\n
\t\t\t}\n
\t\t\tif ( include.length ) {\n
\t\t\t\treturn include.join( "\\n" );\n
\t\t\t}\n
\t\t}\n
\t\treturn stack[ offset ];\n
\t} else if ( e.sourceURL ) {\n
\n
\t\t// Safari < 6\n
\t\t// exclude useless self-reference for generated Error objects\n
\t\tif ( /qunit.js$/.test( e.sourceURL ) ) {\n
\t\t\treturn;\n
\t\t}\n
\n
\t\t// for actual exceptions, this is useful\n
\t\treturn e.sourceURL + ":" + e.line;\n
\t}\n
}\n
\n
function sourceFromStacktrace( offset ) {\n
\tvar e = new Error();\n
\tif ( !e.stack ) {\n
\t\ttry {\n
\t\t\tthrow e;\n
\t\t} catch ( err ) {\n
\t\t\t// This should already be true in most browsers\n
\t\t\te = err;\n
\t\t}\n
\t}\n
\treturn extractStacktrace( e, offset );\n
}\n
\n
function synchronize( callback, last ) {\n
\tif ( QUnit.objectType( callback ) === "array" ) {\n
\t\twhile ( callback.length ) {\n
\t\t\tsynchronize( callback.shift() );\n
\t\t}\n
\t\treturn;\n
\t}\n
\tconfig.queue.push( callback );\n
\n
\tif ( config.autorun && !config.blocking ) {\n
\t\tprocess( last );\n
\t}\n
}\n
\n
function process( last ) {\n
\tfunction next() {\n
\t\tprocess( last );\n
\t}\n
\tvar start = now();\n
\tconfig.depth = ( config.depth || 0 ) + 1;\n
\n
\twhile ( config.queue.length && !config.blocking ) {\n
\t\tif ( !defined.setTimeout || config.updateRate <= 0 ||\n
\t\t\t\t( ( now() - start ) < config.updateRate ) ) {\n
\t\t\tif ( config.current ) {\n
\n
\t\t\t\t// Reset async tracking for each phase of the Test lifecycle\n
\t\t\t\tconfig.current.usedAsync = false;\n
\t\t\t}\n
\t\t\tconfig.queue.shift()();\n
\t\t} else {\n
\t\t\tsetTimeout( next, 13 );\n
\t\t\tbreak;\n
\t\t}\n
\t}\n
\tconfig.depth--;\n
\tif ( last && !config.blocking && !config.queue.length && config.depth === 0 ) {\n
\t\tdone();\n
\t}\n
}\n
\n
function begin() {\n
\tvar i, l,\n
\t\tmodulesLog = [];\n
\n
\t// If the test run hasn\'t officially begun yet\n
\tif ( !config.started ) {\n
\n
\t\t// Record the time of the test run\'s beginning\n
\t\tconfig.started = now();\n
\n
\t\tverifyLoggingCallbacks();\n
\n
\t\t// Delete the loose unnamed module if unused.\n
\t\tif ( config.modules[ 0 ].name === "" && config.modules[ 0 ].tests.length === 0 ) {\n
\t\t\tconfig.modules.shift();\n
\t\t}\n
\n
\t\t// Avoid unnecessary information by not logging modules\' test environments\n
\t\tfor ( i = 0, l = config.modules.length; i < l; i++ ) {\n
\t\t\tmodulesLog.push({\n
\t\t\t\tname: config.modules[ i ].name,\n
\t\t\t\ttests: config.modules[ i ].tests\n
\t\t\t});\n
\t\t}\n
\n
\t\t// The test run is officially beginning now\n
\t\trunLoggingCallbacks( "begin", {\n
\t\t\ttotalTests: Test.count,\n
\t\t\tmodules: modulesLog\n
\t\t});\n
\t}\n
\n
\tconfig.blocking = false;\n
\tprocess( true );\n
}\n
\n
function resumeProcessing() {\n
\trunStarted = true;\n
\n
\t// A slight delay to allow this iteration of the event loop to finish (more assertions, etc.)\n
\tif ( defined.setTimeout ) {\n
\t\tsetTimeout(function() {\n
\t\t\tif ( config.current && config.current.semaphore > 0 ) {\n
\t\t\t\treturn;\n
\t\t\t}\n
\t\t\tif ( config.timeout ) {\n
\t\t\t\tclearTimeout( config.timeout );\n
\t\t\t}\n
\n
\t\t\tbegin();\n
\t\t}, 13 );\n
\t} else {\n
\t\tbegin();\n
\t}\n
}\n
\n
function pauseProcessing() {\n
\tconfig.blocking = true;\n
\n
\tif ( config.testTimeout && defined.setTimeout ) {\n
\t\tclearTimeout( config.timeout );\n
\t\tconfig.timeout = setTimeout(function() {\n
\t\t\tif ( config.current ) {\n
\t\t\t\tconfig.current.semaphore = 0;\n
\t\t\t\tQUnit.pushFailure( "Test timed out", sourceFromStacktrace( 2 ) );\n
\t\t\t} else {\n
\t\t\t\tthrow new Error( "Test timed out" );\n
\t\t\t}\n
\t\t\tresumeProcessing();\n
\t\t}, config.testTimeout );\n
\t}\n
}\n
\n
function saveGlobal() {\n
\tconfig.pollution = [];\n
\n
\tif ( config.noglobals ) {\n
\t\tfor ( var key in window ) {\n
\t\t\tif ( hasOwn.call( window, key ) ) {\n
\t\t\t\t// in Opera sometimes DOM element ids show up here, ignore them\n
\t\t\t\tif ( /^qunit-test-output/.test( key ) ) {\n
\t\t\t\t\tcontinue;\n
\t\t\t\t}\n
\t\t\t\tconfig.pollution.push( key );\n
\t\t\t}\n
\t\t}\n
\t}\n
}\n
\n
function checkPollution() {\n
\tvar newGlobals,\n
\t\tdeletedGlobals,\n
\t\told = config.pollution;\n
\n
\tsaveGlobal();\n
\n
\tnewGlobals = diff( config.pollution, old );\n
\tif ( newGlobals.length > 0 ) {\n
\t\tQUnit.pushFailure( "Introduced global variable(s): " + newGlobals.join( ", " ) );\n
\t}\n
\n
\tdeletedGlobals = diff( old, config.pollution );\n
\tif ( deletedGlobals.length > 0 ) {\n
\t\tQUnit.pushFailure( "Deleted global variable(s): " + deletedGlobals.join( ", " ) );\n
\t}\n
}\n
\n
// returns a new Array with the elements that are in a but not in b\n
function diff( a, b ) {\n
\tvar i, j,\n
\t\tresult = a.slice();\n
\n
\tfor ( i = 0; i < result.length; i++ ) {\n
\t\tfor ( j = 0; j < b.length; j++ ) {\n
\t\t\tif ( result[ i ] === b[ j ] ) {\n
\t\t\t\tresult.splice( i, 1 );\n
\t\t\t\ti--;\n
\t\t\t\tbreak;\n
\t\t\t}\n
\t\t}\n
\t}\n
\treturn result;\n
}\n
\n
function extend( a, b, undefOnly ) {\n
\tfor ( var prop in b ) {\n
\t\tif ( hasOwn.call( b, prop ) ) {\n
\n
\t\t\t// Avoid "Member not found" error in IE8 caused by messing with window.constructor\n
\t\t\tif ( !( prop === "constructor" && a === window ) ) {\n
\t\t\t\tif ( b[ prop ] === undefined ) {\n
\t\t\t\t\tdelete a[ prop ];\n
\t\t\t\t} else if ( !( undefOnly && typeof a[ prop ] !== "undefined" ) ) {\n
\t\t\t\t\ta[ prop ] = b[ prop ];\n
\t\t\t\t}\n
\t\t\t}\n
\t\t}\n
\t}\n
\n
\treturn a;\n
}\n
\n
function runLoggingCallbacks( key, args ) {\n
\tvar i, l, callbacks;\n
\n
\tcallbacks = config.callbacks[ key ];\n
\tfor ( i = 0, l = callbacks.length; i < l; i++ ) {\n
\t\tcallbacks[ i ]( args );\n
\t}\n
}\n
\n
// DEPRECATED: This will be removed on 2.0.0+\n
// This function verifies if the loggingCallbacks were modified by the user\n
// If so, it will restore it, assign the given callback and print a console warning\n
function verifyLoggingCallbacks() {\n
\tvar loggingCallback, userCallback;\n
\n
\tfor ( loggingCallback in loggingCallbacks ) {\n
\t\tif ( QUnit[ loggingCallback ] !== loggingCallbacks[ loggingCallback ] ) {\n
\n
\t\t\tuserCallback = QUnit[ loggingCallback ];\n
\n
\t\t\t// Restore the callback function\n
\t\t\tQUnit[ loggingCallback ] = loggingCallbacks[ loggingCallback ];\n
\n
\t\t\t// Assign the deprecated given callback\n
\t\t\tQUnit[ loggingCallback ]( userCallback );\n
\n
\t\t\tif ( window.console && window.console.warn ) {\n
\t\t\t\twindow.console.warn(\n
\t\t\t\t\t"QUnit." + loggingCallback + " was replaced with a new value.\\n" +\n
\t\t\t\t\t"Please, check out the documentation on how to apply logging callbacks.\\n" +\n
\t\t\t\t\t"Reference: http://api.qunitjs.com/category/callbacks/"\n
\t\t\t\t);\n
\t\t\t}\n
\t\t}\n
\t}\n
}\n
\n
// from jquery.js\n
function inArray( elem, array ) {\n
\tif ( array.indexOf ) {\n
\t\treturn array.indexOf( elem );\n
\t}\n
\n
\tfor ( var i = 0, length = array.length; i < length; i++ ) {\n
\t\tif ( array[ i ] === elem ) {\n
\t\t\treturn i;\n
\t\t}\n
\t}\n
\n
\treturn -1;\n
}\n
\n
function Test( settings ) {\n
\tvar i, l;\n
\n
\t++Test.count;\n
\n
\textend( this, settings );\n
\tthis.assertions = [];\n
\tthis.semaphore = 0;\n
\tthis.usedAsync = false;\n
\tthis.module = config.currentModule;\n
\tthis.stack = sourceFromStacktrace( 3 );\n
\n
\t// Register unique strings\n
\tfor ( i = 0, l = this.module.tests; i < l.length; i++ ) {\n
\t\tif ( this.module.tests[ i ].name === this.testName ) {\n
\t\t\tthis.testName += " ";\n
\t\t}\n
\t}\n
\n
\tthis.testId = generateHash( this.module.name, this.testName );\n
\n
\tthis.module.tests.push({\n
\t\tname: this.testName,\n
\t\ttestId: this.testId\n
\t});\n
\n
\tif ( settings.skip ) {\n
\n
\t\t// Skipped tests will fully ignore any sent callback\n
\t\tthis.callback = function() {};\n
\t\tthis.async = false;\n
\t\tthis.expected = 0;\n
\t} else {\n
\t\tthis.assert = new Assert( this );\n
\t}\n
}\n
\n
Test.count = 0;\n
\n
Test.prototype = {\n
\tbefore: function() {\n
\t\tif (\n
\n
\t\t\t// Emit moduleStart when we\'re switching from one module to another\n
\t\t\tthis.module !== config.previousModule ||\n
\n
\t\t\t\t// They could be equal (both undefined) but if the previousModule property doesn\'t\n
\t\t\t\t// yet exist it means this is the first test in a suite that isn\'t wrapped in a\n
\t\t\t\t// module, in which case we\'ll just emit a moduleStart event for \'undefined\'.\n
\t\t\t\t// Without this, reporters can get testStart before moduleStart  which is a problem.\n
\t\t\t\t!hasOwn.call( config, "previousModule" )\n
\t\t) {\n
\t\t\tif ( hasOwn.call( config, "previousModule" ) ) {\n
\t\t\t\trunLoggingCallbacks( "moduleDone", {\n
\t\t\t\t\tname: config.previousModule.name,\n
\t\t\t\t\ttests: config.previousModule.tests,\n
\t\t\t\t\tfailed: config.moduleStats.bad,\n
\t\t\t\t\tpassed: config.moduleStats.all - config.moduleStats.bad,\n
\t\t\t\t\ttotal: config.moduleStats.all,\n
\t\t\t\t\truntime: now() - config.moduleStats.started\n
\t\t\t\t});\n
\t\t\t}\n
\t\t\tconfig.previousModule = this.module;\n
\t\t\tconfig.moduleStats = { all: 0, bad: 0, started: now() };\n
\t\t\trunLoggingCallbacks( "moduleStart", {\n
\t\t\t\tname: this.module.name,\n
\t\t\t\ttests: this.module.tests\n
\t\t\t});\n
\t\t}\n
\n
\t\tconfig.current = this;\n
\n
\t\tthis.testEnvironment = extend( {}, this.module.testEnvironment );\n
\t\tdelete this.testEnvironment.beforeEach;\n
\t\tdelete this.testEnvironment.afterEach;\n
\n
\t\tthis.started = now();\n
\t\trunLoggingCallbacks( "testStart", {\n
\t\t\tname: this.testName,\n
\t\t\tmodule: this.module.name,\n
\t\t\ttestId: this.testId\n
\t\t});\n
\n
\t\tif ( !config.pollution ) {\n
\t\t\tsaveGlobal();\n
\t\t}\n
\t},\n
\n
\trun: function() {\n
\t\tvar promise;\n
\n
\t\tconfig.current = this;\n
\n
\t\tif ( this.async ) {\n
\t\t\tQUnit.stop();\n
\t\t}\n
\n
\t\tthis.callbackStarted = now();\n
\n
\t\tif ( config.notrycatch ) {\n
\t\t\tpromise = this.callback.call( this.testEnvironment, this.assert );\n
\t\t\tthis.resolvePromise( promise );\n
\t\t\treturn;\n
\t\t}\n
\n
\t\ttry {\n
\t\t\tpromise = this.callback.call( this.testEnvironment, this.assert );\n
\t\t\tthis.resolvePromise( promise );\n
\t\t} catch ( e ) {\n
\t\t\tthis.pushFailure( "Died on test #" + ( this.assertions.length + 1 ) + " " +\n
\t\t\t\tthis.stack + ": " + ( e.message || e ), extractStacktrace( e, 0 ) );\n
\n
\t\t\t// else next test will carry the responsibility\n
\t\t\tsaveGlobal();\n
\n
\t\t\t// Restart the tests if they\'re blocking\n
\t\t\tif ( config.blocking ) {\n
\t\t\t\tQUnit.start();\n
\t\t\t}\n
\t\t}\n
\t},\n
\n
\tafter: function() {\n
\t\tcheckPollution();\n
\t},\n
\n
\tqueueHook: function( hook, hookName ) {\n
\t\tvar promise,\n
\t\t\ttest = this;\n
\t\treturn function runHook() {\n
\t\t\tconfig.current = test;\n
\t\t\tif ( config.notrycatch ) {\n
\t\t\t\tpromise = hook.call( test.testEnvironment, test.assert );\n
\t\t\t\ttest.resolvePromise( promise, hookName );\n
\t\t\t\treturn;\n
\t\t\t}\n
\t\t\ttry {\n
\t\t\t\tpromise = hook.call( test.testEnvironment, test.assert );\n
\t\t\t\ttest.resolvePromise( promise, hookName );\n
\t\t\t} catch ( error ) {\n
\t\t\t\ttest.pushFailure( hookName + " failed on " + test.testName + ": " +\n
\t\t\t\t\t( error.message || error ), extractStacktrace( error, 0 ) );\n
\t\t\t}\n
\t\t};\n
\t},\n
\n
\t// Currently only used for module level hooks, can be used to add global level ones\n
\thooks: function( handler ) {\n
\t\tvar hooks = [];\n
\n
\t\t// Hooks are ignored on skipped tests\n
\t\tif ( this.skip ) {\n
\t\t\treturn hooks;\n
\t\t}\n
\n
\t\tif ( this.module.testEnvironment &&\n
\t\t\t\tQUnit.objectType( this.module.testEnvironment[ handler ] ) === "function" ) {\n
\t\t\thooks.push( this.queueHook( this.module.testEnvironment[ handler ], handler ) );\n
\t\t}\n
\n
\t\treturn hooks;\n
\t},\n
\n
\tfinish: function() {\n
\t\tconfig.current = this;\n
\t\tif ( config.requireExpects && this.expected === null ) {\n
\t\t\tthis.pushFailure( "Expected number of assertions to be defined, but expect() was " +\n
\t\t\t\t"not called.", this.stack );\n
\t\t} else if ( this.expected !== null && this.expected !== this.assertions.length ) {\n
\t\t\tthis.pushFailure( "Expected " + this.expected + " assertions, but " +\n
\t\t\t\tthis.assertions.length + " were run", this.stack );\n
\t\t} else if ( this.expected === null && !this.assertions.length ) {\n
\t\t\tthis.pushFailure( "Expected at least one assertion, but none were run - call " +\n
\t\t\t\t"expect(0) to accept zero assertions.", this.stack );\n
\t\t}\n
\n
\t\tvar i,\n
\t\t\tbad = 0;\n
\n
\t\tthis.runtime = now() - this.started;\n
\t\tconfig.stats.all += this.assertions.length;\n
\t\tconfig.moduleStats.all += this.assertions.length;\n
\n
\t\tfor ( i = 0; i < this.assertions.length; i++ ) {\n
\t\t\tif ( !this.assertions[ i ].result ) {\n
\t\t\t\tbad++;\n
\t\t\t\tconfig.stats.bad++;\n
\t\t\t\tconfig.moduleStats.bad++;\n
\t\t\t}\n
\t\t}\n
\n
\t\trunLoggingCallbacks( "testDone", {\n
\t\t\tname: this.testName,\n
\t\t\tmodule: this.module.name,\n
\t\t\tskipped: !!this.skip,\n
\t\t\tfailed: bad,\n
\t\t\tpassed: this.assertions.length - bad,\n
\t\t\ttotal: this.assertions.length,\n
\t\t\truntime: this.runtime,\n
\n
\t\t\t// HTML Reporter use\n
\t\t\tassertions: this.assertions,\n
\t\t\ttestId: this.testId,\n
\n
\t\t\t// DEPRECATED: this property will be removed in 2.0.0, use runtime instead\n
\t\t\tduration: this.runtime\n
\t\t});\n
\n
\t\t// QUnit.reset() is deprecated and will be replaced for a new\n
\t\t// fixture reset function on QUnit 2.0/2.1.\n
\t\t// It\'s still called here for backwards compatibility handling\n
\t\tQUnit.reset();\n
\n
\t\tconfig.current = undefined;\n
\t},\n
\n
\tqueue: function() {\n
\t\tvar bad,\n
\t\t\ttest = this;\n
\n
\t\tif ( !this.valid() ) {\n
\t\t\treturn;\n
\t\t}\n
\n
\t\tfunction run() {\n
\n
\t\t\t// each of these can by async\n
\t\t\tsynchronize([\n
\t\t\t\tfunction() {\n
\t\t\t\t\ttest.before();\n
\t\t\t\t},\n
\n
\t\t\t\ttest.hooks( "beforeEach" ),\n
\n
\t\t\t\tfunction() {\n
\t\t\t\t\ttest.run();\n
\t\t\t\t},\n
\n
\t\t\t\ttest.hooks( "afterEach" ).reverse(),\n
\n
\t\t\t\tfunction() {\n
\t\t\t\t\ttest.after();\n
\t\t\t\t},\n
\t\t\t\tfunction() {\n
\t\t\t\t\ttest.finish();\n
\t\t\t\t}\n
\t\t\t]);\n
\t\t}\n
\n
\t\t// `bad` initialized at top of scope\n
\t\t// defer when previous test run passed, if storage is available\n
\t\tbad = QUnit.config.reorder && defined.sessionStorage &&\n
\t\t\t\t+sessionStorage.getItem( "qunit-test-" + this.module.name + "-" + this.testName );\n
\n
\t\tif ( bad ) {\n
\t\t\trun();\n
\t\t} else {\n
\t\t\tsynchronize( run, true );\n
\t\t}\n
\t},\n
\n
\tpush: function( result, actual, expected, message ) {\n
\t\tvar source,\n
\t\t\tdetails = {\n
\t\t\t\tmodule: this.module.name,\n
\t\t\t\tname: this.testName,\n
\t\t\t\tresult: result,\n
\t\t\t\tmessage: message,\n
\t\t\t\tactual: actual,\n
\t\t\t\texpected: expected,\n
\t\t\t\ttestId: this.testId,\n
\t\t\t\truntime: now() - this.started\n
\t\t\t};\n
\n
\t\tif ( !result ) {\n
\t\t\tsource = sourceFromStacktrace();\n
\n
\t\t\tif ( source ) {\n
\t\t\t\tdetails.source = source;\n
\t\t\t}\n
\t\t}\n
\n
\t\trunLoggingCallbacks( "log", details );\n
\n
\t\tthis.assertions.push({\n
\t\t\tresult: !!result,\n
\t\t\tmessage: message\n
\t\t});\n
\t},\n
\n
\tpushFailure: function( message, source, actual ) {\n
\t\tif ( !this instanceof Test ) {\n
\t\t\tthrow new Error( "pushFailure() assertion outside test context, was " +\n
\t\t\t\tsourceFromStacktrace( 2 ) );\n
\t\t}\n
\n
\t\tvar details = {\n
\t\t\t\tmodule: this.module.name,\n
\t\t\t\tname: this.testName,\n
\t\t\t\tresult: false,\n
\t\t\t\tmessage: message || "error",\n
\t\t\t\tactual: actual || null,\n
\t\t\t\ttestId: this.testId,\n
\t\t\t\truntime: now() - this.started\n
\t\t\t};\n
\n
\t\tif ( source ) {\n
\t\t\tdetails.source = source;\n
\t\t}\n
\n
\t\trunLoggingCallbacks( "log", details );\n
\n
\t\tthis.assertions.push({\n
\t\t\tresult: false,\n
\t\t\tmessage: message\n
\t\t});\n
\t},\n
\n
\tresolvePromise: function( promise, phase ) {\n
\t\tvar then, message,\n
\t\t\ttest = this;\n
\t\tif ( promise != null ) {\n
\t\t\tthen = promise.then;\n
\t\t\tif ( QUnit.objectType( then ) === "function" ) {\n
\t\t\t\tQUnit.stop();\n
\t\t\t\tthen.call(\n
\t\t\t\t\tpromise,\n
\t\t\t\t\tQUnit.start,\n
\t\t\t\t\tfunction( error ) {\n
\t\t\t\t\t\tmessage = "Promise rejected " +\n
\t\t\t\t\t\t\t( !phase ? "during" : phase.replace( /Each$/, "" ) ) +\n
\t\t\t\t\t\t\t" " + test.testName + ": " + ( error.message || error );\n
\t\t\t\t\t\ttest.pushFailure( message, extractStacktrace( error, 0 ) );\n
\n
\t\t\t\t\t\t// else next test will carry the responsibility\n
\t\t\t\t\t\tsaveGlobal();\n
\n
\t\t\t\t\t\t// Unblock\n
\t\t\t\t\t\tQUnit.start();\n
\t\t\t\t\t}\n
\t\t\t\t);\n
\t\t\t}\n
\t\t}\n
\t},\n
\n
\tvalid: function() {\n
\t\tvar include,\n
\t\t\tfilter = config.filter,\n
\t\t\tmodule = QUnit.urlParams.module && QUnit.urlParams.module.toLowerCase(),\n
\t\t\tfullName = ( this.module.name + ": " + this.testName ).toLowerCase();\n
\n
\t\t// Internally-generated tests are always valid\n
\t\tif ( this.callback && this.callback.validTest ) {\n
\t\t\treturn true;\n
\t\t}\n
\n
\t\tif ( config.testId.length > 0 && inArray( this.testId, config.testId ) < 0 ) {\n
\t\t\treturn false;\n
\t\t}\n
\n
\t\tif ( module && ( !this.module.name || this.module.name.toLowerCase() !== module ) ) {\n
\t\t\treturn false;\n
\t\t}\n
\n
\t\tif ( !filter ) {\n
\t\t\treturn true;\n
\t\t}\n
\n
\t\tinclude = filter.charAt( 0 ) !== "!";\n
\t\tif ( !include ) {\n
\t\t\tfilter = filter.toLowerCase().slice( 1 );\n
\t\t}\n
\n
\t\t// If the filter matches, we need to honour include\n
\t\tif ( fullName.indexOf( filter ) !== -1 ) {\n
\t\t\treturn include;\n
\t\t}\n
\n
\t\t// Otherwise, do the opposite\n
\t\treturn !include;\n
\t}\n
\n
};\n
\n
// Resets the test setup. Useful for tests that modify the DOM.\n
/*\n
DEPRECATED: Use multiple tests instead of resetting inside a test.\n
Use testStart or testDone for custom cleanup.\n
This method will throw an error in 2.0, and will be removed in 2.1\n
*/\n
QUnit.reset = function() {\n
\n
\t// Return on non-browser environments\n
\t// This is necessary to not break on node tests\n
\tif ( typeof window === "undefined" ) {\n
\t\treturn;\n
\t}\n
\n
\tvar fixture = defined.document && document.getElementById &&\n
\t\t\tdocument.getElementById( "qunit-fixture" );\n
\n
\tif ( fixture ) {\n
\t\tfixture.innerHTML = config.fixture;\n
\t}\n
};\n
\n
QUnit.pushFailure = function() {\n
\tif ( !QUnit.config.current ) {\n
\t\tthrow new Error( "pushFailure() assertion outside test context, in " +\n
\t\t\tsourceFromStacktrace( 2 ) );\n
\t}\n
\n
\t// Gets current test obj\n
\tvar currentTest = QUnit.config.current;\n
\n
\treturn currentTest.pushFailure.apply( currentTest, arguments );\n
};\n
\n
// Based on Java\'s String.hashCode, a simple but not\n
// rigorously collision resistant hashing function\n
function generateHash( module, testName ) {\n
\tvar hex,\n
\t\ti = 0,\n
\t\thash = 0,\n
\t\tstr = module + "\\x1C" + testName,\n
\t\tlen = str.length;\n
\n
\tfor ( ; i < len; i++ ) {\n
\t\thash  = ( ( hash << 5 ) - hash ) + str.charCodeAt( i );\n
\t\thash |= 0;\n
\t}\n
\n
\t// Convert the possibly negative integer hash code into an 8 character hex string, which isn\'t\n
\t// strictly necessary but increases user understanding that the id is a SHA-like hash\n
\thex = ( 0x100000000 + hash ).toString( 16 );\n
\tif ( hex.length < 8 ) {\n
\t\thex = "0000000" + hex;\n
\t}\n
\n
\treturn hex.slice( -8 );\n
}\n
\n
function Assert( testContext ) {\n
\tthis.test = testContext;\n
}\n
\n
// Assert helpers\n
QUnit.assert = Assert.prototype = {\n
\n
\t// Specify the number of expected assertions to guarantee that failed test\n
\t// (no assertions are run at all) don\'t slip through.\n
\texpect: function( asserts ) {\n
\t\tif ( arguments.length === 1 ) {\n
\t\t\tthis.test.expected = asserts;\n
\t\t} else {\n
\t\t\treturn this.test.expected;\n
\t\t}\n
\t},\n
\n
\t// Increment this Test\'s semaphore counter, then return a single-use function that\n
\t// decrements that counter a maximum of once.\n
\tasync: function() {\n
\t\tvar test = this.test,\n
\t\t\tpopped = false;\n
\n
\t\ttest.semaphore += 1;\n
\t\ttest.usedAsync = true;\n
\t\tpauseProcessing();\n
\n
\t\treturn function done() {\n
\t\t\tif ( !popped ) {\n
\t\t\t\ttest.semaphore -= 1;\n
\t\t\t\tpopped = true;\n
\t\t\t\tresumeProcessing();\n
\t\t\t} else {\n
\t\t\t\ttest.pushFailure( "Called the callback returned from `assert.async` more than once",\n
\t\t\t\t\tsourceFromStacktrace( 2 ) );\n
\t\t\t}\n
\t\t};\n
\t},\n
\n
\t// Exports test.push() to the user API\n
\tpush: function( /* result, actual, expected, message */ ) {\n
\t\tvar assert = this,\n
\t\t\tcurrentTest = ( assert instanceof Assert && assert.test ) || QUnit.config.current;\n
\n
\t\t// Backwards compatibility fix.\n
\t\t// Allows the direct use of global exported assertions and QUnit.assert.*\n
\t\t// Although, it\'s use is not recommended as it can leak assertions\n
\t\t// to other tests from async tests, because we only get a reference to the current test,\n
\t\t// not exactly the test where assertion were intended to be called.\n
\t\tif ( !currentTest ) {\n
\t\t\tthrow new Error( "assertion outside test context, in " + sourceFromStacktrace( 2 ) );\n
\t\t}\n
\n
\t\tif ( currentTest.usedAsync === true && currentTest.semaphore === 0 ) {\n
\t\t\tcurrentTest.pushFailure( "Assertion after the final `assert.async` was resolved",\n
\t\t\t\tsourceFromStacktrace( 2 ) );\n
\n
\t\t\t// Allow this assertion to continue running anyway...\n
\t\t}\n
\n
\t\tif ( !( assert instanceof Assert ) ) {\n
\t\t\tassert = currentTest.assert;\n
\t\t}\n
\t\treturn assert.test.push.apply( assert.test, arguments );\n
\t},\n
\n
\t/**\n
\t * Asserts rough true-ish result.\n
\t * @name ok\n
\t * @function\n
\t * @example ok( "asdfasdf".length > 5, "There must be at least 5 chars" );\n
\t */\n
\tok: function( result, message ) {\n
\t\tmessage = message || ( result ? "okay" : "failed, expected argument to be truthy, was: " +\n
\t\t\tQUnit.dump.parse( result ) );\n
\t\tthis.push( !!result, result, true, message );\n
\t},\n
\n
\t/**\n
\t * Assert that the first two arguments are equal, with an optional message.\n
\t * Prints out both actual and expected values.\n
\t * @name equal\n
\t * @function\n
\t * @example equal( format( "{0} bytes.", 2), "2 bytes.", "replaces {0} with next argument" );\n
\t */\n
\tequal: function( actual, expected, message ) {\n
\t\t/*jshint eqeqeq:false */\n
\t\tthis.push( expected == actual, actual, expected, message );\n
\t},\n
\n
\t/**\n
\t * @name notEqual\n
\t * @function\n
\t */\n
\tnotEqual: function( actual, expected, message ) {\n
\t\t/*jshint eqeqeq:false */\n
\t\tthis.push( expected != actual, actual, expected, message );\n
\t},\n
\n
\t/**\n
\t * @name propEqual\n
\t * @function\n
\t */\n
\tpropEqual: function( actual, expected, message ) {\n
\t\tactual = objectValues( actual );\n
\t\texpected = objectValues( expected );\n
\t\tthis.push( QUnit.equiv( actual, expected ), actual, expected, message );\n
\t},\n
\n
\t/**\n
\t * @name notPropEqual\n
\t * @function\n
\t */\n
\tnotPropEqual: function( actual, expected, message ) {\n
\t\tactual = objectValues( actual );\n
\t\texpected = objectValues( expected );\n
\t\tthis.push( !QUnit.equiv( actual, expected ), actual, expected, message );\n
\t},\n
\n
\t/**\n
\t * @name deepEqual\n
\t * @function\n
\t */\n
\tdeepEqual: function( actual, expected, message ) {\n
\t\tthis.push( QUnit.equiv( actual, expected ), actual, expected, message );\n
\t},\n
\n
\t/**\n
\t * @name notDeepEqual\n
\t * @function\n
\t */\n
\tnotDeepEqual: function( actual, expected, message ) {\n
\t\tthis.push( !QUnit.equiv( actual, expected ), actual, expected, message );\n
\t},\n
\n
\t/**\n
\t * @name strictEqual\n
\t * @function\n
\t */\n
\tstrictEqual: function( actual, expected, message ) {\n
\t\tthis.push( expected === actual, actual, expected, message );\n
\t},\n
\n
\t/**\n
\t * @name notStrictEqual\n
\t * @function\n
\t */\n
\tnotStrictEqual: function( actual, expected, message ) {\n
\t\tthis.push( expected !== actual, actual, expected, message );\n
\t},\n
\n
\t"throws": function( block, expected, message ) {\n
\t\tvar actual, expectedType,\n
\t\t\texpectedOutput = expected,\n
\t\t\tok = false;\n
\n
\t\t// \'expected\' is optional unless doing string comparison\n
\t\tif ( message == null && typeof expected === "string" ) {\n
\t\t\tmessage = expected;\n
\t\t\texpected = null;\n
\t\t}\n
\n
\t\tthis.test.ignoreGlobalErrors = true;\n
\t\ttry {\n
\t\t\tblock.call( this.test.testEnvironment );\n
\t\t} catch (e) {\n
\t\t\tactual = e;\n
\t\t}\n
\t\tthis.test.ignoreGlobalErrors = false;\n
\n
\t\tif ( actual ) {\n
\t\t\texpectedType = QUnit.objectType( expected );\n
\n
\t\t\t// we don\'t want to validate thrown error\n
\t\t\tif ( !expected ) {\n
\t\t\t\tok = true;\n
\t\t\t\texpectedOutput = null;\n
\n
\t\t\t// expected is a regexp\n
\t\t\t} else if ( expectedType === "regexp" ) {\n
\t\t\t\tok = expected.test( errorString( actual ) );\n
\n
\t\t\t// expected is a string\n
\t\t\t} else if ( expectedType === "string" ) {\n
\t\t\t\tok = expected === errorString( actual );\n
\n
\t\t\t// expected is a constructor, maybe an Error constructor\n
\t\t\t} else if ( expectedType === "function" && actual instanceof expected ) {\n
\t\t\t\tok = true;\n
\n
\t\t\t// expected is an Error object\n
\t\t\t} else if ( expectedType === "object" ) {\n
\t\t\t\tok = actual instanceof expected.constructor &&\n
\t\t\t\t\tactual.name === expected.name &&\n
\t\t\t\t\tactual.message === expected.message;\n
\n
\t\t\t// expected is a validation function which returns true if validation passed\n
\t\t\t} else if ( expectedType === "function" && expected.call( {}, actual ) === true ) {\n
\t\t\t\texpectedOutput = null;\n
\t\t\t\tok = true;\n
\t\t\t}\n
\n
\t\t\tthis.push( ok, actual, expectedOutput, message );\n
\t\t} else {\n
\t\t\tthis.test.pushFailure( message, null, "No exception was thrown." );\n
\t\t}\n
\t}\n
};\n
\n
// Provide an alternative to assert.throws(), for enviroments that consider throws a reserved word\n
// Known to us are: Closure Compiler, Narwhal\n
(function() {\n
\t/*jshint sub:true */\n
\tAssert.prototype.raises = Assert.prototype[ "throws" ];\n
}());\n
\n
// Test for equality any JavaScript type.\n
// Author: Philippe Rathé <prathe@gmail.com>\n
QUnit.equiv = (function() {\n
\n
\t// Call the o related callback with the given arguments.\n
\tfunction bindCallbacks( o, callbacks, args ) {\n
\t\tvar prop = QUnit.objectType( o );\n
\t\tif ( prop ) {\n
\t\t\tif ( QUnit.objectType( callbacks[ prop ] ) === "function" ) {\n
\t\t\t\treturn callbacks[ prop ].apply( callbacks, args );\n
\t\t\t} else {\n
\t\t\t\treturn callbacks[ prop ]; // or undefined\n
\t\t\t}\n
\t\t}\n
\t}\n
\n
\t// the real equiv function\n
\tvar innerEquiv,\n
\n
\t\t// stack to decide between skip/abort functions\n
\t\tcallers = [],\n
\n
\t\t// stack to avoiding loops from circular referencing\n
\t\tparents = [],\n
\t\tparentsB = [],\n
\n
\t\tgetProto = Object.getPrototypeOf || function( obj ) {\n
\t\t\t/* jshint camelcase: false, proto: true */\n
\t\t\treturn obj.__proto__;\n
\t\t},\n
\t\tcallbacks = (function() {\n
\n
\t\t\t// for string, boolean, number and null\n
\t\t\tfunction useStrictEquality( b, a ) {\n
\n
\t\t\t\t/*jshint eqeqeq:false */\n
\t\t\t\tif ( b instanceof a.constructor || a instanceof b.constructor ) {\n
\n
\t\t\t\t\t// to catch short annotation VS \'new\' annotation of a\n
\t\t\t\t\t// declaration\n
\t\t\t\t\t// e.g. var i = 1;\n
\t\t\t\t\t// var j = new Number(1);\n
\t\t\t\t\treturn a == b;\n
\t\t\t\t} else {\n
\t\t\t\t\treturn a === b;\n
\t\t\t\t}\n
\t\t\t}\n
\n
\t\t\treturn {\n
\t\t\t\t"string": useStrictEquality,\n
\t\t\t\t"boolean": useStrictEquality,\n
\t\t\t\t"number": useStrictEquality,\n
\t\t\t\t"null": useStrictEquality,\n
\t\t\t\t"undefined": useStrictEquality,\n
\n
\t\t\t\t"nan": function( b ) {\n
\t\t\t\t\treturn isNaN( b );\n
\t\t\t\t},\n
\n
\t\t\t\t"date": function( b, a ) {\n
\t\t\t\t\treturn QUnit.objectType( b ) === "date" && a.valueOf() === b.valueOf();\n
\t\t\t\t},\n
\n
\t\t\t\t"regexp": function( b, a ) {\n
\t\t\t\t\treturn QUnit.objectType( b ) === "regexp" &&\n
\n
\t\t\t\t\t\t// the regex itself\n
\t\t\t\t\t\ta.source === b.source &&\n
\n
\t\t\t\t\t\t// and its modifiers\n
\t\t\t\t\t\ta.global === b.global &&\n
\n
\t\t\t\t\t\t// (gmi) ...\n
\t\t\t\t\t\ta.ignoreCase === b.ignoreCase &&\n
\t\t\t\t\t\ta.multiline === b.multiline &&\n
\t\t\t\t\t\ta.sticky === b.sticky;\n
\t\t\t\t},\n
\n
\t\t\t\t// - skip when the property is a method of an instance (OOP)\n
\t\t\t\t// - abort otherwise,\n
\t\t\t\t// initial === would have catch identical references anyway\n
\t\t\t\t"function": function() {\n
\t\t\t\t\tvar caller = callers[ callers.length - 1 ];\n
\t\t\t\t\treturn caller !== Object && typeof caller !== "undefined";\n
\t\t\t\t},\n
\n
\t\t\t\t"array": function( b, a ) {\n
\t\t\t\t\tvar i, j, len, loop, aCircular, bCircular;\n
\n
\t\t\t\t\t// b could be an object literal here\n
\t\t\t\t\tif ( QUnit.objectType( b ) !== "array" ) {\n
\t\t\t\t\t\treturn false;\n
\t\t\t\t\t}\n
\n
\t\t\t\t\tlen = a.length;\n
\t\t\t\t\tif ( len !== b.length ) {\n
\t\t\t\t\t\t// safe and faster\n
\t\t\t\t\t\treturn false;\n
\t\t\t\t\t}\n
\n
\t\t\t\t\t// track reference to avoid circular references\n
\t\t\t\t\tparents.push( a );\n
\t\t\t\t\tparentsB.push( b );\n
\t\t\t\t\tfor ( i = 0; i < len; i++ ) {\n
\t\t\t\t\t\tloop = false;\n
\t\t\t\t\t\tfor ( j = 0; j < parents.length; j++ ) {\n
\t\t\t\t\t\t\taCircular = parents[ j ] === a[ i ];\n
\t\t\t\t\t\t\tbCircular = parentsB[ j ] === b[ i ];\n
\t\t\t\t\t\t\tif ( aCircular || bCircular ) {\n
\t\t\t\t\t\t\t\tif ( a[ i ] === b[ i ] || aCircular && bCircular ) {\n
\t\t\t\t\t\t\t\t\tloop = true;\n
\t\t\t\t\t\t\t\t} else {\n
\t\t\t\t\t\t\t\t\tparents.pop();\n
\t\t\t\t\t\t\t\t\tparentsB.pop();\n
\t\t\t\t\t\t\t\t\treturn false;\n
\t\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\tif ( !loop && !innerEquiv( a[ i ], b[ i ] ) ) {\n
\t\t\t\t\t\t\tparents.pop();\n
\t\t\t\t\t\t\tparentsB.pop();\n
\t\t\t\t\t\t\treturn false;\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\t\t\t\t\tparents.pop();\n
\t\t\t\t\tparentsB.pop();\n
\t\t\t\t\treturn true;\n
\t\t\t\t},\n
\n
\t\t\t\t"object": function( b, a ) {\n
\n
\t\t\t\t\t/*jshint forin:false */\n
\t\t\t\t\tvar i, j, loop, aCircular, bCircular,\n
\t\t\t\t\t\t// Default to true\n
\t\t\t\t\t\teq = true,\n
\t\t\t\t\t\taProperties = [],\n
\t\t\t\t\t\tbProperties = [];\n
\n
\t\t\t\t\t// comparing constructors is more strict than using\n
\t\t\t\t\t// instanceof\n
\t\t\t\t\tif ( a.constructor !== b.constructor ) {\n
\n
\t\t\t\t\t\t// Allow objects with no prototype to be equivalent to\n
\t\t\t\t\t\t// objects with Object as their constructor.\n
\t\t\t\t\t\tif ( !( ( getProto( a ) === null && getProto( b ) === Object.prototype ) ||\n
\t\t\t\t\t\t\t( getProto( b ) === null && getProto( a ) === Object.prototype ) ) ) {\n
\t\t\t\t\t\t\treturn false;\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\n
\t\t\t\t\t// stack constructor before traversing properties\n
\t\t\t\t\tcallers.push( a.constructor );\n
\n
\t\t\t\t\t// track reference to avoid circular references\n
\t\t\t\t\tparents.push( a );\n
\t\t\t\t\tparentsB.push( b );\n
\n
\t\t\t\t\t// be strict: don\'t ensure hasOwnProperty and go deep\n
\t\t\t\t\tfor ( i in a ) {\n
\t\t\t\t\t\tloop = false;\n
\t\t\t\t\t\tfor ( j = 0; j < parents.length; j++ ) {\n
\t\t\t\t\t\t\taCircular = parents[ j ] === a[ i ];\n
\t\t\t\t\t\t\tbCircular = parentsB[ j ] === b[ i ];\n
\t\t\t\t\t\t\tif ( aCircular || bCircular ) {\n
\t\t\t\t\t\t\t\tif ( a[ i ] === b[ i ] || aCircular && bCircular ) {\n
\t\t\t\t\t\t\t\t\tloop = true;\n
\t\t\t\t\t\t\t\t} else {\n
\t\t\t\t\t\t\t\t\teq = false;\n
\t\t\t\t\t\t\t\t\tbreak;\n
\t\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\taProperties.push( i );\n
\t\t\t\t\t\tif ( !loop && !innerEquiv( a[ i ], b[ i ] ) ) {\n
\t\t\t\t\t\t\teq = false;\n
\t\t\t\t\t\t\tbreak;\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\n
\t\t\t\t\tparents.pop();\n
\t\t\t\t\tparentsB.pop();\n
\t\t\t\t\tcallers.pop(); // unstack, we are done\n
\n
\t\t\t\t\tfor ( i in b ) {\n
\t\t\t\t\t\tbProperties.push( i ); // collect b\'s properties\n
\t\t\t\t\t}\n
\n
\t\t\t\t\t// Ensures identical properties name\n
\t\t\t\t\treturn eq && innerEquiv( aProperties.sort(), bProperties.sort() );\n
\t\t\t\t}\n
\t\t\t};\n
\t\t}());\n
\n
\tinnerEquiv = function() { // can take multiple arguments\n
\t\tvar args = [].slice.apply( arguments );\n
\t\tif ( args.length < 2 ) {\n
\t\t\treturn true; // end transition\n
\t\t}\n
\n
\t\treturn ( (function( a, b ) {\n
\t\t\tif ( a === b ) {\n
\t\t\t\treturn true; // catch the most you can\n
\t\t\t} else if ( a === null || b === null || typeof a === "undefined" ||\n
\t\t\t\t\ttypeof b === "undefined" ||\n
\t\t\t\t\tQUnit.objectType( a ) !== QUnit.objectType( b ) ) {\n
\n
\t\t\t\t// don\'t lose time with error prone cases\n
\t\t\t\treturn false;\n
\t\t\t} else {\n
\t\t\t\treturn bindCallbacks( a, callbacks, [ b, a ] );\n
\t\t\t}\n
\n
\t\t\t// apply transition with (1..n) arguments\n
\t\t}( args[ 0 ], args[ 1 ] ) ) &&\n
\t\t\tinnerEquiv.apply( this, args.splice( 1, args.length - 1 ) ) );\n
\t};\n
\n
\treturn innerEquiv;\n
}());\n
\n
// Based on jsDump by Ariel Flesler\n
// http://flesler.blogspot.com/2008/05/jsdump-pretty-dump-of-any-javascript.html\n
QUnit.dump = (function() {\n
\tfunction quote( str ) {\n
\t\treturn "\\"" + str.toString().replace( /"/g, "\\\\\\"" ) + "\\"";\n
\t}\n
\tfunction literal( o ) {\n
\t\treturn o + "";\n
\t}\n
\tfunction join( pre, arr, post ) {\n
\t\tvar s = dump.separator(),\n
\t\t\tbase = dump.indent(),\n
\t\t\tinner = dump.indent( 1 );\n
\t\tif ( arr.join ) {\n
\t\t\tarr = arr.join( "," + s + inner );\n
\t\t}\n
\t\tif ( !arr ) {\n
\t\t\treturn pre + post;\n
\t\t}\n
\t\treturn [ pre, inner + arr, base + post ].join( s );\n
\t}\n
\tfunction array( arr, stack ) {\n
\t\tvar i = arr.length,\n
\t\t\tret = new Array( i );\n
\n
\t\tif ( dump.maxDepth && dump.depth > dump.maxDepth ) {\n
\t\t\treturn "[object Array]";\n
\t\t}\n
\n
\t\tthis.up();\n
\t\twhile ( i-- ) {\n
\t\t\tret[ i ] = this.parse( arr[ i ], undefined, stack );\n
\t\t}\n
\t\tthis.down();\n
\t\treturn join( "[", ret, "]" );\n
\t}\n
\n
\tvar reName = /^function (\\w+)/,\n
\t\tdump = {\n
\n
\t\t\t// objType is used mostly internally, you can fix a (custom) type in advance\n
\t\t\tparse: function( obj, objType, stack ) {\n
\t\t\t\tstack = stack || [];\n
\t\t\t\tvar res, parser, parserType,\n
\t\t\t\t\tinStack = inArray( obj, stack );\n
\n
\t\t\t\tif ( inStack !== -1 ) {\n
\t\t\t\t\treturn "recursion(" + ( inStack - stack.length ) + ")";\n
\t\t\t\t}\n
\n
\t\t\t\tobjType = objType || this.typeOf( obj  );\n
\t\t\t\tparser = this.parsers[ objType ];\n
\t\t\t\tparserType = typeof parser;\n
\n
\t\t\t\tif ( parserType === "function" ) {\n
\t\t\t\t\tstack.push( obj );\n
\t\t\t\t\tres = parser.call( this, obj, stack );\n
\t\t\t\t\tstack.pop();\n
\t\t\t\t\treturn res;\n
\t\t\t\t}\n
\t\t\t\treturn ( parserType === "string" ) ? parser : this.parsers.error;\n
\t\t\t},\n
\t\t\ttypeOf: function( obj ) {\n
\t\t\t\tvar type;\n
\t\t\t\tif ( obj === null ) {\n
\t\t\t\t\ttype = "null";\n
\t\t\t\t} else if ( typeof obj === "undefined" ) {\n
\t\t\t\t\ttype = "undefined";\n
\t\t\t\t} else if ( QUnit.is( "regexp", obj ) ) {\n
\t\t\t\t\ttype = "regexp";\n
\t\t\t\t} else if ( QUnit.is( "date", obj ) ) {\n
\t\t\t\t\ttype = "date";\n
\t\t\t\t} else if ( QUnit.is( "function", obj ) ) {\n
\t\t\t\t\ttype = "function";\n
\t\t\t\t} else if ( obj.setInterval !== undefined &&\n
\t\t\t\t\t\tobj.document !== undefined &&\n
\t\t\t\t\t\tobj.nodeType === undefined ) {\n
\t\t\t\t\ttype = "window";\n
\t\t\t\t} else if ( obj.nodeType === 9 ) {\n
\t\t\t\t\ttype = "document";\n
\t\t\t\t} else if ( obj.nodeType ) {\n
\t\t\t\t\ttype = "node";\n
\t\t\t\t} else if (\n
\n
\t\t\t\t\t// native arrays\n
\t\t\t\t\ttoString.call( obj ) === "[object Array]" ||\n
\n
\t\t\t\t\t// NodeList objects\n
\t\t\t\t\t( typeof obj.length === "number" && obj.item !== undefined &&\n
\t\t\t\t\t( obj.length ? obj.item( 0 ) === obj[ 0 ] : ( obj.item( 0 ) === null &&\n
\t\t\t\t\tobj[ 0 ] === undefined ) ) )\n
\t\t\t\t) {\n
\t\t\t\t\ttype = "array";\n
\t\t\t\t} else if ( obj.constructor === Error.prototype.constructor ) {\n
\t\t\t\t\ttype = "error";\n
\t\t\t\t} else {\n
\t\t\t\t\ttype = typeof obj;\n
\t\t\t\t}\n
\t\t\t\treturn type;\n
\t\t\t},\n
\t\t\tseparator: function() {\n
\t\t\t\treturn this.multiline ? this.HTML ? "<br />" : "\\n" : this.HTML ? "&#160;" : " ";\n
\t\t\t},\n
\t\t\t// extra can be a number, shortcut for increasing-calling-decreasing\n
\t\t\tindent: function( extra ) {\n
\t\t\t\tif ( !this.multiline ) {\n
\t\t\t\t\treturn "";\n
\t\t\t\t}\n
\t\t\t\tvar chr = this.indentChar;\n
\t\t\t\tif ( this.HTML ) {\n
\t\t\t\t\tchr = chr.replace( /\\t/g, "   " ).replace( / /g, "&#160;" );\n
\t\t\t\t}\n
\t\t\t\treturn new Array( this.depth + ( extra || 0 ) ).join( chr );\n
\t\t\t},\n
\t\t\tup: function( a ) {\n
\t\t\t\tthis.depth += a || 1;\n
\t\t\t},\n
\t\t\tdown: function( a ) {\n
\t\t\t\tthis.depth -= a || 1;\n
\t\t\t},\n
\t\t\tsetParser: function( name, parser ) {\n
\t\t\t\tthis.parsers[ name ] = parser;\n
\t\t\t},\n
\t\t\t// The next 3 are exposed so you can use them\n
\t\t\tquote: quote,\n
\t\t\tliteral: literal,\n
\t\t\tjoin: join,\n
\t\t\t//\n
\t\t\tdepth: 1,\n
\t\t\tmaxDepth: 5,\n
\n
\t\t\t// This is the list of parsers, to modify them, use dump.setParser\n
\t\t\tparsers: {\n
\t\t\t\twindow: "[Window]",\n
\t\t\t\tdocument: "[Document]",\n
\t\t\t\terror: function( error ) {\n
\t\t\t\t\treturn "Error(\\"" + error.message + "\\")";\n
\t\t\t\t},\n
\t\t\t\tunknown: "[Unknown]",\n
\t\t\t\t"null": "null",\n
\t\t\t\t"undefined": "undefined",\n
\t\t\t\t"function": function( fn ) {\n
\t\t\t\t\tvar ret = "function",\n
\n
\t\t\t\t\t\t// functions never have name in IE\n
\t\t\t\t\t\tname = "name" in fn ? fn.name : ( reName.exec( fn ) || [] )[ 1 ];\n
\n
\t\t\t\t\tif ( name ) {\n
\t\t\t\t\t\tret += " " + name;\n
\t\t\t\t\t}\n
\t\t\t\t\tret += "( ";\n
\n
\t\t\t\t\tret = [ ret, dump.parse( fn, "functionArgs" ), "){" ].join( "" );\n
\t\t\t\t\treturn join( ret, dump.parse( fn, "functionCode" ), "}" );\n
\t\t\t\t},\n
\t\t\t\tarray: array,\n
\t\t\t\tnodelist: array,\n
\t\t\t\t"arguments": array,\n
\t\t\t\tobject: function( map, stack ) {\n
\t\t\t\t\tvar keys, key, val, i, nonEnumerableProperties,\n
\t\t\t\t\t\tret = [];\n
\n
\t\t\t\t\tif ( dump.maxDepth && dump.depth > dump.maxDepth ) {\n
\t\t\t\t\t\treturn "[object Object]";\n
\t\t\t\t\t}\n
\n
\t\t\t\t\tdump.up();\n
\t\t\t\t\tkeys = [];\n
\t\t\t\t\tfor ( key in map ) {\n
\t\t\t\t\t\tkeys.push( key );\n
\t\t\t\t\t}\n
\n
\t\t\t\t\t// Some properties are not always enumerable on Error objects.\n
\t\t\t\t\tnonEnumerableProperties = [ "message", "name" ];\n
\t\t\t\t\tfor ( i in nonEnumerableProperties ) {\n
\t\t\t\t\t\tkey = nonEnumerableProperties[ i ];\n
\t\t\t\t\t\tif ( key in map && !( key in keys ) ) {\n
\t\t\t\t\t\t\tkeys.push( key );\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\t\t\t\t\tkeys.sort();\n
\t\t\t\t\tfor ( i = 0; i < keys.length; i++ ) {\n
\t\t\t\t\t\tkey = keys[ i ];\n
\t\t\t\t\t\tval = map[ key ];\n
\t\t\t\t\t\tret.push( dump.parse( key, "key" ) + ": " +\n
\t\t\t\t\t\t\tdump.parse( val, undefined, stack ) );\n
\t\t\t\t\t}\n
\t\t\t\t\tdump.down();\n
\t\t\t\t\treturn join( "{", ret, "}" );\n
\t\t\t\t},\n
\t\t\t\tnode: function( node ) {\n
\t\t\t\t\tvar len, i, val,\n
\t\t\t\t\t\topen = dump.HTML ? "&lt;" : "<",\n
\t\t\t\t\t\tclose = dump.HTML ? "&gt;" : ">",\n
\t\t\t\t\t\ttag = node.nodeName.toLowerCase(),\n
\t\t\t\t\t\tret = open + tag,\n
\t\t\t\t\t\tattrs = node.attributes;\n
\n
\t\t\t\t\tif ( attrs ) {\n
\t\t\t\t\t\tfor ( i = 0, len = attrs.length; i < len; i++ ) {\n
\t\t\t\t\t\t\tval = attrs[ i ].nodeValue;\n
\n
\t\t\t\t\t\t\t// IE6 includes all attributes in .attributes, even ones not explicitly\n
\t\t\t\t\t\t\t// set. Those have values like undefined, null, 0, false, "" or\n
\t\t\t\t\t\t\t// "inherit".\n
\t\t\t\t\t\t\tif ( val && val !== "inherit" ) {\n
\t\t\t\t\t\t\t\tret += " " + attrs[ i ].nodeName + "=" +\n
\t\t\t\t\t\t\t\t\tdump.parse( val, "attribute" );\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\t\t\t\t\tret += close;\n
\n
\t\t\t\t\t// Show content of TextNode or CDATASection\n
\t\t\t\t\tif ( node.nodeType === 3 || node.nodeType === 4 ) {\n
\t\t\t\t\t\tret += node.nodeValue;\n
\t\t\t\t\t}\n
\n
\t\t\t\t\treturn ret + open + "/" + tag + close;\n
\t\t\t\t},\n
\n
\t\t\t\t// function calls it internally, it\'s the arguments part of the function\n
\t\t\t\tfunctionArgs: function( fn ) {\n
\t\t\t\t\tvar args,\n
\t\t\t\t\t\tl = fn.length;\n
\n
\t\t\t\t\tif ( !l ) {\n
\t\t\t\t\t\treturn "";\n
\t\t\t\t\t}\n
\n
\t\t\t\t\targs = new Array( l );\n
\t\t\t\t\twhile ( l-- ) {\n
\n
\t\t\t\t\t\t// 97 is \'a\'\n
\t\t\t\t\t\targs[ l ] = String.fromCharCode( 97 + l );\n
\t\t\t\t\t}\n
\t\t\t\t\treturn " " + args.join( ", " ) + " ";\n
\t\t\t\t},\n
\t\t\t\t// object calls it internally, the key part of an item in a map\n
\t\t\t\tkey: quote,\n
\t\t\t\t// function calls it internally, it\'s the content of the function\n
\t\t\t\tfunctionCode: "[code]",\n
\t\t\t\t// node calls it internally, it\'s an html attribute value\n
\t\t\t\tattribute: quote,\n
\t\t\t\tstring: quote,\n
\t\t\t\tdate: quote,\n
\t\t\t\tregexp: literal,\n
\t\t\t\tnumber: literal,\n
\t\t\t\t"boolean": literal\n
\t\t\t},\n
\t\t\t// if true, entities are escaped ( <, >, \\t, space and \\n )\n
\t\t\tHTML: false,\n
\t\t\t// indentation unit\n
\t\t\tindentChar: "  ",\n
\t\t\t// if true, items in a collection, are separated by a \\n, else just a space.\n
\t\t\tmultiline: true\n
\t\t};\n
\n
\treturn dump;\n
}());\n
\n
// back compat\n
QUnit.jsDump = QUnit.dump;\n
\n
// For browser, export only select globals\n
if ( typeof window !== "undefined" ) {\n
\n
\t// Deprecated\n
\t// Extend assert methods to QUnit and Global scope through Backwards compatibility\n
\t(function() {\n
\t\tvar i,\n
\t\t\tassertions = Assert.prototype;\n
\n
\t\tfunction applyCurrent( current ) {\n
\t\t\treturn function() {\n
\t\t\t\tvar assert = new Assert( QUnit.config.current );\n
\t\t\t\tcurrent.apply( assert, arguments );\n
\t\t\t};\n
\t\t}\n
\n
\t\tfor ( i in assertions ) {\n
\t\t\tQUnit[ i ] = applyCurrent( assertions[ i ] );\n
\t\t}\n
\t})();\n
\n
\t(function() {\n
\t\tvar i, l,\n
\t\t\tkeys = [\n
\t\t\t\t"test",\n
\t\t\t\t"module",\n
\t\t\t\t"expect",\n
\t\t\t\t"asyncTest",\n
\t\t\t\t"start",\n
\t\t\t\t"stop",\n
\t\t\t\t"ok",\n
\t\t\t\t"equal",\n
\t\t\t\t"notEqual",\n
\t\t\t\t"propEqual",\n
\t\t\t\t"notPropEqual",\n
\t\t\t\t"deepEqual",\n
\t\t\t\t"notDeepEqual",\n
\t\t\t\t"strictEqual",\n
\t\t\t\t"notStrictEqual",\n
\t\t\t\t"throws"\n
\t\t\t];\n
\n
\t\tfor ( i = 0, l = keys.length; i < l; i++ ) {\n
\t\t\twindow[ keys[ i ] ] = QUnit[ keys[ i ] ];\n
\t\t}\n
\t})();\n
\n
\twindow.QUnit = QUnit;\n
}\n
\n
// For nodejs\n
if ( typeof module !== "undefined" && module && module.exports ) {\n
\tmodule.exports = QUnit;\n
\n
\t// For consistency with CommonJS environments\' exports\n
\tmodule.exports.QUnit = QUnit;\n
}\n
\n
// For CommonJS with exports, but without module.exports, like Rhino\n
if ( typeof exports !== "undefined" && exports ) {\n
\texports.QUnit = QUnit;\n
}\n
\n
// Get a reference to the global object, like window in browsers\n
}( (function() {\n
\treturn this;\n
})() ));\n
\n
/*istanbul ignore next */\n
// jscs:disable maximumLineLength\n
/*\n
 * Javascript Diff Algorithm\n
 *  By John Resig (http://ejohn.org/)\n
 *  Modified by Chu Alan "sprite"\n
 *\n
 * Released under the MIT license.\n
 *\n
 * More Info:\n
 *  http://ejohn.org/projects/javascript-diff-algorithm/\n
 *\n
 * Usage: QUnit.diff(expected, actual)\n
 *\n
 * QUnit.diff( "the quick brown fox jumped over", "the quick fox jumps over" ) == "the  quick <del>brown </del> fox <del>jumped </del><ins>jumps </ins> over"\n
 */\n
QUnit.diff = (function() {\n
\tvar hasOwn = Object.prototype.hasOwnProperty;\n
\n
\t/*jshint eqeqeq:false, eqnull:true */\n
\tfunction diff( o, n ) {\n
\t\tvar i,\n
\t\t\tns = {},\n
\t\t\tos = {};\n
\n
\t\tfor ( i = 0; i < n.length; i++ ) {\n
\t\t\tif ( !hasOwn.call( ns, n[ i ] ) ) {\n
\t\t\t\tns[ n[ i ] ] = {\n
\t\t\t\t\trows: [],\n
\t\t\t\t\to: null\n
\t\t\t\t};\n
\t\t\t}\n
\t\t\tns[ n[ i ] ].rows.push( i );\n
\t\t}\n
\n
\t\tfor ( i = 0; i < o.length; i++ ) {\n
\t\t\tif ( !hasOwn.call( os, o[ i ] ) ) {\n
\t\t\t\tos[ o[ i ] ] = {\n
\t\t\t\t\trows: [],\n
\t\t\t\t\tn: null\n
\t\t\t\t};\n
\t\t\t}\n
\t\t\tos[ o[ i ] ].rows.push( i );\n
\t\t}\n
\n
\t\tfor ( i in ns ) {\n
\t\t\tif ( hasOwn.call( ns, i ) ) {\n
\t\t\t\tif ( ns[ i ].rows.length === 1 && hasOwn.call( os, i ) && os[ i ].rows.length === 1 ) {\n
\t\t\t\t\tn[ ns[ i ].rows[ 0 ] ] = {\n
\t\t\t\t\t\ttext: n[ ns[ i ].rows[ 0 ] ],\n
\t\t\t\t\t\trow: os[ i ].rows[ 0 ]\n
\t\t\t\t\t};\n
\t\t\t\t\to[ os[ i ].rows[ 0 ] ] = {\n
\t\t\t\t\t\ttext: o[ os[ i ].rows[ 0 ] ],\n
\t\t\t\t\t\trow: ns[ i ].rows[ 0 ]\n
\t\t\t\t\t};\n
\t\t\t\t}\n
\t\t\t}\n
\t\t}\n
\n
\t\tfor ( i = 0; i < n.length - 1; i++ ) {\n
\t\t\tif ( n[ i ].text != null && n[ i + 1 ].text == null && n[ i ].row + 1 < o.length && o[ n[ i ].row + 1 ].text == null &&\n
\t\t\t\tn[ i + 1 ] == o[ n[ i ].row + 1 ] ) {\n
\n
\t\t\t\tn[ i + 1 ] = {\n
\t\t\t\t\ttext: n[ i + 1 ],\n
\t\t\t\t\trow: n[ i ].row + 1\n
\t\t\t\t};\n
\t\t\t\to[ n[ i ].row + 1 ] = {\n
\t\t\t\t\ttext: o[ n[ i ].row + 1 ],\n
\t\t\t\t\trow: i + 1\n
\t\t\t\t};\n
\t\t\t}\n
\t\t}\n
\n
\t\tfor ( i = n.length - 1; i > 0; i-- ) {\n
\t\t\tif ( n[ i ].text != null && n[ i - 1 ].text == null && n[ i ].row > 0 && o[ n[ i ].row - 1 ].text == null &&\n
\t\t\t\tn[ i - 1 ] == o[ n[ i ].row - 1 ] ) {\n
\n
\t\t\t\tn[ i - 1 ] = {\n
\t\t\t\t\ttext: n[ i - 1 ],\n
\t\t\t\t\trow: n[ i ].row - 1\n
\t\t\t\t};\n
\t\t\t\to[ n[ i ].row - 1 ] = {\n
\t\t\t\t\ttext: o[ n[ i ].row - 1 ],\n
\t\t\t\t\trow: i - 1\n
\t\t\t\t};\n
\t\t\t}\n
\t\t}\n
\n
\t\treturn {\n
\t\t\to: o,\n
\t\t\tn: n\n
\t\t};\n
\t}\n
\n
\treturn function( o, n ) {\n
\t\to = o.replace( /\\s+$/, "" );\n
\t\tn = n.replace( /\\s+$/, "" );\n
\n
\t\tvar i, pre,\n
\t\t\tstr = "",\n
\t\t\tout = diff( o === "" ? [] : o.split( /\\s+/ ), n === "" ? [] : n.split( /\\s+/ ) ),\n
\t\t\toSpace = o.match( /\\s+/g ),\n
\t\t\tnSpace = n.match( /\\s+/g );\n
\n
\t\tif ( oSpace == null ) {\n
\t\t\toSpace = [ " " ];\n
\t\t} else {\n
\t\t\toSpace.push( " " );\n
\t\t}\n
\n
\t\tif ( nSpace == null ) {\n
\t\t\tnSpace = [ " " ];\n
\t\t} else {\n
\t\t\tnSpace.push( " " );\n
\t\t}\n
\n
\t\tif ( out.n.length === 0 ) {\n
\t\t\tfor ( i = 0; i < out.o.length; i++ ) {\n
\t\t\t\tstr += "<del>" + out.o[ i ] + oSpace[ i ] + "</del>";\n
\t\t\t}\n
\t\t} else {\n
\t\t\tif ( out.n[ 0 ].text == null ) {\n
\t\t\t\tfor ( n = 0; n < out.o.length && out.o[ n ].text == null; n++ ) {\n
\t\t\t\t\tstr += "<del>" + out.o[ n ] + oSpace[ n ] + "</del>";\n
\t\t\t\t}\n
\t\t\t}\n
\n
\t\t\tfor ( i = 0; i < out.n.length; i++ ) {\n
\t\t\t\tif ( out.n[ i ].text == null ) {\n
\t\t\t\t\tstr += "<ins>" + out.n[ i ] + nSpace[ i ] + "</ins>";\n
\t\t\t\t} else {\n
\n
\t\t\t\t\t// `pre` initialized at top of scope\n
\t\t\t\t\tpre = "";\n
\n
\t\t\t\t\tfor ( n = out.n[ i ].row + 1; n < out.o.length && out.o[ n ].text == null; n++ ) {\n
\t\t\t\t\t\tpre += "<del>" + out.o[ n ] + oSpace[ n ] + "</del>";\n
\t\t\t\t\t}\n
\t\t\t\t\tstr += " " + out.n[ i ].text + nSpace[ i ] + pre;\n
\t\t\t\t}\n
\t\t\t}\n
\t\t}\n
\n
\t\treturn str;\n
\t};\n
}());\n
// jscs:enable\n
\n
(function() {\n
\n
// Deprecated QUnit.init - Ref #530\n
// Re-initialize the configuration options\n
QUnit.init = function() {\n
\tvar tests, banner, result, qunit,\n
\t\tconfig = QUnit.config;\n
\n
\tconfig.stats = { all: 0, bad: 0 };\n
\tconfig.moduleStats = { all: 0, bad: 0 };\n
\tconfig.started = 0;\n
\tconfig.updateRate = 1000;\n
\tconfig.blocking = false;\n
\tconfig.autostart = true;\n
\tconfig.autorun = false;\n
\tconfig.filter = "";\n
\tconfig.queue = [];\n
\n
\t// Return on non-browser environments\n
\t// This is necessary to not break on node tests\n
\tif ( typeof window === "undefined" ) {\n
\t\treturn;\n
\t}\n
\n
\tqunit = id( "qunit" );\n
\tif ( qunit ) {\n
\t\tqunit.innerHTML =\n
\t\t\t"<h1 id=\'qunit-header\'>" + escapeText( document.title ) + "</h1>" +\n
\t\t\t"<h2 id=\'qunit-banner\'></h2>" +\n
\t\t\t"<div id=\'qunit-testrunner-toolbar\'></div>" +\n
\t\t\t"<h2 id=\'qunit-userAgent\'></h2>" +\n
\t\t\t"<ol id=\'qunit-tests\'></ol>";\n
\t}\n
\n
\ttests = id( "qunit-tests" );\n
\tbanner = id( "qunit-banner" );\n
\tresult = id( "qunit-testresult" );\n
\n
\tif ( tests ) {\n
\t\ttests.innerHTML = "";\n
\t}\n
\n
\tif ( banner ) {\n
\t\tbanner.className = "";\n
\t}\n
\n
\tif ( result ) {\n
\t\tresult.parentNode.removeChild( result );\n
\t}\n
\n
\tif ( tests ) {\n
\t\tresult = document.createElement( "p" );\n
\t\tresult.id = "qunit-testresult";\n
\t\tresult.className = "result";\n
\t\ttests.parentNode.insertBefore( result, tests );\n
\t\tresult.innerHTML = "Running...<br />&#160;";\n
\t}\n
};\n
\n
// Don\'t load the HTML Reporter on non-Browser environments\n
if ( typeof window === "undefined" ) {\n
\treturn;\n
}\n
\n
var config = QUnit.config,\n
\thasOwn = Object.prototype.hasOwnProperty,\n
\tdefined = {\n
\t\tdocument: window.document !== undefined,\n
\t\tsessionStorage: (function() {\n
\t\t\tvar x = "qunit-test-string";\n
\t\t\ttry {\n
\t\t\t\tsessionStorage.setItem( x, x );\n
\t\t\t\tsessionStorage.removeItem( x );\n
\t\t\t\treturn true;\n
\t\t\t} catch ( e ) {\n
\t\t\t\treturn false;\n
\t\t\t}\n
\t\t}())\n
\t},\n
\tmodulesList = [];\n
\n
/**\n
* Escape text for attribute or text content.\n
*/\n
function escapeText( s ) {\n
\tif ( !s ) {\n
\t\treturn "";\n
\t}\n
\ts = s + "";\n
\n
\t// Both single quotes and double quotes (for attributes)\n
\treturn s.replace( /[\'"<>&]/g, function( s ) {\n
\t\tswitch ( s ) {\n
\t\tcase "\'":\n
\t\t\treturn "&#039;";\n
\t\tcase "\\"":\n
\t\t\treturn "&quot;";\n
\t\tcase "<":\n
\t\t\treturn "&lt;";\n
\t\tcase ">":\n
\t\t\treturn "&gt;";\n
\t\tcase "&":\n
\t\t\treturn "&amp;";\n
\t\t}\n
\t});\n
}\n
\n
/**\n
 * @param {HTMLElement} elem\n
 * @param {string} type\n
 * @param {Function} fn\n
 */\n
function addEvent( elem, type, fn ) {\n
\tif ( elem.addEventListener ) {\n
\n
\t\t// Standards-based browsers\n
\t\telem.addEventListener( type, fn, false );\n
\t} else if ( elem.attachEvent ) {\n
\n
\t\t// support: IE <9\n
\t\telem.attachEvent( "on" + type, fn );\n
\t}\n
}\n
\n
/**\n
 * @param {Array|NodeList} elems\n
 * @param {string} type\n
 * @param {Function} fn\n
 */\n
function addEvents( elems, type, fn ) {\n
\tvar i = elems.length;\n
\twhile ( i-- ) {\n
\t\taddEvent( elems[ i ], type, fn );\n
\t}\n
}\n
\n
function hasClass( elem, name ) {\n
\treturn ( " " + elem.className + " " ).indexOf( " " + name + " " ) >= 0;\n
}\n
\n
function addClass( elem, name ) {\n
\tif ( !hasClass( elem, name ) ) {\n
\t\telem.className += ( elem.className ? " " : "" ) + name;\n
\t}\n
}\n
\n
function toggleClass( elem, name ) {\n
\tif ( hasClass( elem, name ) ) {\n
\t\tremoveClass( elem, name );\n
\t} else {\n
\t\taddClass( elem, name );\n
\t}\n
}\n
\n
function removeClass( elem, name ) {\n
\tvar set = " " + elem.className + " ";\n
\n
\t// Class name may appear multiple times\n
\twhile ( set.indexOf( " " + name + " " ) >= 0 ) {\n
\t\tset = set.replace( " " + name + " ", " " );\n
\t}\n
\n
\t// trim for prettiness\n
\telem.className = typeof set.trim === "function" ? set.trim() : set.replace( /^\\s+|\\s+$/g, "" );\n
}\n
\n
function id( name ) {\n
\treturn defined.document && document.getElementById && document.getElementById( name );\n
}\n
\n
function getUrlConfigHtml() {\n
\tvar i, j, val,\n
\t\tescaped, escapedTooltip,\n
\t\tselection = false,\n
\t\tlen = config.urlConfig.length,\n
\t\turlConfigHtml = "";\n
\n
\tfor ( i = 0; i < len; i++ ) {\n
\t\tval = config.urlConfig[ i ];\n
\t\tif ( typeof val === "string" ) {\n
\t\t\tval = {\n
\t\t\t\tid: val,\n
\t\t\t\tlabel: val\n
\t\t\t};\n
\t\t}\n
\n
\t\tescaped = escapeText( val.id );\n
\t\tescapedTooltip = escapeText( val.tooltip );\n
\n
\t\tif ( config[ val.id ] === undefined ) {\n
\t\t\tconfig[ val.id ] = QUnit.urlParams[ val.id ];\n
\t\t}\n
\n
\t\tif ( !val.value || typeof val.value === "string" ) {\n
\t\t\turlConfigHtml += "<input id=\'qunit-urlconfig-" + escaped +\n
\t\t\t\t"\' name=\'" + escaped + "\' type=\'checkbox\'" +\n
\t\t\t\t( val.value ? " value=\'" + escapeText( val.value ) + "\'" : "" ) +\n
\t\t\t\t( config[ val.id ] ? " checked=\'checked\'" : "" ) +\n
\t\t\t\t" title=\'" + escapedTooltip + "\' /><label for=\'qunit-urlconfig-" + escaped +\n
\t\t\t\t"\' title=\'" + escapedTooltip + "\'>" + val.label + "</label>";\n
\t\t} else {\n
\t\t\turlConfigHtml += "<label for=\'qunit-urlconfig-" + escaped +\n
\t\t\t\t"\' title=\'" + escapedTooltip + "\'>" + val.label +\n
\t\t\t\t": </label><select id=\'qunit-urlconfig-" + escaped +\n
\t\t\t\t"\' name=\'" + escaped + "\' title=\'" + escapedTooltip + "\'><option></option>";\n
\n
\t\t\tif ( QUnit.is( "array", val.value ) ) {\n
\t\t\t\tfor ( j = 0; j < val.value.length; j++ ) {\n
\t\t\t\t\tescaped = escapeText( val.value[ j ] );\n
\t\t\t\t\turlConfigHtml += "<option value=\'" + escaped + "\'" +\n
\t\t\t\t\t\t( config[ val.id ] === val.value[ j ] ?\n
\t\t\t\t\t\t\t( selection = true ) && " selected=\'selected\'" : "" ) +\n
\t\t\t\t\t\t">" + escaped + "</option>";\n
\t\t\t\t}\n
\t\t\t} else {\n
\t\t\t\tfor ( j in val.value ) {\n
\t\t\t\t\tif ( hasOwn.call( val.value, j ) ) {\n
\t\t\t\t\t\turlConfigHtml += "<option value=\'" + escapeText( j ) + "\'" +\n
\t\t\t\t\t\t\t( config[ val.id ] === j ?\n
\t\t\t\t\t\t\t\t( selection = true ) && " selected=\'selected\'" : "" ) +\n
\t\t\t\t\t\t\t">" + escapeText( val.value[ j ] ) + "</option>";\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t}\n
\t\t\tif ( config[ val.id ] && !selection ) {\n
\t\t\t\tescaped = escapeText( config[ val.id ] );\n
\t\t\t\turlConfigHtml += "<option value=\'" + escaped +\n
\t\t\t\t\t"\' selected=\'selected\' disabled=\'disabled\'>" + escaped + "</option>";\n
\t\t\t}\n
\t\t\turlConfigHtml += "</select>";\n
\t\t}\n
\t}\n
\n
\treturn urlConfigHtml;\n
}\n
\n
// Handle "click" events on toolbar checkboxes and "change" for select menus.\n
// Updates the URL with the new state of `config.urlConfig` values.\n
function toolbarChanged() {\n
\tvar updatedUrl, value,\n
\t\tfield = this,\n
\t\tparams = {};\n
\n
\t// Detect if field is a select menu or a checkbox\n
\tif ( "selectedIndex" in field ) {\n
\t\tvalue = field.options[ field.selectedIndex ].value || undefined;\n
\t} else {\n
\t\tvalue = field.checked ? ( field.defaultValue || true ) : undefined;\n
\t}\n
\n
\tparams[ field.name ] = value;\n
\tupdatedUrl = setUrl( params );\n
\n
\tif ( "hidepassed" === field.name && "replaceState" in window.history ) {\n
\t\tconfig[ field.name ] = value || false;\n
\t\tif ( value ) {\n
\t\t\taddClass( id( "qunit-tests" ), "hidepass" );\n
\t\t} else {\n
\t\t\tremoveClass( id( "qunit-tests" ), "hidepass" );\n
\t\t}\n
\n
\t\t// It is not necessary to refresh the whole page\n
\t\twindow.history.replaceState( null, "", updatedUrl );\n
\t} else {\n
\t\twindow.location = updatedUrl;\n
\t}\n
}\n
\n
function setUrl( params ) {\n
\tvar key,\n
\t\tquerystring = "?";\n
\n
\tparams = QUnit.extend( QUnit.extend( {}, QUnit.urlParams ), params );\n
\n
\tfor ( key in params ) {\n
\t\tif ( hasOwn.call( params, key ) ) {\n
\t\t\tif ( params[ key ] === undefined ) {\n
\t\t\t\tcontinue;\n
\t\t\t}\n
\t\t\tquerystring += encodeURIComponent( key );\n
\t\t\tif ( params[ key ] !== true ) {\n
\t\t\t\tquerystring += "=" + encodeURIComponent( params[ key ] );\n
\t\t\t}\n
\t\t\tquerystring += "&";\n
\t\t}\n
\t}\n
\treturn location.protocol + "//" + location.host +\n
\t\tlocation.pathname + querystring.slice( 0, -1 );\n
}\n
\n
function applyUrlParams() {\n
\tvar selectBox = id( "qunit-modulefilter" ),\n
\t\tselection = decodeURIComponent( selectBox.options[ selectBox.selectedIndex ].value ),\n
\t\tfilter = id( "qunit-filter-input" ).value;\n
\n
\twindow.location = setUrl({\n
\t\tmodule: ( selection === "" ) ? undefined : selection,\n
\t\tfilter: ( filter === "" ) ? undefined : filter,\n
\n
\t\t// Remove testId filter\n
\t\ttestId: undefined\n
\t});\n
}\n
\n
function toolbarUrlConfigContainer() {\n
\tvar urlConfigContainer = document.createElement( "span" );\n
\n
\turlConfigContainer.innerHTML = getUrlConfigHtml();\n
\taddClass( urlConfigContainer, "qunit-url-config" );\n
\n
\t// For oldIE support:\n
\t// * Add handlers to the individual elements instead of the container\n
\t// * Use "click" instead of "change" for checkboxes\n
\taddEvents( urlConfigContainer.getElementsByTagName( "input" ), "click", toolbarChanged );\n
\taddEvents( urlConfigContainer.getElementsByTagName( "select" ), "change", toolbarChanged );\n
\n
\treturn urlConfigContainer;\n
}\n
\n
function toolbarLooseFilter() {\n
\tvar filter = document.createElement( "form" ),\n
\t\tlabel = document.createElement( "label" ),\n
\t\tinput = document.createElement( "input" ),\n
\t\tbutton = document.createElement( "button" );\n
\n
\taddClass( filter, "qunit-filter" );\n
\n
\tlabel.innerHTML = "Filter: ";\n
\n
\tinput.type = "text";\n
\tinput.value = config.filter || "";\n
\tinput.name = "filter";\n
\tinput.id = "qunit-filter-input";\n
\n
\tbutton.innerHTML = "Go";\n
\n
\tlabel.appendChild( input );\n
\n
\tfilter.appendChild( label );\n
\tfilter.appendChild( button );\n
\taddEvent( filter, "submit", function( ev ) {\n
\t\tapplyUrlParams();\n
\n
\t\tif ( ev && ev.preventDefault ) {\n
\t\t\tev.preventDefault();\n
\t\t}\n
\n
\t\treturn false;\n
\t});\n
\n
\treturn filter;\n
}\n
\n
function toolbarModuleFilterHtml() {\n
\tvar i,\n
\t\tmoduleFilterHtml = "";\n
\n
\tif ( !modulesList.length ) {\n
\t\treturn false;\n
\t}\n
\n
\tmodulesList.sort(function( a, b ) {\n
\t\treturn a.localeCompare( b );\n
\t});\n
\n
\tmoduleFilterHtml += "<label for=\'qunit-modulefilter\'>Module: </label>" +\n
\t\t"<select id=\'qunit-modulefilter\' name=\'modulefilter\'><option value=\'\' " +\n
\t\t( QUnit.urlParams.module === undefined ? "selected=\'selected\'" : "" ) +\n
\t\t">< All Modules ></option>";\n
\n
\tfor ( i = 0; i < modulesList.length; i++ ) {\n
\t\tmoduleFilterHtml += "<option value=\'" +\n
\t\t\tescapeText( encodeURIComponent( modulesList[ i ] ) ) + "\' " +\n
\t\t\t( QUnit.urlParams.module === modulesList[ i ] ? "selected=\'selected\'" : "" ) +\n
\t\t\t">" + escapeText( modulesList[ i ] ) + "</option>";\n
\t}\n
\tmoduleFilterHtml += "</select>";\n
\n
\treturn moduleFilterHtml;\n
}\n
\n
function toolbarModuleFilter() {\n
\tvar toolbar = id( "qunit-testrunner-toolbar" ),\n
\t\tmoduleFilter = document.createElement( "span" ),\n
\t\tmoduleFilterHtml = toolbarModuleFilterHtml();\n
\n
\tif ( !toolbar || !moduleFilterHtml ) {\n
\t\treturn false;\n
\t}\n
\n
\tmoduleFilter.setAttribute( "id", "qunit-modulefilter-container" );\n
\tmoduleFilter.innerHTML = moduleFilterHtml;\n
\n
\taddEvent( moduleFilter.lastChild, "change", applyUrlParams );\n
\n
\ttoolbar.appendChild( moduleFilter );\n
}\n
\n
function appendToolbar() {\n
\tvar toolbar = id( "qunit-testrunner-toolbar" );\n
\n
\tif ( toolbar ) {\n
\t\ttoolbar.appendChild( toolbarUrlConfigContainer() );\n
\t\ttoolbar.appendChild( toolbarLooseFilter() );\n
\t}\n
}\n
\n
function appendHeader() {\n
\tvar header = id( "qunit-header" );\n
\n
\tif ( header ) {\n
\t\theader.innerHTML = "<a href=\'" +\n
\t\t\tsetUrl({ filter: undefined, module: undefined, testId: undefined }) +\n
\t\t\t"\'>" + header.innerHTML + "</a> ";\n
\t}\n
}\n
\n
function appendBanner() {\n
\tvar banner = id( "qunit-banner" );\n
\n
\tif ( banner ) {\n
\t\tbanner.className = "";\n
\t}\n
}\n
\n
function appendTestResults() {\n
\tvar tests = id( "qunit-tests" ),\n
\t\tresult = id( "qunit-testresult" );\n
\n
\tif ( result ) {\n
\t\tresult.parentNode.removeChild( result );\n
\t}\n
\n
\tif ( tests ) {\n
\t\ttests.innerHTML = "";\n
\t\tresult = document.createElement( "p" );\n
\t\tresult.id = "qunit-testresult";\n
\t\tresult.className = "result";\n
\t\ttests.parentNode.insertBefore( result, tests );\n
\t\tresult.innerHTML = "Running...<br />&#160;";\n
\t}\n
}\n
\n
function storeFixture() {\n
\tvar fixture = id( "qunit-fixture" );\n
\tif ( fixture ) {\n
\t\tconfig.fixture = fixture.innerHTML;\n
\t}\n
}\n
\n
function appendUserAgent() {\n
\tvar userAgent = id( "qunit-userAgent" );\n
\tif ( userAgent ) {\n
\t\tuserAgent.innerHTML = "";\n
\t\tuserAgent.appendChild( document.createTextNode( navigator.userAgent ) );\n
\t}\n
}\n
\n
function appendTestsList( modules ) {\n
\tvar i, l, x, z, test, moduleObj;\n
\n
\tfor ( i = 0, l = modules.length; i < l; i++ ) {\n
\t\tmoduleObj = modules[ i ];\n
\n
\t\tif ( moduleObj.name ) {\n
\t\t\tmodulesList.push( moduleObj.name );\n
\t\t}\n
\n
\t\tfor ( x = 0, z = moduleObj.tests.length; x < z; x++ ) {\n
\t\t\ttest = moduleObj.tests[ x ];\n
\n
\t\t\tappendTest( test.name, test.testId, moduleObj.name );\n
\t\t}\n
\t}\n
}\n
\n
function appendTest( name, testId, moduleName ) {\n
\tvar title, rerunTrigger, testBlock, assertList,\n
\t\ttests = id( "qunit-tests" );\n
\n
\tif ( !tests ) {\n
\t\treturn;\n
\t}\n
\n
\ttitle = document.createElement( "strong" );\n
\ttitle.innerHTML = getNameHtml( name, moduleName );\n
\n
\trerunTrigger = document.createElement( "a" );\n
\trerunTrigger.innerHTML = "Rerun";\n
\trerunTrigger.href = setUrl({ testId: testId });\n
\n
\ttestBlock = document.createElement( "li" );\n
\ttestBlock.appendChild( title );\n
\ttestBlock.appendChild( rerunTrigger );\n
\ttestBlock.id = "qunit-test-output-" + testId;\n
\n
\tassertList = document.createElement( "ol" );\n
\tassertList.className = "qunit-assert-list";\n
\n
\ttestBlock.appendChild( assertList );\n
\n
\ttests.appendChild( testBlock );\n
}\n
\n
// HTML Reporter initialization and load\n
QUnit.begin(function( details ) {\n
\tvar qunit = id( "qunit" );\n
\n
\t// Fixture is the only one necessary to run without the #qunit element\n
\tstoreFixture();\n
\n
\tif ( qunit ) {\n
\t\tqunit.innerHTML =\n
\t\t\t"<h1 id=\'qunit-header\'>" + escapeText( document.title ) + "</h1>" +\n
\t\t\t"<h2 id=\'qunit-banner\'></h2>" +\n
\t\t\t"<div id=\'qunit-testrunner-toolbar\'></div>" +\n
\t\t\t"<h2 id=\'qunit-userAgent\'></h2>" +\n
\t\t\t"<ol id=\'qunit-tests\'></ol>";\n
\t}\n
\n
\tappendHeader();\n
\tappendBanner();\n
\tappendTestResults();\n
\tappendUserAgent();\n
\tappendToolbar();\n
\tappendTestsList( details.modules );\n
\ttoolbarModuleFilter();\n
\n
\tif ( qunit && config.hidepassed ) {\n
\t\taddClass( qunit.lastChild, "hidepass" );\n
\t}\n
});\n
\n
QUnit.done(function( details ) {\n
\tvar i, key,\n
\t\tbanner = id( "qunit-banner" ),\n
\t\ttests = id( "qunit-tests" ),\n
\t\thtml = [\n
\t\t\t"Tests completed in ",\n
\t\t\tdetails.runtime,\n
\t\t\t" milliseconds.<br />",\n
\t\t\t"<span class=\'passed\'>",\n
\t\t\tdetails.passed,\n
\t\t\t"</span> assertions of <span class=\'total\'>",\n
\t\t\tdetails.total,\n
\t\t\t"</span> passed, <span class=\'failed\'>",\n
\t\t\tdetails.failed,\n
\t\t\t"</span> failed."\n
\t\t].join( "" );\n
\n
\tif ( banner ) {\n
\t\tbanner.className = details.failed ? "qunit-fail" : "qunit-pass";\n
\t}\n
\n
\tif ( tests ) {\n
\t\tid( "qunit-testresult" ).innerHTML = html;\n
\t}\n
\n
\tif ( config.altertitle && defined.document && document.title ) {\n
\n
\t\t// show ✖ for good, ✔ for bad suite result in title\n
\t\t// use escape sequences in case file gets loaded with non-utf-8-charset\n
\t\tdocument.title = [\n
\t\t\t( details.failed ? "\\u2716" : "\\u2714" ),\n
\t\t\tdocument.title.replace( /^[\\u2714\\u2716] /i, "" )\n
\t\t].join( " " );\n
\t}\n
\n
\t// clear own sessionStorage items if all tests passed\n
\tif ( config.reorder && defined.sessionStorage && details.failed === 0 ) {\n
\t\tfor ( i = 0; i < sessionStorage.length; i++ ) {\n
\t\t\tkey = sessionStorage.key( i++ );\n
\t\t\tif ( key.indexOf( "qunit-test-" ) === 0 ) {\n
\t\t\t\tsessionStorage.removeItem( key );\n
\t\t\t}\n
\t\t}\n
\t}\n
\n
\t// scroll back to top to show results\n
\tif ( config.scrolltop && window.scrollTo ) {\n
\t\twindow.scrollTo( 0, 0 );\n
\t}\n
});\n
\n
function getNameHtml( name, module ) {\n
\tvar nameHtml = "";\n
\n
\tif ( module ) {\n
\t\tnameHtml = "<span class=\'module-name\'>" + escapeText( module ) + "</span>: ";\n
\t}\n
\n
\tnameHtml += "<span class=\'test-name\'>" + escapeText( name ) + "</span>";\n
\n
\treturn nameHtml;\n
}\n
\n
QUnit.testStart(function( details ) {\n
\tvar running, testBlock;\n
\n
\ttestBlock = id( "qunit-test-output-" + details.testId );\n
\tif ( testBlock ) {\n
\t\ttestBlock.className = "running";\n
\t} else {\n
\n
\t\t// Report later registered tests\n
\t\tappendTest( details.name, details.testId, details.module );\n
\t}\n
\n
\trunning = id( "qunit-testresult" );\n
\tif ( running ) {\n
\t\trunning.innerHTML = "Running: <br />" + getNameHtml( details.name, details.module );\n
\t}\n
\n
});\n
\n
QUnit.log(function( details ) {\n
\tvar assertList, assertLi,\n
\t\tmessage, expected, actual,\n
\t\ttestItem = id( "qunit-test-output-" + details.testId );\n
\n
\tif ( !testItem ) {\n
\t\treturn;\n
\t}\n
\n
\tmessage = escapeText( details.message ) || ( details.result ? "okay" : "failed" );\n
\tmessage = "<span class=\'test-message\'>" + message + "</span>";\n
\tmessage += "<span class=\'runtime\'>@ " + details.runtime + " ms</span>";\n
\n
\t// pushFailure doesn\'t provide details.expected\n
\t// when it calls, it\'s implicit to also not show expected and diff stuff\n
\t// Also, we need to check details.expected existence, as it can exist and be undefined\n
\tif ( !details.result && hasOwn.call( details, "expected" ) ) {\n
\t\texpected = escapeText( QUnit.dump.parse( details.expected ) );\n
\t\tactual = escapeText( QUnit.dump.parse( details.actual ) );\n
\t\tmessage += "<table><tr class=\'test-expected\'><th>Expected: </th><td><pre>" +\n
\t\t\texpected +\n
\t\t\t"</pre></td></tr>";\n
\n
\t\tif ( actual !== expected ) {\n
\t\t\tmessage += "<tr class=\'test-actual\'><th>Result: </th><td><pre>" +\n
\t\t\t\tactual + "</pre></td></tr>" +\n
\t\t\t\t"<tr class=\'test-diff\'><th>Diff: </th><td><pre>" +\n
\t\t\t\tQUnit.diff( expected, actual ) + "</pre></td></tr>";\n
\t\t}\n
\n
\t\tif ( details.source ) {\n
\t\t\tmessage += "<tr class=\'test-source\'><th>Source: </th><td><pre>" +\n
\t\t\t\tescapeText( details.source ) + "</pre></td></tr>";\n
\t\t}\n
\n
\t\tmessage += "</table>";\n
\n
\t// this occours when pushFailure is set and we have an extracted stack trace\n
\t} else if ( !details.result && details.source ) {\n
\t\tmessage += "<table>" +\n
\t\t\t"<tr class=\'test-source\'><th>Source: </th><td><pre>" +\n
\t\t\tescapeText( details.source ) + "</pre></td></tr>" +\n
\t\t\t"</table>";\n
\t}\n
\n
\tassertList = testItem.getElementsByTagName( "ol" )[ 0 ];\n
\n
\tassertLi = document.createElement( "li" );\n
\tassertLi.className = details.result ? "pass" : "fail";\n
\tassertLi.innerHTML = message;\n
\tassertList.appendChild( assertLi );\n
});\n
\n
QUnit.testDone(function( details ) {\n
\tvar testTitle, time, testItem, assertList,\n
\t\tgood, bad, testCounts, skipped,\n
\t\ttests = id( "qunit-tests" );\n
\n
\tif ( !tests ) {\n
\t\treturn;\n
\t}\n
\n
\ttestItem = id( "qunit-test-output-" + details.testId );\n
\n
\tassertList = testItem.getElementsByTagName( "ol" )[ 0 ];\n
\n
\tgood = details.passed;\n
\tbad = details.failed;\n
\n
\t// store result when possible\n
\tif ( config.reorder && defined.sessionStorage ) {\n
\t\tif ( bad ) {\n
\t\t\tsessionStorage.setItem( "qunit-test-" + details.module + "-" + details.name, bad );\n
\t\t} else {\n
\t\t\tsessionStorage.removeItem( "qunit-test-" + details.module + "-" + details.name );\n
\t\t}\n
\t}\n
\n
\tif ( bad === 0 ) {\n
\t\taddClass( assertList, "qunit-collapsed" );\n
\t}\n
\n
\t// testItem.firstChild is the test name\n
\ttestTitle = testItem.firstChild;\n
\n
\ttestCounts = bad ?\n
\t\t"<b class=\'failed\'>" + bad + "</b>, " + "<b class=\'passed\'>" + good + "</b>, " :\n
\t\t"";\n
\n
\ttestTitle.innerHTML += " <b class=\'counts\'>(" + testCounts +\n
\t\tdetails.assertions.length + ")</b>";\n
\n
\tif ( details.skipped ) {\n
\t\ttestItem.className = "skipped";\n
\t\tskipped = document.createElement( "em" );\n
\t\tskipped.className = "qunit-skipped-label";\n
\t\tskipped.innerHTML = "skipped";\n
\t\ttestItem.insertBefore( skipped, testTitle );\n
\t} else {\n
\t\taddEvent( testTitle, "click", function() {\n
\t\t\ttoggleClass( assertList, "qunit-collapsed" );\n
\t\t});\n
\n
\t\ttestItem.className = bad ? "fail" : "pass";\n
\n
\t\ttime = document.createElement( "span" );\n
\t\ttime.className = "runtime";\n
\t\ttime.innerHTML = details.runtime + " ms";\n
\t\ttestItem.insertBefore( time, assertList );\n
\t}\n
});\n
\n
if ( !defined.document || document.readyState === "complete" ) {\n
\tconfig.pageLoaded = true;\n
\tconfig.autorun = true;\n
}\n
\n
if ( defined.document ) {\n
\taddEvent( window, "load", QUnit.load );\n
}\n
\n
})();\n


]]></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
