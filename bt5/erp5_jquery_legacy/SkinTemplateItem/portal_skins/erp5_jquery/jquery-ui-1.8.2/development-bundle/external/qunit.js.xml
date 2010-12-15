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
            <value> <string>ts77895651.82</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>qunit.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/x-javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*\n
 * QUnit - A JavaScript Unit Testing Framework\n
 * \n
 * http://docs.jquery.com/QUnit\n
 *\n
 * Copyright (c) 2009 John Resig, Jörn Zaefferer\n
 * Dual licensed under the MIT (MIT-LICENSE.txt)\n
 * and GPL (GPL-LICENSE.txt) licenses.\n
 */\n
\n
(function(window) {\n
\n
var QUnit = {\n
\n
\t// Initialize the configuration options\n
\tinit: function() {\n
\t\tconfig = {\n
\t\t\tstats: { all: 0, bad: 0 },\n
\t\t\tmoduleStats: { all: 0, bad: 0 },\n
\t\t\tstarted: +new Date,\n
\t\t\tupdateRate: 1000,\n
\t\t\tblocking: false,\n
\t\t\tautorun: false,\n
\t\t\tassertions: [],\n
\t\t\tfilters: [],\n
\t\t\tqueue: []\n
\t\t};\n
\n
\t\tvar tests = id("qunit-tests"),\n
\t\t\tbanner = id("qunit-banner"),\n
\t\t\tresult = id("qunit-testresult");\n
\n
\t\tif ( tests ) {\n
\t\t\ttests.innerHTML = "";\n
\t\t}\n
\n
\t\tif ( banner ) {\n
\t\t\tbanner.className = "";\n
\t\t}\n
\n
\t\tif ( result ) {\n
\t\t\tresult.parentNode.removeChild( result );\n
\t\t}\n
\t},\n
\t\n
\t// call on start of module test to prepend name to all tests\n
\tmodule: function(name, testEnvironment) {\n
\t\tconfig.currentModule = name;\n
\n
\t\tsynchronize(function() {\n
\t\t\tif ( config.currentModule ) {\n
\t\t\t\tQUnit.moduleDone( config.currentModule, config.moduleStats.bad, config.moduleStats.all );\n
\t\t\t}\n
\n
\t\t\tconfig.currentModule = name;\n
\t\t\tconfig.moduleTestEnvironment = testEnvironment;\n
\t\t\tconfig.moduleStats = { all: 0, bad: 0 };\n
\n
\t\t\tQUnit.moduleStart( name, testEnvironment );\n
\t\t});\n
\t},\n
\n
\tasyncTest: function(testName, expected, callback) {\n
\t\tif ( arguments.length === 2 ) {\n
\t\t\tcallback = expected;\n
\t\t\texpected = 0;\n
\t\t}\n
\n
\t\tQUnit.test(testName, expected, callback, true);\n
\t},\n
\t\n
\ttest: function(testName, expected, callback, async) {\n
\t\tvar name = testName, testEnvironment, testEnvironmentArg;\n
\n
\t\tif ( arguments.length === 2 ) {\n
\t\t\tcallback = expected;\n
\t\t\texpected = null;\n
\t\t}\n
\t\t// is 2nd argument a testEnvironment?\n
\t\tif ( expected && typeof expected === \'object\') {\n
\t\t\ttestEnvironmentArg =  expected;\n
\t\t\texpected = null;\n
\t\t}\n
\n
\t\tif ( config.currentModule ) {\n
\t\t\tname = config.currentModule + " module: " + name;\n
\t\t}\n
\n
\t\tif ( !validTest(name) ) {\n
\t\t\treturn;\n
\t\t}\n
\n
\t\tsynchronize(function() {\n
\t\t\tQUnit.testStart( testName );\n
\n
\t\t\ttestEnvironment = extend({\n
\t\t\t\tsetup: function() {},\n
\t\t\t\tteardown: function() {}\n
\t\t\t}, config.moduleTestEnvironment);\n
\t\t\tif (testEnvironmentArg) {\n
\t\t\t\textend(testEnvironment,testEnvironmentArg);\n
\t\t\t}\n
\n
\t\t\t// allow utility functions to access the current test environment\n
\t\t\tQUnit.current_testEnvironment = testEnvironment;\n
\t\t\t\n
\t\t\tconfig.assertions = [];\n
\t\t\tconfig.expected = expected;\n
\n
\t\t\ttry {\n
\t\t\t\tif ( !config.pollution ) {\n
\t\t\t\t\tsaveGlobal();\n
\t\t\t\t}\n
\n
\t\t\t\ttestEnvironment.setup.call(testEnvironment);\n
\t\t\t} catch(e) {\n
\t\t\t\tQUnit.ok( false, "Setup failed on " + name + ": " + e.message );\n
\t\t\t}\n
\n
\t\t\tif ( async ) {\n
\t\t\t\tQUnit.stop();\n
\t\t\t}\n
\n
\t\t\ttry {\n
\t\t\t\tcallback.call(testEnvironment);\n
\t\t\t} catch(e) {\n
\t\t\t\tfail("Test " + name + " died, exception and test follows", e, callback);\n
\t\t\t\tQUnit.ok( false, "Died on test #" + (config.assertions.length + 1) + ": " + e.message );\n
\t\t\t\t// else next test will carry the responsibility\n
\t\t\t\tsaveGlobal();\n
\n
\t\t\t\t// Restart the tests if they\'re blocking\n
\t\t\t\tif ( config.blocking ) {\n
\t\t\t\t\tstart();\n
\t\t\t\t}\n
\t\t\t}\n
\t\t});\n
\n
\t\tsynchronize(function() {\n
\t\t\ttry {\n
\t\t\t\tcheckPollution();\n
\t\t\t\ttestEnvironment.teardown.call(testEnvironment);\n
\t\t\t} catch(e) {\n
\t\t\t\tQUnit.ok( false, "Teardown failed on " + name + ": " + e.message );\n
\t\t\t}\n
\n
\t\t\ttry {\n
\t\t\t\tQUnit.reset();\n
\t\t\t} catch(e) {\n
\t\t\t\tfail("reset() failed, following Test " + name + ", exception and reset fn follows", e, reset);\n
\t\t\t}\n
\n
\t\t\tif ( config.expected && config.expected != config.assertions.length ) {\n
\t\t\t\tQUnit.ok( false, "Expected " + config.expected + " assertions, but " + config.assertions.length + " were run" );\n
\t\t\t}\n
\n
\t\t\tvar good = 0, bad = 0,\n
\t\t\t\ttests = id("qunit-tests");\n
\n
\t\t\tconfig.stats.all += config.assertions.length;\n
\t\t\tconfig.moduleStats.all += config.assertions.length;\n
\n
\t\t\tif ( tests ) {\n
\t\t\t\tvar ol  = document.createElement("ol");\n
\t\t\t\tol.style.display = "none";\n
\n
\t\t\t\tfor ( var i = 0; i < config.assertions.length; i++ ) {\n
\t\t\t\t\tvar assertion = config.assertions[i];\n
\n
\t\t\t\t\tvar li = document.createElement("li");\n
\t\t\t\t\tli.className = assertion.result ? "pass" : "fail";\n
\t\t\t\t\tli.appendChild(document.createTextNode(assertion.message || "(no message)"));\n
\t\t\t\t\tol.appendChild( li );\n
\n
\t\t\t\t\tif ( assertion.result ) {\n
\t\t\t\t\t\tgood++;\n
\t\t\t\t\t} else {\n
\t\t\t\t\t\tbad++;\n
\t\t\t\t\t\tconfig.stats.bad++;\n
\t\t\t\t\t\tconfig.moduleStats.bad++;\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\n
\t\t\t\tvar b = document.createElement("strong");\n
\t\t\t\tb.innerHTML = name + " <b style=\'color:black;\'>(<b class=\'fail\'>" + bad + "</b>, <b class=\'pass\'>" + good + "</b>, " + config.assertions.length + ")</b>";\n
\t\t\t\t\n
\t\t\t\taddEvent(b, "click", function() {\n
\t\t\t\t\tvar next = b.nextSibling, display = next.style.display;\n
\t\t\t\t\tnext.style.display = display === "none" ? "block" : "none";\n
\t\t\t\t});\n
\t\t\t\t\n
\t\t\t\taddEvent(b, "dblclick", function(e) {\n
\t\t\t\t\tvar target = e && e.target ? e.target : window.event.srcElement;\n
\t\t\t\t\tif ( target.nodeName.toLowerCase() === "strong" ) {\n
\t\t\t\t\t\tvar text = "", node = target.firstChild;\n
\n
\t\t\t\t\t\twhile ( node.nodeType === 3 ) {\n
\t\t\t\t\t\t\ttext += node.nodeValue;\n
\t\t\t\t\t\t\tnode = node.nextSibling;\n
\t\t\t\t\t\t}\n
\n
\t\t\t\t\t\ttext = text.replace(/(^\\s*|\\s*$)/g, "");\n
\n
\t\t\t\t\t\tif ( window.location ) {\n
\t\t\t\t\t\t\twindow.location.href = window.location.href.match(/^(.+?)(\\?.*)?$/)[1] + "?" + encodeURIComponent(text);\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\t\t\t\t});\n
\n
\t\t\t\tvar li = document.createElement("li");\n
\t\t\t\tli.className = bad ? "fail" : "pass";\n
\t\t\t\tli.appendChild( b );\n
\t\t\t\tli.appendChild( ol );\n
\t\t\t\ttests.appendChild( li );\n
\n
\t\t\t\tif ( bad ) {\n
\t\t\t\t\tvar toolbar = id("qunit-testrunner-toolbar");\n
\t\t\t\t\tif ( toolbar ) {\n
\t\t\t\t\t\ttoolbar.style.display = "block";\n
\t\t\t\t\t\tid("qunit-filter-pass").disabled = null;\n
\t\t\t\t\t\tid("qunit-filter-missing").disabled = null;\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\n
\t\t\t} else {\n
\t\t\t\tfor ( var i = 0; i < config.assertions.length; i++ ) {\n
\t\t\t\t\tif ( !config.assertions[i].result ) {\n
\t\t\t\t\t\tbad++;\n
\t\t\t\t\t\tconfig.stats.bad++;\n
\t\t\t\t\t\tconfig.moduleStats.bad++;\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t}\n
\n
\t\t\tQUnit.testDone( testName, bad, config.assertions.length );\n
\n
\t\t\tif ( !window.setTimeout && !config.queue.length ) {\n
\t\t\t\tdone();\n
\t\t\t}\n
\t\t});\n
\n
\t\tif ( window.setTimeout && !config.doneTimer ) {\n
\t\t\tconfig.doneTimer = window.setTimeout(function(){\n
\t\t\t\tif ( !config.queue.length ) {\n
\t\t\t\t\tdone();\n
\t\t\t\t} else {\n
\t\t\t\t\tsynchronize( done );\n
\t\t\t\t}\n
\t\t\t}, 13);\n
\t\t}\n
\t},\n
\t\n
\t/**\n
\t * Specify the number of expected assertions to gurantee that failed test (no assertions are run at all) don\'t slip through.\n
\t */\n
\texpect: function(asserts) {\n
\t\tconfig.expected = asserts;\n
\t},\n
\n
\t/**\n
\t * Asserts true.\n
\t * @example ok( "asdfasdf".length > 5, "There must be at least 5 chars" );\n
\t */\n
\tok: function(a, msg) {\n
\t\tQUnit.log(a, msg);\n
\n
\t\tconfig.assertions.push({\n
\t\t\tresult: !!a,\n
\t\t\tmessage: msg\n
\t\t});\n
\t},\n
\n
\t/**\n
\t * Checks that the first two arguments are equal, with an optional message.\n
\t * Prints out both actual and expected values.\n
\t *\n
\t * Prefered to ok( actual == expected, message )\n
\t *\n
\t * @example equal( format("Received {0} bytes.", 2), "Received 2 bytes." );\n
\t *\n
\t * @param Object actual\n
\t * @param Object expected\n
\t * @param String message (optional)\n
\t */\n
\tequal: function(actual, expected, message) {\n
\t\tpush(expected == actual, actual, expected, message);\n
\t},\n
\n
\tnotEqual: function(actual, expected, message) {\n
\t\tpush(expected != actual, actual, expected, message);\n
\t},\n
\t\n
\tdeepEqual: function(a, b, message) {\n
\t\tpush(QUnit.equiv(a, b), a, b, message);\n
\t},\n
\n
\tnotDeepEqual: function(a, b, message) {\n
\t\tpush(!QUnit.equiv(a, b), a, b, message);\n
\t},\n
\n
\tstrictEqual: function(actual, expected, message) {\n
\t\tpush(expected === actual, actual, expected, message);\n
\t},\n
\n
\tnotStrictEqual: function(actual, expected, message) {\n
\t\tpush(expected !== actual, actual, expected, message);\n
\t},\n
\t\n
\tstart: function() {\n
\t\t// A slight delay, to avoid any current callbacks\n
\t\tif ( window.setTimeout ) {\n
\t\t\twindow.setTimeout(function() {\n
\t\t\t\tif ( config.timeout ) {\n
\t\t\t\t\tclearTimeout(config.timeout);\n
\t\t\t\t}\n
\n
\t\t\t\tconfig.blocking = false;\n
\t\t\t\tprocess();\n
\t\t\t}, 13);\n
\t\t} else {\n
\t\t\tconfig.blocking = false;\n
\t\t\tprocess();\n
\t\t}\n
\t},\n
\t\n
\tstop: function(timeout) {\n
\t\tconfig.blocking = true;\n
\n
\t\tif ( timeout && window.setTimeout ) {\n
\t\t\tconfig.timeout = window.setTimeout(function() {\n
\t\t\t\tQUnit.ok( false, "Test timed out" );\n
\t\t\t\tQUnit.start();\n
\t\t\t}, timeout);\n
\t\t}\n
\t},\n
\t\n
\t/**\n
\t * Resets the test setup. Useful for tests that modify the DOM.\n
\t */\n
\treset: function() {\n
\t\tif ( window.jQuery ) {\n
\t\t\tjQuery("#main").html( config.fixture );\n
\t\t\tjQuery.event.global = {};\n
\t\t\tjQuery.ajaxSettings = extend({}, config.ajaxSettings);\n
\t\t}\n
\t},\n
\t\n
\t/**\n
\t * Trigger an event on an element.\n
\t *\n
\t * @example triggerEvent( document.body, "click" );\n
\t *\n
\t * @param DOMElement elem\n
\t * @param String type\n
\t */\n
\ttriggerEvent: function( elem, type, event ) {\n
\t\tif ( document.createEvent ) {\n
\t\t\tevent = document.createEvent("MouseEvents");\n
\t\t\tevent.initMouseEvent(type, true, true, elem.ownerDocument.defaultView,\n
\t\t\t\t0, 0, 0, 0, 0, false, false, false, false, 0, null);\n
\t\t\telem.dispatchEvent( event );\n
\n
\t\t} else if ( elem.fireEvent ) {\n
\t\t\telem.fireEvent("on"+type);\n
\t\t}\n
\t},\n
\t\n
\t// Safe object type checking\n
\tis: function( type, obj ) {\n
\t\treturn Object.prototype.toString.call( obj ) === "[object "+ type +"]";\n
\t},\n
\t\n
\t// Logging callbacks\n
\tdone: function(failures, total) {},\n
\tlog: function(result, message) {},\n
\ttestStart: function(name) {},\n
\ttestDone: function(name, failures, total) {},\n
\tmoduleStart: function(name, testEnvironment) {},\n
\tmoduleDone: function(name, failures, total) {}\n
};\n
\n
// Backwards compatibility, deprecated\n
QUnit.equals = QUnit.equal;\n
QUnit.same = QUnit.deepEqual;\n
\n
// Maintain internal state\n
var config = {\n
\t// The queue of tests to run\n
\tqueue: [],\n
\n
\t// block until document ready\n
\tblocking: true\n
};\n
\n
// Load paramaters\n
(function() {\n
\tvar location = window.location || { search: "", protocol: "file:" },\n
\t\tGETParams = location.search.slice(1).split(\'&\');\n
\n
\tfor ( var i = 0; i < GETParams.length; i++ ) {\n
\t\tGETParams[i] = decodeURIComponent( GETParams[i] );\n
\t\tif ( GETParams[i] === "noglobals" ) {\n
\t\t\tGETParams.splice( i, 1 );\n
\t\t\ti--;\n
\t\t\tconfig.noglobals = true;\n
\t\t} else if ( GETParams[i].search(\'=\') > -1 ) {\n
\t\t\tGETParams.splice( i, 1 );\n
\t\t\ti--;\n
\t\t}\n
\t}\n
\t\n
\t// restrict modules/tests by get parameters\n
\tconfig.filters = GETParams;\n
\t\n
\t// Figure out if we\'re running the tests from a server or not\n
\tQUnit.isLocal = !!(location.protocol === \'file:\');\n
})();\n
\n
// Expose the API as global variables, unless an \'exports\'\n
// object exists, in that case we assume we\'re in CommonJS\n
if ( typeof exports === "undefined" || typeof require === "undefined" ) {\n
\textend(window, QUnit);\n
\twindow.QUnit = QUnit;\n
} else {\n
\textend(exports, QUnit);\n
\texports.QUnit = QUnit;\n
}\n
\n
if ( typeof document === "undefined" || document.readyState === "complete" ) {\n
\tconfig.autorun = true;\n
}\n
\n
addEvent(window, "load", function() {\n
\t// Initialize the config, saving the execution queue\n
\tvar oldconfig = extend({}, config);\n
\tQUnit.init();\n
\textend(config, oldconfig);\n
\n
\tconfig.blocking = false;\n
\n
\tvar userAgent = id("qunit-userAgent");\n
\tif ( userAgent ) {\n
\t\tuserAgent.innerHTML = navigator.userAgent;\n
\t}\n
\t\n
\tvar toolbar = id("qunit-testrunner-toolbar");\n
\tif ( toolbar ) {\n
\t\ttoolbar.style.display = "none";\n
\t\t\n
\t\tvar filter = document.createElement("input");\n
\t\tfilter.type = "checkbox";\n
\t\tfilter.id = "qunit-filter-pass";\n
\t\tfilter.disabled = true;\n
\t\taddEvent( filter, "click", function() {\n
\t\t\tvar li = document.getElementsByTagName("li");\n
\t\t\tfor ( var i = 0; i < li.length; i++ ) {\n
\t\t\t\tif ( li[i].className.indexOf("pass") > -1 ) {\n
\t\t\t\t\tli[i].style.display = filter.checked ? "none" : "";\n
\t\t\t\t}\n
\t\t\t}\n
\t\t});\n
\t\ttoolbar.appendChild( filter );\n
\n
\t\tvar label = document.createElement("label");\n
\t\tlabel.setAttribute("for", "qunit-filter-pass");\n
\t\tlabel.innerHTML = "Hide passed tests";\n
\t\ttoolbar.appendChild( label );\n
\n
\t\tvar missing = document.createElement("input");\n
\t\tmissing.type = "checkbox";\n
\t\tmissing.id = "qunit-filter-missing";\n
\t\tmissing.disabled = true;\n
\t\taddEvent( missing, "click", function() {\n
\t\t\tvar li = document.getElementsByTagName("li");\n
\t\t\tfor ( var i = 0; i < li.length; i++ ) {\n
\t\t\t\tif ( li[i].className.indexOf("fail") > -1 && li[i].innerHTML.indexOf(\'missing test - untested code is broken code\') > - 1 ) {\n
\t\t\t\t\tli[i].parentNode.parentNode.style.display = missing.checked ? "none" : "block";\n
\t\t\t\t}\n
\t\t\t}\n
\t\t});\n
\t\ttoolbar.appendChild( missing );\n
\n
\t\tlabel = document.createElement("label");\n
\t\tlabel.setAttribute("for", "qunit-filter-missing");\n
\t\tlabel.innerHTML = "Hide missing tests (untested code is broken code)";\n
\t\ttoolbar.appendChild( label );\n
\t}\n
\n
\tvar main = id(\'main\');\n
\tif ( main ) {\n
\t\tconfig.fixture = main.innerHTML;\n
\t}\n
\n
\tif ( window.jQuery ) {\n
\t\tconfig.ajaxSettings = window.jQuery.ajaxSettings;\n
\t}\n
\n
\tQUnit.start();\n
});\n
\n
function done() {\n
\tif ( config.doneTimer && window.clearTimeout ) {\n
\t\twindow.clearTimeout( config.doneTimer );\n
\t\tconfig.doneTimer = null;\n
\t}\n
\n
\tif ( config.queue.length ) {\n
\t\tconfig.doneTimer = window.setTimeout(function(){\n
\t\t\tif ( !config.queue.length ) {\n
\t\t\t\tdone();\n
\t\t\t} else {\n
\t\t\t\tsynchronize( done );\n
\t\t\t}\n
\t\t}, 13);\n
\n
\t\treturn;\n
\t}\n
\n
\tconfig.autorun = true;\n
\n
\t// Log the last module results\n
\tif ( config.currentModule ) {\n
\t\tQUnit.moduleDone( config.currentModule, config.moduleStats.bad, config.moduleStats.all );\n
\t}\n
\n
\tvar banner = id("qunit-banner"),\n
\t\ttests = id("qunit-tests"),\n
\t\thtml = [\'Tests completed in \',\n
\t\t+new Date - config.started, \' milliseconds.<br/>\',\n
\t\t\'<span class="passed">\', config.stats.all - config.stats.bad, \'</span> tests of <span class="total">\', config.stats.all, \'</span> passed, <span class="failed">\', config.stats.bad,\'</span> failed.\'].join(\'\');\n
\n
\tif ( banner ) {\n
\t\tbanner.className = (config.stats.bad ? "qunit-fail" : "qunit-pass");\n
\t}\n
\n
\tif ( tests ) {\t\n
\t\tvar result = id("qunit-testresult");\n
\n
\t\tif ( !result ) {\n
\t\t\tresult = document.createElement("p");\n
\t\t\tresult.id = "qunit-testresult";\n
\t\t\tresult.className = "result";\n
\t\t\ttests.parentNode.insertBefore( result, tests.nextSibling );\n
\t\t}\n
\n
\t\tresult.innerHTML = html;\n
\t}\n
\n
\tQUnit.done( config.stats.bad, config.stats.all );\n
}\n
\n
function validTest( name ) {\n
\tvar i = config.filters.length,\n
\t\trun = false;\n
\n
\tif ( !i ) {\n
\t\treturn true;\n
\t}\n
\t\n
\twhile ( i-- ) {\n
\t\tvar filter = config.filters[i],\n
\t\t\tnot = filter.charAt(0) == \'!\';\n
\n
\t\tif ( not ) {\n
\t\t\tfilter = filter.slice(1);\n
\t\t}\n
\n
\t\tif ( name.indexOf(filter) !== -1 ) {\n
\t\t\treturn !not;\n
\t\t}\n
\n
\t\tif ( not ) {\n
\t\t\trun = true;\n
\t\t}\n
\t}\n
\n
\treturn run;\n
}\n
\n
function push(result, actual, expected, message) {\n
\tmessage = message || (result ? "okay" : "failed");\n
\tQUnit.ok( result, result ? message + ": " + QUnit.jsDump.parse(expected) : message + ", expected: " + QUnit.jsDump.parse(expected) + " result: " + QUnit.jsDump.parse(actual) );\n
}\n
\n
function synchronize( callback ) {\n
\tconfig.queue.push( callback );\n
\n
\tif ( config.autorun && !config.blocking ) {\n
\t\tprocess();\n
\t}\n
}\n
\n
function process() {\n
\tvar start = (new Date()).getTime();\n
\n
\twhile ( config.queue.length && !config.blocking ) {\n
\t\tif ( config.updateRate <= 0 || (((new Date()).getTime() - start) < config.updateRate) ) {\n
\t\t\tconfig.queue.shift()();\n
\n
\t\t} else {\n
\t\t\tsetTimeout( process, 13 );\n
\t\t\tbreak;\n
\t\t}\n
\t}\n
}\n
\n
function saveGlobal() {\n
\tconfig.pollution = [];\n
\t\n
\tif ( config.noglobals ) {\n
\t\tfor ( var key in window ) {\n
\t\t\tconfig.pollution.push( key );\n
\t\t}\n
\t}\n
}\n
\n
function checkPollution( name ) {\n
\tvar old = config.pollution;\n
\tsaveGlobal();\n
\t\n
\tvar newGlobals = diff( old, config.pollution );\n
\tif ( newGlobals.length > 0 ) {\n
\t\tok( false, "Introduced global variable(s): " + newGlobals.join(", ") );\n
\t\tconfig.expected++;\n
\t}\n
\n
\tvar deletedGlobals = diff( config.pollution, old );\n
\tif ( deletedGlobals.length > 0 ) {\n
\t\tok( false, "Deleted global variable(s): " + deletedGlobals.join(", ") );\n
\t\tconfig.expected++;\n
\t}\n
}\n
\n
// returns a new Array with the elements that are in a but not in b\n
function diff( a, b ) {\n
\tvar result = a.slice();\n
\tfor ( var i = 0; i < result.length; i++ ) {\n
\t\tfor ( var j = 0; j < b.length; j++ ) {\n
\t\t\tif ( result[i] === b[j] ) {\n
\t\t\t\tresult.splice(i, 1);\n
\t\t\t\ti--;\n
\t\t\t\tbreak;\n
\t\t\t}\n
\t\t}\n
\t}\n
\treturn result;\n
}\n
\n
function fail(message, exception, callback) {\n
\tif ( typeof console !== "undefined" && console.error && console.warn ) {\n
\t\tconsole.error(message);\n
\t\tconsole.error(exception);\n
\t\tconsole.warn(callback.toString());\n
\n
\t} else if ( window.opera && opera.postError ) {\n
\t\topera.postError(message, exception, callback.toString);\n
\t}\n
}\n
\n
function extend(a, b) {\n
\tfor ( var prop in b ) {\n
\t\ta[prop] = b[prop];\n
\t}\n
\n
\treturn a;\n
}\n
\n
function addEvent(elem, type, fn) {\n
\tif ( elem.addEventListener ) {\n
\t\telem.addEventListener( type, fn, false );\n
\t} else if ( elem.attachEvent ) {\n
\t\telem.attachEvent( "on" + type, fn );\n
\t} else {\n
\t\tfn();\n
\t}\n
}\n
\n
function id(name) {\n
\treturn !!(typeof document !== "undefined" && document && document.getElementById) &&\n
\t\tdocument.getElementById( name );\n
}\n
\n
// Test for equality any JavaScript type.\n
// Discussions and reference: http://philrathe.com/articles/equiv\n
// Test suites: http://philrathe.com/tests/equiv\n
// Author: Philippe Rathé <prathe@gmail.com>\n
QUnit.equiv = function () {\n
\n
    var innerEquiv; // the real equiv function\n
    var callers = []; // stack to decide between skip/abort functions\n
    var parents = []; // stack to avoiding loops from circular referencing\n
\n
\n
    // Determine what is o.\n
    function hoozit(o) {\n
        if (QUnit.is("String", o)) {\n
            return "string";\n
            \n
        } else if (QUnit.is("Boolean", o)) {\n
            return "boolean";\n
\n
        } else if (QUnit.is("Number", o)) {\n
\n
            if (isNaN(o)) {\n
                return "nan";\n
            } else {\n
                return "number";\n
            }\n
\n
        } else if (typeof o === "undefined") {\n
            return "undefined";\n
\n
        // consider: typeof null === object\n
        } else if (o === null) {\n
            return "null";\n
\n
        // consider: typeof [] === object\n
        } else if (QUnit.is( "Array", o)) {\n
            return "array";\n
        \n
        // consider: typeof new Date() === object\n
        } else if (QUnit.is( "Date", o)) {\n
            return "date";\n
\n
        // consider: /./ instanceof Object;\n
        //           /./ instanceof RegExp;\n
        //          typeof /./ === "function"; // => false in IE and Opera,\n
        //                                          true in FF and Safari\n
        } else if (QUnit.is( "RegExp", o)) {\n
            return "regexp";\n
\n
        } else if (typeof o === "object") {\n
            return "object";\n
\n
        } else if (QUnit.is( "Function", o)) {\n
            return "function";\n
        } else {\n
            return undefined;\n
        }\n
    }\n
\n
    // Call the o related callback with the given arguments.\n
    function bindCallbacks(o, callbacks, args) {\n
        var prop = hoozit(o);\n
        if (prop) {\n
            if (hoozit(callbacks[prop]) === "function") {\n
                return callbacks[prop].apply(callbacks, args);\n
            } else {\n
                return callbacks[prop]; // or undefined\n
            }\n
        }\n
    }\n
    \n
    var callbacks = function () {\n
\n
        // for string, boolean, number and null\n
        function useStrictEquality(b, a) {\n
            if (b instanceof a.constructor || a instanceof b.constructor) {\n
                // to catch short annotaion VS \'new\' annotation of a declaration\n
                // e.g. var i = 1;\n
                //      var j = new Number(1);\n
                return a == b;\n
            } else {\n
                return a === b;\n
            }\n
        }\n
\n
        return {\n
            "string": useStrictEquality,\n
            "boolean": useStrictEquality,\n
            "number": useStrictEquality,\n
            "null": useStrictEquality,\n
            "undefined": useStrictEquality,\n
\n
            "nan": function (b) {\n
                return isNaN(b);\n
            },\n
\n
            "date": function (b, a) {\n
                return hoozit(b) === "date" && a.valueOf() === b.valueOf();\n
            },\n
\n
            "regexp": function (b, a) {\n
                return hoozit(b) === "regexp" &&\n
                    a.source === b.source && // the regex itself\n
                    a.global === b.global && // and its modifers (gmi) ...\n
                    a.ignoreCase === b.ignoreCase &&\n
                    a.multiline === b.multiline;\n
            },\n
\n
            // - skip when the property is a method of an instance (OOP)\n
            // - abort otherwise,\n
            //   initial === would have catch identical references anyway\n
            "function": function () {\n
                var caller = callers[callers.length - 1];\n
                return caller !== Object &&\n
                        typeof caller !== "undefined";\n
            },\n
\n
            "array": function (b, a) {\n
                var i, j, loop;\n
                var len;\n
\n
                // b could be an object literal here\n
                if ( ! (hoozit(b) === "array")) {\n
                    return false;\n
                }   \n
                \n
                len = a.length;\n
                if (len !== b.length) { // safe and faster\n
                    return false;\n
                }\n
                \n
                //track reference to avoid circular references\n
                parents.push(a);\n
                for (i = 0; i < len; i++) {\n
                    loop = false;\n
                    for(j=0;j<parents.length;j++){\n
                        if(parents[j] === a[i]){\n
                            loop = true;//dont rewalk array\n
                        }\n
                    }\n
                    if (!loop && ! innerEquiv(a[i], b[i])) {\n
                        parents.pop();\n
                        return false;\n
                    }\n
                }\n
                parents.pop();\n
                return true;\n
            },\n
\n
            "object": function (b, a) {\n
                var i, j, loop;\n
                var eq = true; // unless we can proove it\n
                var aProperties = [], bProperties = []; // collection of strings\n
\n
                // comparing constructors is more strict than using instanceof\n
                if ( a.constructor !== b.constructor) {\n
                    return false;\n
                }\n
\n
                // stack constructor before traversing properties\n
                callers.push(a.constructor);\n
                //track reference to avoid circular references\n
                parents.push(a);\n
                \n
                for (i in a) { // be strict: don\'t ensures hasOwnProperty and go deep\n
                    loop = false;\n
                    for(j=0;j<parents.length;j++){\n
                        if(parents[j] === a[i])\n
                            loop = true; //don\'t go down the same path twice\n
                    }\n
                    aProperties.push(i); // collect a\'s properties\n
\n
                    if (!loop && ! innerEquiv(a[i], b[i])) {\n
                        eq = false;\n
                        break;\n
                    }\n
                }\n
\n
                callers.pop(); // unstack, we are done\n
                parents.pop();\n
\n
                for (i in b) {\n
                    bProperties.push(i); // collect b\'s properties\n
                }\n
\n
                // Ensures identical properties name\n
                return eq && innerEquiv(aProperties.sort(), bProperties.sort());\n
            }\n
        };\n
    }();\n
\n
    innerEquiv = function () { // can take multiple arguments\n
        var args = Array.prototype.slice.apply(arguments);\n
        if (args.length < 2) {\n
            return true; // end transition\n
        }\n
\n
        return (function (a, b) {\n
            if (a === b) {\n
                return true; // catch the most you can\n
            } else if (a === null || b === null || typeof a === "undefined" || typeof b === "undefined" || hoozit(a) !== hoozit(b)) {\n
                return false; // don\'t lose time with error prone cases\n
            } else {\n
                return bindCallbacks(a, callbacks, [b, a]);\n
            }\n
\n
        // apply transition with (1..n) arguments\n
        })(args[0], args[1]) && arguments.callee.apply(this, args.splice(1, args.length -1));\n
    };\n
\n
    return innerEquiv;\n
\n
}();\n
\n
/**\n
 * jsDump\n
 * Copyright (c) 2008 Ariel Flesler - aflesler(at)gmail(dot)com | http://flesler.blogspot.com\n
 * Licensed under BSD (http://www.opensource.org/licenses/bsd-license.php)\n
 * Date: 5/15/2008\n
 * @projectDescription Advanced and extensible data dumping for Javascript.\n
 * @version 1.0.0\n
 * @author Ariel Flesler\n
 * @link {http://flesler.blogspot.com/2008/05/jsdump-pretty-dump-of-any-javascript.html}\n
 */\n
QUnit.jsDump = (function() {\n
\tfunction quote( str ) {\n
\t\treturn \'"\' + str.toString().replace(/"/g, \'\\\\"\') + \'"\';\n
\t};\n
\tfunction literal( o ) {\n
\t\treturn o + \'\';\t\n
\t};\n
\tfunction join( pre, arr, post ) {\n
\t\tvar s = jsDump.separator(),\n
\t\t\tbase = jsDump.indent(),\n
\t\t\tinner = jsDump.indent(1);\n
\t\tif ( arr.join )\n
\t\t\tarr = arr.join( \',\' + s + inner );\n
\t\tif ( !arr )\n
\t\t\treturn pre + post;\n
\t\treturn [ pre, inner + arr, base + post ].join(s);\n
\t};\n
\tfunction array( arr ) {\n
\t\tvar i = arr.length,\tret = Array(i);\t\t\t\t\t\n
\t\tthis.up();\n
\t\twhile ( i-- )\n
\t\t\tret[i] = this.parse( arr[i] );\t\t\t\t\n
\t\tthis.down();\n
\t\treturn join( \'[\', ret, \']\' );\n
\t};\n
\t\n
\tvar reName = /^function (\\w+)/;\n
\t\n
\tvar jsDump = {\n
\t\tparse:function( obj, type ) { //type is used mostly internally, you can fix a (custom)type in advance\n
\t\t\tvar\tparser = this.parsers[ type || this.typeOf(obj) ];\n
\t\t\ttype = typeof parser;\t\t\t\n
\t\t\t\n
\t\t\treturn type == \'function\' ? parser.call( this, obj ) :\n
\t\t\t\t   type == \'string\' ? parser :\n
\t\t\t\t   this.parsers.error;\n
\t\t},\n
\t\ttypeOf:function( obj ) {\n
\t\t\tvar type;\n
\t\t\tif ( obj === null ) {\n
\t\t\t\ttype = "null";\n
\t\t\t} else if (typeof obj === "undefined") {\n
\t\t\t\ttype = "undefined";\n
\t\t\t} else if (QUnit.is("RegExp", obj)) {\n
\t\t\t\ttype = "regexp";\n
\t\t\t} else if (QUnit.is("Date", obj)) {\n
\t\t\t\ttype = "date";\n
\t\t\t} else if (QUnit.is("Function", obj)) {\n
\t\t\t\ttype = "function";\n
\t\t\t} else if (obj.setInterval && obj.document && !obj.nodeType) {\n
\t\t\t\ttype = "window";\n
\t\t\t} else if (obj.nodeType === 9) {\n
\t\t\t\ttype = "document";\n
\t\t\t} else if (obj.nodeType) {\n
\t\t\t\ttype = "node";\n
\t\t\t} else if (typeof obj === "object" && typeof obj.length === "number" && obj.length >= 0) {\n
\t\t\t\ttype = "array";\n
\t\t\t} else {\n
\t\t\t\ttype = typeof obj;\n
\t\t\t}\n
\t\t\treturn type;\n
\t\t},\n
\t\tseparator:function() {\n
\t\t\treturn this.multiline ?\tthis.HTML ? \'<br />\' : \'\\n\' : this.HTML ? \'&nbsp;\' : \' \';\n
\t\t},\n
\t\tindent:function( extra ) {// extra can be a number, shortcut for increasing-calling-decreasing\n
\t\t\tif ( !this.multiline )\n
\t\t\t\treturn \'\';\n
\t\t\tvar chr = this.indentChar;\n
\t\t\tif ( this.HTML )\n
\t\t\t\tchr = chr.replace(/\\t/g,\'   \').replace(/ /g,\'&nbsp;\');\n
\t\t\treturn Array( this._depth_ + (extra||0) ).join(chr);\n
\t\t},\n
\t\tup:function( a ) {\n
\t\t\tthis._depth_ += a || 1;\n
\t\t},\n
\t\tdown:function( a ) {\n
\t\t\tthis._depth_ -= a || 1;\n
\t\t},\n
\t\tsetParser:function( name, parser ) {\n
\t\t\tthis.parsers[name] = parser;\n
\t\t},\n
\t\t// The next 3 are exposed so you can use them\n
\t\tquote:quote, \n
\t\tliteral:literal,\n
\t\tjoin:join,\n
\t\t//\n
\t\t_depth_: 1,\n
\t\t// This is the list of parsers, to modify them, use jsDump.setParser\n
\t\tparsers:{\n
\t\t\twindow: \'[Window]\',\n
\t\t\tdocument: \'[Document]\',\n
\t\t\terror:\'[ERROR]\', //when no parser is found, shouldn\'t happen\n
\t\t\tunknown: \'[Unknown]\',\n
\t\t\t\'null\':\'null\',\n
\t\t\tundefined:\'undefined\',\n
\t\t\t\'function\':function( fn ) {\n
\t\t\t\tvar ret = \'function\',\n
\t\t\t\t\tname = \'name\' in fn ? fn.name : (reName.exec(fn)||[])[1];//functions never have name in IE\n
\t\t\t\tif ( name )\n
\t\t\t\t\tret += \' \' + name;\n
\t\t\t\tret += \'(\';\n
\t\t\t\t\n
\t\t\t\tret = [ ret, this.parse( fn, \'functionArgs\' ), \'){\'].join(\'\');\n
\t\t\t\treturn join( ret, this.parse(fn,\'functionCode\'), \'}\' );\n
\t\t\t},\n
\t\t\tarray: array,\n
\t\t\tnodelist: array,\n
\t\t\targuments: array,\n
\t\t\tobject:function( map ) {\n
\t\t\t\tvar ret = [ ];\n
\t\t\t\tthis.up();\n
\t\t\t\tfor ( var key in map )\n
\t\t\t\t\tret.push( this.parse(key,\'key\') + \': \' + this.parse(map[key]) );\n
\t\t\t\tthis.down();\n
\t\t\t\treturn join( \'{\', ret, \'}\' );\n
\t\t\t},\n
\t\t\tnode:function( node ) {\n
\t\t\t\tvar open = this.HTML ? \'&lt;\' : \'<\',\n
\t\t\t\t\tclose = this.HTML ? \'&gt;\' : \'>\';\n
\t\t\t\t\t\n
\t\t\t\tvar tag = node.nodeName.toLowerCase(),\n
\t\t\t\t\tret = open + tag;\n
\t\t\t\t\t\n
\t\t\t\tfor ( var a in this.DOMAttrs ) {\n
\t\t\t\t\tvar val = node[this.DOMAttrs[a]];\n
\t\t\t\t\tif ( val )\n
\t\t\t\t\t\tret += \' \' + a + \'=\' + this.parse( val, \'attribute\' );\n
\t\t\t\t}\n
\t\t\t\treturn ret + close + open + \'/\' + tag + close;\n
\t\t\t},\n
\t\t\tfunctionArgs:function( fn ) {//function calls it internally, it\'s the arguments part of the function\n
\t\t\t\tvar l = fn.length;\n
\t\t\t\tif ( !l ) return \'\';\t\t\t\t\n
\t\t\t\t\n
\t\t\t\tvar args = Array(l);\n
\t\t\t\twhile ( l-- )\n
\t\t\t\t\targs[l] = String.fromCharCode(97+l);//97 is \'a\'\n
\t\t\t\treturn \' \' + args.join(\', \') + \' \';\n
\t\t\t},\n
\t\t\tkey:quote, //object calls it internally, the key part of an item in a map\n
\t\t\tfunctionCode:\'[code]\', //function calls it internally, it\'s the content of the function\n
\t\t\tattribute:quote, //node calls it internally, it\'s an html attribute value\n
\t\t\tstring:quote,\n
\t\t\tdate:quote,\n
\t\t\tregexp:literal, //regex\n
\t\t\tnumber:literal,\n
\t\t\t\'boolean\':literal\n
\t\t},\n
\t\tDOMAttrs:{//attributes to dump from nodes, name=>realName\n
\t\t\tid:\'id\',\n
\t\t\tname:\'name\',\n
\t\t\t\'class\':\'className\'\n
\t\t},\n
\t\tHTML:false,//if true, entities are escaped ( <, >, \\t, space and \\n )\n
\t\tindentChar:\'   \',//indentation unit\n
\t\tmultiline:false //if true, items in a collection, are separated by a \\n, else just a space.\n
\t};\n
\n
\treturn jsDump;\n
})();\n
\n
})(this);\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>29043</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
