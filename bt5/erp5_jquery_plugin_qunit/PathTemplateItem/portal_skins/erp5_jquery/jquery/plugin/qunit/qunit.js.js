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
            <value> <string>ts33438286.57</string> </value>
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
            <value> <string encoding="cdata"><![CDATA[

/**\n
 * QUnit v1.5.0pre - A JavaScript Unit Testing Framework\n
 *\n
 * http://docs.jquery.com/QUnit\n
 *\n
 * Copyright (c) 2012 John Resig, Jörn Zaefferer\n
 * Dual licensed under the MIT (MIT-LICENSE.txt)\n
 * or GPL (GPL-LICENSE.txt) licenses.\n
 */\n
\n
(function(window) {\n
\n
var defined = {\n
\tsetTimeout: typeof window.setTimeout !== "undefined",\n
\tsessionStorage: (function() {\n
\t\tvar x = "qunit-test-string";\n
\t\ttry {\n
\t\t\tsessionStorage.setItem(x, x);\n
\t\t\tsessionStorage.removeItem(x);\n
\t\t\treturn true;\n
\t\t} catch(e) {\n
\t\t\treturn false;\n
\t\t}\n
\t}())\n
};\n
\n
var\ttestId = 0,\n
\ttoString = Object.prototype.toString,\n
\thasOwn = Object.prototype.hasOwnProperty;\n
\n
var Test = function(name, testName, expected, async, callback) {\n
\tthis.name = name;\n
\tthis.testName = testName;\n
\tthis.expected = expected;\n
\tthis.async = async;\n
\tthis.callback = callback;\n
\tthis.assertions = [];\n
};\n
Test.prototype = {\n
\tinit: function() {\n
\t\tvar tests = id("qunit-tests");\n
\t\tif (tests) {\n
\t\t\tvar b = document.createElement("strong");\n
\t\t\t\tb.innerHTML = "Running " + this.name;\n
\t\t\tvar li = document.createElement("li");\n
\t\t\t\tli.appendChild( b );\n
\t\t\t\tli.className = "running";\n
\t\t\t\tli.id = this.id = "test-output" + testId++;\n
\t\t\ttests.appendChild( li );\n
\t\t}\n
\t},\n
\tsetup: function() {\n
\t\tif (this.module != config.previousModule) {\n
\t\t\tif ( config.previousModule ) {\n
\t\t\t\trunLoggingCallbacks(\'moduleDone\', QUnit, {\n
\t\t\t\t\tname: config.previousModule,\n
\t\t\t\t\tfailed: config.moduleStats.bad,\n
\t\t\t\t\tpassed: config.moduleStats.all - config.moduleStats.bad,\n
\t\t\t\t\ttotal: config.moduleStats.all\n
\t\t\t\t} );\n
\t\t\t}\n
\t\t\tconfig.previousModule = this.module;\n
\t\t\tconfig.moduleStats = { all: 0, bad: 0 };\n
\t\t\trunLoggingCallbacks( \'moduleStart\', QUnit, {\n
\t\t\t\tname: this.module\n
\t\t\t} );\n
\t\t} else if (config.autorun) {\n
\t\t\trunLoggingCallbacks( \'moduleStart\', QUnit, {\n
\t\t\t\tname: this.module\n
\t\t\t} );\n
\t\t}\n
\n
\t\tconfig.current = this;\n
\t\tthis.testEnvironment = extend({\n
\t\t\tsetup: function() {},\n
\t\t\tteardown: function() {}\n
\t\t}, this.moduleTestEnvironment);\n
\n
\t\trunLoggingCallbacks( \'testStart\', QUnit, {\n
\t\t\tname: this.testName,\n
\t\t\tmodule: this.module\n
\t\t});\n
\n
\t\t// allow utility functions to access the current test environment\n
\t\t// TODO why??\n
\t\tQUnit.current_testEnvironment = this.testEnvironment;\n
\n
\t\tif ( !config.pollution ) {\n
\t\t\tsaveGlobal();\n
\t\t}\n
\t\tif ( config.notrycatch ) {\n
\t\t\tthis.testEnvironment.setup.call(this.testEnvironment);\n
\t\t\treturn;\n
\t\t}\n
\t\ttry {\n
\t\t\tthis.testEnvironment.setup.call(this.testEnvironment);\n
\t\t} catch(e) {\n
\t\t\tQUnit.pushFailure( "Setup failed on " + this.testName + ": " + e.message, extractStacktrace( e, 1 ) );\n
\t\t}\n
\t},\n
\trun: function() {\n
\t\tconfig.current = this;\n
\n
\t\tvar running = id("qunit-testresult");\n
\n
\t\tif ( running ) {\n
\t\t\trunning.innerHTML = "Running: <br/>" + this.name;\n
\t\t}\n
\n
\t\tif ( this.async ) {\n
\t\t\tQUnit.stop();\n
\t\t}\n
\n
\t\tif ( config.notrycatch ) {\n
\t\t\tthis.callback.call(this.testEnvironment);\n
\t\t\treturn;\n
\t\t}\n
\t\ttry {\n
\t\t\tthis.callback.call(this.testEnvironment);\n
\t\t} catch(e) {\n
\t\t\tQUnit.pushFailure( "Died on test #" + (this.assertions.length + 1) + ": " + e.message, extractStacktrace( e, 1 ) );\n
\t\t\t// else next test will carry the responsibility\n
\t\t\tsaveGlobal();\n
\n
\t\t\t// Restart the tests if they\'re blocking\n
\t\t\tif ( config.blocking ) {\n
\t\t\t\tQUnit.start();\n
\t\t\t}\n
\t\t}\n
\t},\n
\tteardown: function() {\n
\t\tconfig.current = this;\n
\t\tif ( config.notrycatch ) {\n
\t\t\tthis.testEnvironment.teardown.call(this.testEnvironment);\n
\t\t\treturn;\n
\t\t} else {\n
\t\t\ttry {\n
\t\t\t\tthis.testEnvironment.teardown.call(this.testEnvironment);\n
\t\t\t} catch(e) {\n
\t\t\t\tQUnit.pushFailure( "Teardown failed on " + this.testName + ": " + e.message, extractStacktrace( e, 1 ) );\n
\t\t\t}\n
\t\t}\n
\t\tcheckPollution();\n
\t},\n
\tfinish: function() {\n
\t\tconfig.current = this;\n
\t\tif ( this.expected != null && this.expected != this.assertions.length ) {\n
\t\t\tQUnit.pushFailure( "Expected " + this.expected + " assertions, but " + this.assertions.length + " were run" );\n
\t\t} else if ( this.expected == null && !this.assertions.length ) {\n
\t\t\tQUnit.pushFailure( "Expected at least one assertion, but none were run - call expect(0) to accept zero assertions." );\n
\t\t}\n
\n
\t\tvar good = 0, bad = 0,\n
\t\t\tli, i,\n
\t\t\ttests = id("qunit-tests");\n
\n
\t\tconfig.stats.all += this.assertions.length;\n
\t\tconfig.moduleStats.all += this.assertions.length;\n
\n
\t\tif ( tests ) {\n
\t\t\tvar ol = document.createElement("ol");\n
\n
\t\t\tfor ( i = 0; i < this.assertions.length; i++ ) {\n
\t\t\t\tvar assertion = this.assertions[i];\n
\n
\t\t\t\tli = document.createElement("li");\n
\t\t\t\tli.className = assertion.result ? "pass" : "fail";\n
\t\t\t\tli.innerHTML = assertion.message || (assertion.result ? "okay" : "failed");\n
\t\t\t\tol.appendChild( li );\n
\n
\t\t\t\tif ( assertion.result ) {\n
\t\t\t\t\tgood++;\n
\t\t\t\t} else {\n
\t\t\t\t\tbad++;\n
\t\t\t\t\tconfig.stats.bad++;\n
\t\t\t\t\tconfig.moduleStats.bad++;\n
\t\t\t\t}\n
\t\t\t}\n
\n
\t\t\t// store result when possible\n
\t\t\tif ( QUnit.config.reorder && defined.sessionStorage ) {\n
\t\t\t\tif (bad) {\n
\t\t\t\t\tsessionStorage.setItem("qunit-test-" + this.module + "-" + this.testName, bad);\n
\t\t\t\t} else {\n
\t\t\t\t\tsessionStorage.removeItem("qunit-test-" + this.module + "-" + this.testName);\n
\t\t\t\t}\n
\t\t\t}\n
\n
\t\t\tif (bad === 0) {\n
\t\t\t\tol.style.display = "none";\n
\t\t\t}\n
\n
\t\t\tvar b = document.createElement("strong");\n
\t\t\tb.innerHTML = this.name + " <b class=\'counts\'>(<b class=\'failed\'>" + bad + "</b>, <b class=\'passed\'>" + good + "</b>, " + this.assertions.length + ")</b>";\n
\n
\t\t\tvar a = document.createElement("a");\n
\t\t\ta.innerHTML = "Rerun";\n
\t\t\ta.href = QUnit.url({ filter: getText([b]).replace(/\\([^)]+\\)$/, "").replace(/(^\\s*|\\s*$)/g, "") });\n
\n
\t\t\taddEvent(b, "click", function() {\n
\t\t\t\tvar next = b.nextSibling.nextSibling,\n
\t\t\t\t\tdisplay = next.style.display;\n
\t\t\t\tnext.style.display = display === "none" ? "block" : "none";\n
\t\t\t});\n
\n
\t\t\taddEvent(b, "dblclick", function(e) {\n
\t\t\t\tvar target = e && e.target ? e.target : window.event.srcElement;\n
\t\t\t\tif ( target.nodeName.toLowerCase() == "span" || target.nodeName.toLowerCase() == "b" ) {\n
\t\t\t\t\ttarget = target.parentNode;\n
\t\t\t\t}\n
\t\t\t\tif ( window.location && target.nodeName.toLowerCase() === "strong" ) {\n
\t\t\t\t\twindow.location = QUnit.url({ filter: getText([target]).replace(/\\([^)]+\\)$/, "").replace(/(^\\s*|\\s*$)/g, "") });\n
\t\t\t\t}\n
\t\t\t});\n
\n
\t\t\tli = id(this.id);\n
\t\t\tli.className = bad ? "fail" : "pass";\n
\t\t\tli.removeChild( li.firstChild );\n
\t\t\tli.appendChild( b );\n
\t\t\tli.appendChild( a );\n
\t\t\tli.appendChild( ol );\n
\n
\t\t} else {\n
\t\t\tfor ( i = 0; i < this.assertions.length; i++ ) {\n
\t\t\t\tif ( !this.assertions[i].result ) {\n
\t\t\t\t\tbad++;\n
\t\t\t\t\tconfig.stats.bad++;\n
\t\t\t\t\tconfig.moduleStats.bad++;\n
\t\t\t\t}\n
\t\t\t}\n
\t\t}\n
\n
\t\tQUnit.reset();\n
\n
\t\trunLoggingCallbacks( \'testDone\', QUnit, {\n
\t\t\tname: this.testName,\n
\t\t\tmodule: this.module,\n
\t\t\tfailed: bad,\n
\t\t\tpassed: this.assertions.length - bad,\n
\t\t\ttotal: this.assertions.length\n
\t\t} );\n
\t},\n
\n
\tqueue: function() {\n
\t\tvar test = this;\n
\t\tsynchronize(function() {\n
\t\t\ttest.init();\n
\t\t});\n
\t\tfunction run() {\n
\t\t\t// each of these can by async\n
\t\t\tsynchronize(function() {\n
\t\t\t\ttest.setup();\n
\t\t\t});\n
\t\t\tsynchronize(function() {\n
\t\t\t\ttest.run();\n
\t\t\t});\n
\t\t\tsynchronize(function() {\n
\t\t\t\ttest.teardown();\n
\t\t\t});\n
\t\t\tsynchronize(function() {\n
\t\t\t\ttest.finish();\n
\t\t\t});\n
\t\t}\n
\t\t// defer when previous test run passed, if storage is available\n
\t\tvar bad = QUnit.config.reorder && defined.sessionStorage && +sessionStorage.getItem("qunit-test-" + this.module + "-" + this.testName);\n
\t\tif (bad) {\n
\t\t\trun();\n
\t\t} else {\n
\t\t\tsynchronize(run, true);\n
\t\t}\n
\t}\n
\n
};\n
\n
var QUnit = {\n
\n
\t// call on start of module test to prepend name to all tests\n
\tmodule: function(name, testEnvironment) {\n
\t\tconfig.currentModule = name;\n
\t\tconfig.currentModuleTestEnviroment = testEnvironment;\n
\t},\n
\n
\tasyncTest: function(testName, expected, callback) {\n
\t\tif ( arguments.length === 2 ) {\n
\t\t\tcallback = expected;\n
\t\t\texpected = null;\n
\t\t}\n
\n
\t\tQUnit.test(testName, expected, callback, true);\n
\t},\n
\n
\ttest: function(testName, expected, callback, async) {\n
\t\tvar name = \'<span class="test-name">\' + escapeInnerText(testName) + \'</span>\';\n
\n
\t\tif ( arguments.length === 2 ) {\n
\t\t\tcallback = expected;\n
\t\t\texpected = null;\n
\t\t}\n
\n
\t\tif ( config.currentModule ) {\n
\t\t\tname = \'<span class="module-name">\' + config.currentModule + "</span>: " + name;\n
\t\t}\n
\n
\t\tif ( !validTest(config.currentModule + ": " + testName) ) {\n
\t\t\treturn;\n
\t\t}\n
\n
\t\tvar test = new Test(name, testName, expected, async, callback);\n
\t\ttest.module = config.currentModule;\n
\t\ttest.moduleTestEnvironment = config.currentModuleTestEnviroment;\n
\t\ttest.queue();\n
\t},\n
\n
\t// Specify the number of expected assertions to gurantee that failed test (no assertions are run at all) don\'t slip through.\n
\texpect: function(asserts) {\n
\t\tconfig.current.expected = asserts;\n
\t},\n
\n
\t// Asserts true.\n
\t// @example ok( "asdfasdf".length > 5, "There must be at least 5 chars" );\n
\tok: function(result, msg) {\n
\t\tif (!config.current) {\n
\t\t\tthrow new Error("ok() assertion outside test context, was " + sourceFromStacktrace(2));\n
\t\t}\n
\t\tresult = !!result;\n
\t\tvar details = {\n
\t\t\tresult: result,\n
\t\t\tmessage: msg\n
\t\t};\n
\t\tmsg = escapeInnerText(msg || (result ? "okay" : "failed"));\n
\t\tif ( !result ) {\n
\t\t\tvar source = sourceFromStacktrace(2);\n
\t\t\tif (source) {\n
\t\t\t\tdetails.source = source;\n
\t\t\t\tmsg += \'<table><tr class="test-source"><th>Source: </th><td><pre>\' + escapeInnerText(source) + \'</pre></td></tr></table>\';\n
\t\t\t}\n
\t\t}\n
\t\trunLoggingCallbacks( \'log\', QUnit, details );\n
\t\tconfig.current.assertions.push({\n
\t\t\tresult: result,\n
\t\t\tmessage: msg\n
\t\t});\n
\t},\n
\n
\t// Checks that the first two arguments are equal, with an optional message. Prints out both actual and expected values.\n
\t// @example equal( format("Received {0} bytes.", 2), "Received 2 bytes." );\n
\tequal: function(actual, expected, message) {\n
\t\tQUnit.push(expected == actual, actual, expected, message);\n
\t},\n
\n
\tnotEqual: function(actual, expected, message) {\n
\t\tQUnit.push(expected != actual, actual, expected, message);\n
\t},\n
\n
\tdeepEqual: function(actual, expected, message) {\n
\t\tQUnit.push(QUnit.equiv(actual, expected), actual, expected, message);\n
\t},\n
\n
\tnotDeepEqual: function(actual, expected, message) {\n
\t\tQUnit.push(!QUnit.equiv(actual, expected), actual, expected, message);\n
\t},\n
\n
\tstrictEqual: function(actual, expected, message) {\n
\t\tQUnit.push(expected === actual, actual, expected, message);\n
\t},\n
\n
\tnotStrictEqual: function(actual, expected, message) {\n
\t\tQUnit.push(expected !== actual, actual, expected, message);\n
\t},\n
\n
\traises: function(block, expected, message) {\n
\t\tvar actual, ok = false;\n
\n
\t\tif (typeof expected === \'string\') {\n
\t\t\tmessage = expected;\n
\t\t\texpected = null;\n
\t\t}\n
\n
\t\ttry {\n
\t\t\tblock.call(config.current.testEnvironment);\n
\t\t} catch (e) {\n
\t\t\tactual = e;\n
\t\t}\n
\n
\t\tif (actual) {\n
\t\t\t// we don\'t want to validate thrown error\n
\t\t\tif (!expected) {\n
\t\t\t\tok = true;\n
\t\t\t// expected is a regexp\n
\t\t\t} else if (QUnit.objectType(expected) === "regexp") {\n
\t\t\t\tok = expected.test(actual);\n
\t\t\t// expected is a constructor\n
\t\t\t} else if (actual instanceof expected) {\n
\t\t\t\tok = true;\n
\t\t\t// expected is a validation function which returns true is validation passed\n
\t\t\t} else if (expected.call({}, actual) === true) {\n
\t\t\t\tok = true;\n
\t\t\t}\n
\t\t}\n
\n
\t\tQUnit.ok(ok, message);\n
\t},\n
\n
\tstart: function(count) {\n
\t\tconfig.semaphore -= count || 1;\n
\t\tif (config.semaphore > 0) {\n
\t\t\t// don\'t start until equal number of stop-calls\n
\t\t\treturn;\n
\t\t}\n
\t\tif (config.semaphore < 0) {\n
\t\t\t// ignore if start is called more often then stop\n
\t\t\tconfig.semaphore = 0;\n
\t\t}\n
\t\t// A slight delay, to avoid any current callbacks\n
\t\tif ( defined.setTimeout ) {\n
\t\t\twindow.setTimeout(function() {\n
\t\t\t\tif (config.semaphore > 0) {\n
\t\t\t\t\treturn;\n
\t\t\t\t}\n
\t\t\t\tif ( config.timeout ) {\n
\t\t\t\t\tclearTimeout(config.timeout);\n
\t\t\t\t}\n
\n
\t\t\t\tconfig.blocking = false;\n
\t\t\t\tprocess(true);\n
\t\t\t}, 13);\n
\t\t} else {\n
\t\t\tconfig.blocking = false;\n
\t\t\tprocess(true);\n
\t\t}\n
\t},\n
\n
\tstop: function(count) {\n
\t\tconfig.semaphore += count || 1;\n
\t\tconfig.blocking = true;\n
\n
\t\tif ( config.testTimeout && defined.setTimeout ) {\n
\t\t\tclearTimeout(config.timeout);\n
\t\t\tconfig.timeout = window.setTimeout(function() {\n
\t\t\t\tQUnit.ok( false, "Test timed out" );\n
\t\t\t\tconfig.semaphore = 1;\n
\t\t\t\tQUnit.start();\n
\t\t\t}, config.testTimeout);\n
\t\t}\n
\t}\n
};\n
\n
//We want access to the constructor\'s prototype\n
(function() {\n
\tfunction F(){}\n
\tF.prototype = QUnit;\n
\tQUnit = new F();\n
\t//Make F QUnit\'s constructor so that we can add to the prototype later\n
\tQUnit.constructor = F;\n
}());\n
\n
// deprecated; still export them to window to provide clear error messages\n
// next step: remove entirely\n
QUnit.equals = function() {\n
\tQUnit.push(false, false, false, "QUnit.equals has been deprecated since 2009 (e88049a0), use QUnit.equal instead");\n
};\n
QUnit.same = function() {\n
\tQUnit.push(false, false, false, "QUnit.same has been deprecated since 2009 (e88049a0), use QUnit.deepEqual instead");\n
};\n
\n
// Maintain internal state\n
var config = {\n
\t// The queue of tests to run\n
\tqueue: [],\n
\n
\t// block until document ready\n
\tblocking: true,\n
\n
\t// when enabled, show only failing tests\n
\t// gets persisted through sessionStorage and can be changed in UI via checkbox\n
\thidepassed: false,\n
\n
\t// by default, run previously failed tests first\n
\t// very useful in combination with "Hide passed tests" checked\n
\treorder: true,\n
\n
\t// by default, modify document.title when suite is done\n
\taltertitle: true,\n
\n
\turlConfig: [\'noglobals\', \'notrycatch\'],\n
\n
\t//logging callback queues\n
\tbegin: [],\n
\tdone: [],\n
\tlog: [],\n
\ttestStart: [],\n
\ttestDone: [],\n
\tmoduleStart: [],\n
\tmoduleDone: []\n
};\n
\n
// Load paramaters\n
(function() {\n
\tvar location = window.location || { search: "", protocol: "file:" },\n
\t\tparams = location.search.slice( 1 ).split( "&" ),\n
\t\tlength = params.length,\n
\t\turlParams = {},\n
\t\tcurrent;\n
\n
\tif ( params[ 0 ] ) {\n
\t\tfor ( var i = 0; i < length; i++ ) {\n
\t\t\tcurrent = params[ i ].split( "=" );\n
\t\t\tcurrent[ 0 ] = decodeURIComponent( current[ 0 ] );\n
\t\t\t// allow just a key to turn on a flag, e.g., test.html?noglobals\n
\t\t\tcurrent[ 1 ] = current[ 1 ] ? decodeURIComponent( current[ 1 ] ) : true;\n
\t\t\turlParams[ current[ 0 ] ] = current[ 1 ];\n
\t\t}\n
\t}\n
\n
\tQUnit.urlParams = urlParams;\n
\tconfig.filter = urlParams.filter;\n
\n
\t// Figure out if we\'re running the tests from a server or not\n
\tQUnit.isLocal = location.protocol === \'file:\';\n
}());\n
\n
// Expose the API as global variables, unless an \'exports\'\n
// object exists, in that case we assume we\'re in CommonJS - export everything at the end\n
if ( typeof exports === "undefined" || typeof require === "undefined" ) {\n
\textend(window, QUnit);\n
\twindow.QUnit = QUnit;\n
}\n
\n
// define these after exposing globals to keep them in these QUnit namespace only\n
extend(QUnit, {\n
\tconfig: config,\n
\n
\t// Initialize the configuration options\n
\tinit: function() {\n
\t\textend(config, {\n
\t\t\tstats: { all: 0, bad: 0 },\n
\t\t\tmoduleStats: { all: 0, bad: 0 },\n
\t\t\tstarted: +new Date(),\n
\t\t\tupdateRate: 1000,\n
\t\t\tblocking: false,\n
\t\t\tautostart: true,\n
\t\t\tautorun: false,\n
\t\t\tfilter: "",\n
\t\t\tqueue: [],\n
\t\t\tsemaphore: 0\n
\t\t});\n
\n
\t\tvar qunit = id( "qunit" );\n
\t\tif ( qunit ) {\n
\t\t\tqunit.innerHTML =\n
\t\t\t\t\'<h1 id="qunit-header">\' + escapeInnerText( document.title ) + \'</h1>\' +\n
\t\t\t\t\'<h2 id="qunit-banner"></h2>\' +\n
\t\t\t\t\'<div id="qunit-testrunner-toolbar"></div>\' +\n
\t\t\t\t\'<h2 id="qunit-userAgent"></h2>\' +\n
\t\t\t\t\'<ol id="qunit-tests"></ol>\';\n
\t\t}\n
\n
\t\tvar tests = id( "qunit-tests" ),\n
\t\t\tbanner = id( "qunit-banner" ),\n
\t\t\tresult = id( "qunit-testresult" );\n
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
\n
\t\tif ( tests ) {\n
\t\t\tresult = document.createElement( "p" );\n
\t\t\tresult.id = "qunit-testresult";\n
\t\t\tresult.className = "result";\n
\t\t\ttests.parentNode.insertBefore( result, tests );\n
\t\t\tresult.innerHTML = \'Running...<br/>&nbsp;\';\n
\t\t}\n
\t},\n
\n
\t// Resets the test setup. Useful for tests that modify the DOM.\n
\t// If jQuery is available, uses jQuery\'s html(), otherwise just innerHTML.\n
\treset: function() {\n
\t\tif ( window.jQuery ) {\n
\t\t\tjQuery( "#qunit-fixture" ).html( config.fixture );\n
\t\t} else {\n
\t\t\tvar main = id( \'qunit-fixture\' );\n
\t\t\tif ( main ) {\n
\t\t\t\tmain.innerHTML = config.fixture;\n
\t\t\t}\n
\t\t}\n
\t},\n
\n
\t// Trigger an event on an element.\n
\t// @example triggerEvent( document.body, "click" );\n
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
\n
\t// Safe object type checking\n
\tis: function( type, obj ) {\n
\t\treturn QUnit.objectType( obj ) == type;\n
\t},\n
\n
\tobjectType: function( obj ) {\n
\t\tif (typeof obj === "undefined") {\n
\t\t\t\treturn "undefined";\n
\n
\t\t// consider: typeof null === object\n
\t\t}\n
\t\tif (obj === null) {\n
\t\t\t\treturn "null";\n
\t\t}\n
\n
\t\tvar type = toString.call( obj ).match(/^\\[object\\s(.*)\\]$/)[1] || \'\';\n
\n
\t\tswitch (type) {\n
\t\t\tcase \'Number\':\n
\t\t\t\tif (isNaN(obj)) {\n
\t\t\t\t\treturn "nan";\n
\t\t\t\t}\n
\t\t\t\treturn "number";\n
\t\t\tcase \'String\':\n
\t\t\tcase \'Boolean\':\n
\t\t\tcase \'Array\':\n
\t\t\tcase \'Date\':\n
\t\t\tcase \'RegExp\':\n
\t\t\tcase \'Function\':\n
\t\t\t\t\treturn type.toLowerCase();\n
\t\t}\n
\t\tif (typeof obj === "object") {\n
\t\t\t\treturn "object";\n
\t\t}\n
\t\treturn undefined;\n
\t},\n
\n
\tpush: function(result, actual, expected, message) {\n
\t\tif (!config.current) {\n
\t\t\tthrow new Error("assertion outside test context, was " + sourceFromStacktrace());\n
\t\t}\n
\t\tvar details = {\n
\t\t\tresult: result,\n
\t\t\tmessage: message,\n
\t\t\tactual: actual,\n
\t\t\texpected: expected\n
\t\t};\n
\n
\t\tmessage = escapeInnerText(message) || (result ? "okay" : "failed");\n
\t\tmessage = \'<span class="test-message">\' + message + "</span>";\n
\t\tvar output = message;\n
\t\tif (!result) {\n
\t\t\texpected = escapeInnerText(QUnit.jsDump.parse(expected));\n
\t\t\tactual = escapeInnerText(QUnit.jsDump.parse(actual));\n
\t\t\toutput += \'<table><tr class="test-expected"><th>Expected: </th><td><pre>\' + expected + \'</pre></td></tr>\';\n
\t\t\tif (actual != expected) {\n
\t\t\t\toutput += \'<tr class="test-actual"><th>Result: </th><td><pre>\' + actual + \'</pre></td></tr>\';\n
\t\t\t\toutput += \'<tr class="test-diff"><th>Diff: </th><td><pre>\' + QUnit.diff(expected, actual) +\'</pre></td></tr>\';\n
\t\t\t}\n
\t\t\tvar source = sourceFromStacktrace();\n
\t\t\tif (source) {\n
\t\t\t\tdetails.source = source;\n
\t\t\t\toutput += \'<tr class="test-source"><th>Source: </th><td><pre>\' + escapeInnerText(source) + \'</pre></td></tr>\';\n
\t\t\t}\n
\t\t\toutput += "</table>";\n
\t\t}\n
\n
\t\trunLoggingCallbacks( \'log\', QUnit, details );\n
\n
\t\tconfig.current.assertions.push({\n
\t\t\tresult: !!result,\n
\t\t\tmessage: output\n
\t\t});\n
\t},\n
\n
\tpushFailure: function(message, source) {\n
\t\tvar details = {\n
\t\t\tresult: false,\n
\t\t\tmessage: message\n
\t\t};\n
\t\tvar output = escapeInnerText(message);\n
\t\tif (source) {\n
\t\t\tdetails.source = source;\n
\t\t\toutput += \'<table><tr class="test-source"><th>Source: </th><td><pre>\' + escapeInnerText(source) + \'</pre></td></tr></table>\';\n
\t\t}\n
\t\trunLoggingCallbacks( \'log\', QUnit, details );\n
\t\tconfig.current.assertions.push({\n
\t\t\tresult: false,\n
\t\t\tmessage: output\n
\t\t});\n
\t},\n
\n
\turl: function( params ) {\n
\t\tparams = extend( extend( {}, QUnit.urlParams ), params );\n
\t\tvar querystring = "?",\n
\t\t\tkey;\n
\t\tfor ( key in params ) {\n
\t\t\tif ( !hasOwn.call( params, key ) ) {\n
\t\t\t\tcontinue;\n
\t\t\t}\n
\t\t\tquerystring += encodeURIComponent( key ) + "=" +\n
\t\t\t\tencodeURIComponent( params[ key ] ) + "&";\n
\t\t}\n
\t\treturn window.location.pathname + querystring.slice( 0, -1 );\n
\t},\n
\n
\textend: extend,\n
\tid: id,\n
\taddEvent: addEvent\n
});\n
\n
//QUnit.constructor is set to the empty F() above so that we can add to it\'s prototype later\n
//Doing this allows us to tell if the following methods have been overwritten on the actual\n
//QUnit object, which is a deprecated way of using the callbacks.\n
extend(QUnit.constructor.prototype, {\n
\t// Logging callbacks; all receive a single argument with the listed properties\n
\t// run test/logs.html for any related changes\n
\tbegin: registerLoggingCallback(\'begin\'),\n
\t// done: { failed, passed, total, runtime }\n
\tdone: registerLoggingCallback(\'done\'),\n
\t// log: { result, actual, expected, message }\n
\tlog: registerLoggingCallback(\'log\'),\n
\t// testStart: { name }\n
\ttestStart: registerLoggingCallback(\'testStart\'),\n
\t// testDone: { name, failed, passed, total }\n
\ttestDone: registerLoggingCallback(\'testDone\'),\n
\t// moduleStart: { name }\n
\tmoduleStart: registerLoggingCallback(\'moduleStart\'),\n
\t// moduleDone: { name, failed, passed, total }\n
\tmoduleDone: registerLoggingCallback(\'moduleDone\')\n
});\n
\n
if ( typeof document === "undefined" || document.readyState === "complete" ) {\n
\tconfig.autorun = true;\n
}\n
\n
QUnit.load = function() {\n
\trunLoggingCallbacks( \'begin\', QUnit, {} );\n
\n
\t// Initialize the config, saving the execution queue\n
\tvar oldconfig = extend({}, config);\n
\tQUnit.init();\n
\textend(config, oldconfig);\n
\n
\tconfig.blocking = false;\n
\n
\tvar urlConfigHtml = \'\', len = config.urlConfig.length;\n
\tfor ( var i = 0, val; i < len; i++ ) {\n
\t\tval = config.urlConfig[i];\n
\t\tconfig[val] = QUnit.urlParams[val];\n
\t\turlConfigHtml += \'<label><input name="\' + val + \'" type="checkbox"\' + ( config[val] ? \' checked="checked"\' : \'\' ) + \'>\' + val + \'</label>\';\n
\t}\n
\n
\tvar userAgent = id("qunit-userAgent");\n
\tif ( userAgent ) {\n
\t\tuserAgent.innerHTML = navigator.userAgent;\n
\t}\n
\tvar banner = id("qunit-header");\n
\tif ( banner ) {\n
\t\tbanner.innerHTML = \'<a href="\' + QUnit.url({ filter: undefined }) + \'"> \' + banner.innerHTML + \'</a> \' + urlConfigHtml;\n
\t\taddEvent( banner, "change", function( event ) {\n
\t\t\tvar params = {};\n
\t\t\tparams[ event.target.name ] = event.target.checked ? true : undefined;\n
\t\t\twindow.location = QUnit.url( params );\n
\t\t});\n
\t}\n
\n
\tvar toolbar = id("qunit-testrunner-toolbar");\n
\tif ( toolbar ) {\n
\t\tvar filter = document.createElement("input");\n
\t\tfilter.type = "checkbox";\n
\t\tfilter.id = "qunit-filter-pass";\n
\t\taddEvent( filter, "click", function() {\n
\t\t\tvar ol = document.getElementById("qunit-tests");\n
\t\t\tif ( filter.checked ) {\n
\t\t\t\tol.className = ol.className + " hidepass";\n
\t\t\t} else {\n
\t\t\t\tvar tmp = " " + ol.className.replace( /[\\n\\t\\r]/g, " " ) + " ";\n
\t\t\t\tol.className = tmp.replace(/ hidepass /, " ");\n
\t\t\t}\n
\t\t\tif ( defined.sessionStorage ) {\n
\t\t\t\tif (filter.checked) {\n
\t\t\t\t\tsessionStorage.setItem("qunit-filter-passed-tests", "true");\n
\t\t\t\t} else {\n
\t\t\t\t\tsessionStorage.removeItem("qunit-filter-passed-tests");\n
\t\t\t\t}\n
\t\t\t}\n
\t\t});\n
\t\tif ( config.hidepassed || defined.sessionStorage && sessionStorage.getItem("qunit-filter-passed-tests") ) {\n
\t\t\tfilter.checked = true;\n
\t\t\tvar ol = document.getElementById("qunit-tests");\n
\t\t\tol.className = ol.className + " hidepass";\n
\t\t}\n
\t\ttoolbar.appendChild( filter );\n
\n
\t\tvar label = document.createElement("label");\n
\t\tlabel.setAttribute("for", "qunit-filter-pass");\n
\t\tlabel.innerHTML = "Hide passed tests";\n
\t\ttoolbar.appendChild( label );\n
\t}\n
\n
\tvar main = id(\'qunit-fixture\');\n
\tif ( main ) {\n
\t\tconfig.fixture = main.innerHTML;\n
\t}\n
\n
\tif (config.autostart) {\n
\t\tQUnit.start();\n
\t}\n
};\n
\n
addEvent(window, "load", QUnit.load);\n
\n
// addEvent(window, "error") gives us a useless event object\n
window.onerror = function( message, file, line ) {\n
\tif ( QUnit.config.current ) {\n
\t\tQUnit.pushFailure( message, file + ":" + line );\n
\t} else {\n
\t\tQUnit.test( "global failure", function() {\n
\t\t\tQUnit.pushFailure( message, file + ":" + line );\n
\t\t});\n
\t}\n
};\n
\n
function done() {\n
\tconfig.autorun = true;\n
\n
\t// Log the last module results\n
\tif ( config.currentModule ) {\n
\t\trunLoggingCallbacks( \'moduleDone\', QUnit, {\n
\t\t\tname: config.currentModule,\n
\t\t\tfailed: config.moduleStats.bad,\n
\t\t\tpassed: config.moduleStats.all - config.moduleStats.bad,\n
\t\t\ttotal: config.moduleStats.all\n
\t\t} );\n
\t}\n
\n
\tvar banner = id("qunit-banner"),\n
\t\ttests = id("qunit-tests"),\n
\t\truntime = +new Date() - config.started,\n
\t\tpassed = config.stats.all - config.stats.bad,\n
\t\thtml = [\n
\t\t\t\'Tests completed in \',\n
\t\t\truntime,\n
\t\t\t\' milliseconds.<br/>\',\n
\t\t\t\'<span class="passed">\',\n
\t\t\tpassed,\n
\t\t\t\'</span> tests of <span class="total">\',\n
\t\t\tconfig.stats.all,\n
\t\t\t\'</span> passed, <span class="failed">\',\n
\t\t\tconfig.stats.bad,\n
\t\t\t\'</span> failed.\'\n
\t\t].join(\'\');\n
\n
\tif ( banner ) {\n
\t\tbanner.className = (config.stats.bad ? "qunit-fail" : "qunit-pass");\n
\t}\n
\n
\tif ( tests ) {\n
\t\tid( "qunit-testresult" ).innerHTML = html;\n
\t}\n
\n
\tif ( config.altertitle && typeof document !== "undefined" && document.title ) {\n
\t\t// show ✖ for good, ✔ for bad suite result in title\n
\t\t// use escape sequences in case file gets loaded with non-utf-8-charset\n
\t\tdocument.title = [\n
\t\t\t(config.stats.bad ? "\\u2716" : "\\u2714"),\n
\t\t\tdocument.title.replace(/^[\\u2714\\u2716] /i, "")\n
\t\t].join(" ");\n
\t}\n
\n
\t// clear own sessionStorage items if all tests passed\n
\tif ( config.reorder && defined.sessionStorage && config.stats.bad === 0 ) {\n
\t\tvar key;\n
\t\tfor ( var i = 0; i < sessionStorage.length; i++ ) {\n
\t\t\tkey = sessionStorage.key( i++ );\n
\t\t\tif ( key.indexOf("qunit-test-") === 0 ) {\n
\t\t\t\tsessionStorage.removeItem( key );\n
\t\t\t}\n
\t\t}\n
\t}\n
\n
\trunLoggingCallbacks( \'done\', QUnit, {\n
\t\tfailed: config.stats.bad,\n
\t\tpassed: passed,\n
\t\ttotal: config.stats.all,\n
\t\truntime: runtime\n
\t} );\n
}\n
\n
function validTest( name ) {\n
\tvar filter = config.filter,\n
\t\trun = false;\n
\n
\tif ( !filter ) {\n
\t\treturn true;\n
\t}\n
\n
\tvar not = filter.charAt( 0 ) === "!";\n
\tif ( not ) {\n
\t\tfilter = filter.slice( 1 );\n
\t}\n
\n
\tif ( name.indexOf( filter ) !== -1 ) {\n
\t\treturn !not;\n
\t}\n
\n
\tif ( not ) {\n
\t\trun = true;\n
\t}\n
\n
\treturn run;\n
}\n
\n
// so far supports only Firefox, Chrome and Opera (buggy), Safari (for real exceptions)\n
// Later Safari and IE10 are supposed to support error.stack as well\n
// See also https://developer.mozilla.org/en/JavaScript/Reference/Global_Objects/Error/Stack\n
function extractStacktrace( e, offset ) {\n
\toffset = offset || 3;\n
\tif (e.stacktrace) {\n
\t\t// Opera\n
\t\treturn e.stacktrace.split("\\n")[offset + 3];\n
\t} else if (e.stack) {\n
\t\t// Firefox, Chrome\n
\t\tvar stack = e.stack.split("\\n");\n
\t\tif (/^error$/i.test(stack[0])) {\n
\t\t\tstack.shift();\n
\t\t}\n
\t\treturn stack[offset];\n
\t} else if (e.sourceURL) {\n
\t\t// Safari, PhantomJS\n
\t\t// hopefully one day Safari provides actual stacktraces\n
\t\t// exclude useless self-reference for generated Error objects\n
\t\tif ( /qunit.js$/.test( e.sourceURL ) ) {\n
\t\t\treturn;\n
\t\t}\n
\t\t// for actual exceptions, this is useful\n
\t\treturn e.sourceURL + ":" + e.line;\n
\t}\n
}\n
function sourceFromStacktrace(offset) {\n
\ttry {\n
\t\tthrow new Error();\n
\t} catch ( e ) {\n
\t\treturn extractStacktrace( e, offset );\n
\t}\n
}\n
\n
function escapeInnerText(s) {\n
\tif (!s) {\n
\t\treturn "";\n
\t}\n
\ts = s + "";\n
\treturn s.replace(/[\\&<>]/g, function(s) {\n
\t\tswitch(s) {\n
\t\t\tcase "&": return "&amp;";\n
\t\t\tcase "<": return "&lt;";\n
\t\t\tcase ">": return "&gt;";\n
\t\t\tdefault: return s;\n
\t\t}\n
\t});\n
}\n
\n
function synchronize( callback, last ) {\n
\tconfig.queue.push( callback );\n
\n
\tif ( config.autorun && !config.blocking ) {\n
\t\tprocess(last);\n
\t}\n
}\n
\n
function process( last ) {\n
\tfunction next() {\n
\t\tprocess( last );\n
\t}\n
\tvar start = new Date().getTime();\n
\tconfig.depth = config.depth ? config.depth + 1 : 1;\n
\n
\twhile ( config.queue.length && !config.blocking ) {\n
\t\tif ( !defined.setTimeout || config.updateRate <= 0 || ( ( new Date().getTime() - start ) < config.updateRate ) ) {\n
\t\t\tconfig.queue.shift()();\n
\t\t} else {\n
\t\t\twindow.setTimeout( next, 13 );\n
\t\t\tbreak;\n
\t\t}\n
\t}\n
\tconfig.depth--;\n
\tif ( last && !config.blocking && !config.queue.length && config.depth === 0 ) {\n
\t\tdone();\n
\t}\n
}\n
\n
function saveGlobal() {\n
\tconfig.pollution = [];\n
\n
\tif ( config.noglobals ) {\n
\t\tfor ( var key in window ) {\n
\t\t\tif ( !hasOwn.call( window, key ) ) {\n
\t\t\t\tcontinue;\n
\t\t\t}\n
\t\t\tconfig.pollution.push( key );\n
\t\t}\n
\t}\n
}\n
\n
function checkPollution( name ) {\n
\tvar old = config.pollution;\n
\tsaveGlobal();\n
\n
\tvar newGlobals = diff( config.pollution, old );\n
\tif ( newGlobals.length > 0 ) {\n
\t\tQUnit.pushFailure( "Introduced global variable(s): " + newGlobals.join(", ") );\n
\t}\n
\n
\tvar deletedGlobals = diff( old, config.pollution );\n
\tif ( deletedGlobals.length > 0 ) {\n
\t\tQUnit.pushFailure( "Deleted global variable(s): " + deletedGlobals.join(", ") );\n
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
function extend(a, b) {\n
\tfor ( var prop in b ) {\n
\t\tif ( b[prop] === undefined ) {\n
\t\t\tdelete a[prop];\n
\n
\t\t// Avoid "Member not found" error in IE8 caused by setting window.constructor\n
\t\t} else if ( prop !== "constructor" || a !== window ) {\n
\t\t\ta[prop] = b[prop];\n
\t\t}\n
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
function registerLoggingCallback(key){\n
\treturn function(callback){\n
\t\tconfig[key].push( callback );\n
\t};\n
}\n
\n
// Supports deprecated method of completely overwriting logging callbacks\n
function runLoggingCallbacks(key, scope, args) {\n
\t//debugger;\n
\tvar callbacks;\n
\tif ( QUnit.hasOwnProperty(key) ) {\n
\t\tQUnit[key].call(scope, args);\n
\t} else {\n
\t\tcallbacks = config[key];\n
\t\tfor( var i = 0; i < callbacks.length; i++ ) {\n
\t\t\tcallbacks[i].call( scope, args );\n
\t\t}\n
\t}\n
}\n
\n
// Test for equality any JavaScript type.\n
// Author: Philippe Rathé <prathe@gmail.com>\n
QUnit.equiv = (function() {\n
\n
\tvar innerEquiv; // the real equiv function\n
\tvar callers = []; // stack to decide between skip/abort functions\n
\tvar parents = []; // stack to avoiding loops from circular referencing\n
\n
\t// Call the o related callback with the given arguments.\n
\tfunction bindCallbacks(o, callbacks, args) {\n
\t\tvar prop = QUnit.objectType(o);\n
\t\tif (prop) {\n
\t\t\tif (QUnit.objectType(callbacks[prop]) === "function") {\n
\t\t\t\treturn callbacks[prop].apply(callbacks, args);\n
\t\t\t} else {\n
\t\t\t\treturn callbacks[prop]; // or undefined\n
\t\t\t}\n
\t\t}\n
\t}\n
\n
\tvar getProto = Object.getPrototypeOf || function (obj) {\n
\t\treturn obj.__proto__;\n
\t};\n
\n
\tvar callbacks = (function () {\n
\n
\t\t// for string, boolean, number and null\n
\t\tfunction useStrictEquality(b, a) {\n
\t\t\tif (b instanceof a.constructor || a instanceof b.constructor) {\n
\t\t\t\t// to catch short annotaion VS \'new\' annotation of a\n
\t\t\t\t// declaration\n
\t\t\t\t// e.g. var i = 1;\n
\t\t\t\t// var j = new Number(1);\n
\t\t\t\treturn a == b;\n
\t\t\t} else {\n
\t\t\t\treturn a === b;\n
\t\t\t}\n
\t\t}\n
\n
\t\treturn {\n
\t\t\t"string" : useStrictEquality,\n
\t\t\t"boolean" : useStrictEquality,\n
\t\t\t"number" : useStrictEquality,\n
\t\t\t"null" : useStrictEquality,\n
\t\t\t"undefined" : useStrictEquality,\n
\n
\t\t\t"nan" : function(b) {\n
\t\t\t\treturn isNaN(b);\n
\t\t\t},\n
\n
\t\t\t"date" : function(b, a) {\n
\t\t\t\treturn QUnit.objectType(b) === "date" && a.valueOf() === b.valueOf();\n
\t\t\t},\n
\n
\t\t\t"regexp" : function(b, a) {\n
\t\t\t\treturn QUnit.objectType(b) === "regexp" &&\n
\t\t\t\t\t// the regex itself\n
\t\t\t\t\ta.source === b.source &&\n
\t\t\t\t\t// and its modifers\n
\t\t\t\t\ta.global === b.global &&\n
\t\t\t\t\t// (gmi) ...\n
\t\t\t\t\ta.ignoreCase === b.ignoreCase &&\n
\t\t\t\t\ta.multiline === b.multiline;\n
\t\t\t},\n
\n
\t\t\t// - skip when the property is a method of an instance (OOP)\n
\t\t\t// - abort otherwise,\n
\t\t\t// initial === would have catch identical references anyway\n
\t\t\t"function" : function() {\n
\t\t\t\tvar caller = callers[callers.length - 1];\n
\t\t\t\treturn caller !== Object && typeof caller !== "undefined";\n
\t\t\t},\n
\n
\t\t\t"array" : function(b, a) {\n
\t\t\t\tvar i, j, loop;\n
\t\t\t\tvar len;\n
\n
\t\t\t\t// b could be an object literal here\n
\t\t\t\tif (QUnit.objectType(b) !== "array") {\n
\t\t\t\t\treturn false;\n
\t\t\t\t}\n
\n
\t\t\t\tlen = a.length;\n
\t\t\t\tif (len !== b.length) { // safe and faster\n
\t\t\t\t\treturn false;\n
\t\t\t\t}\n
\n
\t\t\t\t// track reference to avoid circular references\n
\t\t\t\tparents.push(a);\n
\t\t\t\tfor (i = 0; i < len; i++) {\n
\t\t\t\t\tloop = false;\n
\t\t\t\t\tfor (j = 0; j < parents.length; j++) {\n
\t\t\t\t\t\tif (parents[j] === a[i]) {\n
\t\t\t\t\t\t\tloop = true;// dont rewalk array\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\t\t\t\t\tif (!loop && !innerEquiv(a[i], b[i])) {\n
\t\t\t\t\t\tparents.pop();\n
\t\t\t\t\t\treturn false;\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t\tparents.pop();\n
\t\t\t\treturn true;\n
\t\t\t},\n
\n
\t\t\t"object" : function(b, a) {\n
\t\t\t\tvar i, j, loop;\n
\t\t\t\tvar eq = true; // unless we can proove it\n
\t\t\t\tvar aProperties = [], bProperties = []; // collection of\n
\t\t\t\t\t\t\t\t\t\t\t\t\t\t// strings\n
\n
\t\t\t\t// comparing constructors is more strict than using\n
\t\t\t\t// instanceof\n
\t\t\t\tif (a.constructor !== b.constructor) {\n
\t\t\t\t\t// Allow objects with no prototype to be equivalent to\n
\t\t\t\t\t// objects with Object as their constructor.\n
\t\t\t\t\tif (!((getProto(a) === null && getProto(b) === Object.prototype) ||\n
\t\t\t\t\t\t(getProto(b) === null && getProto(a) === Object.prototype)))\n
\t\t\t\t\t{\n
\t\t\t\t\t\treturn false;\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\n
\t\t\t\t// stack constructor before traversing properties\n
\t\t\t\tcallers.push(a.constructor);\n
\t\t\t\t// track reference to avoid circular references\n
\t\t\t\tparents.push(a);\n
\n
\t\t\t\tfor (i in a) { // be strict: don\'t ensures hasOwnProperty\n
\t\t\t\t\t\t\t\t// and go deep\n
\t\t\t\t\tloop = false;\n
\t\t\t\t\tfor (j = 0; j < parents.length; j++) {\n
\t\t\t\t\t\tif (parents[j] === a[i]) {\n
\t\t\t\t\t\t\t// don\'t go down the same path twice\n
\t\t\t\t\t\t\tloop = true;\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\t\t\t\t\taProperties.push(i); // collect a\'s properties\n
\n
\t\t\t\t\tif (!loop && !innerEquiv(a[i], b[i])) {\n
\t\t\t\t\t\teq = false;\n
\t\t\t\t\t\tbreak;\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\n
\t\t\t\tcallers.pop(); // unstack, we are done\n
\t\t\t\tparents.pop();\n
\n
\t\t\t\tfor (i in b) {\n
\t\t\t\t\tbProperties.push(i); // collect b\'s properties\n
\t\t\t\t}\n
\n
\t\t\t\t// Ensures identical properties name\n
\t\t\t\treturn eq && innerEquiv(aProperties.sort(), bProperties.sort());\n
\t\t\t}\n
\t\t};\n
\t}());\n
\n
\tinnerEquiv = function() { // can take multiple arguments\n
\t\tvar args = Array.prototype.slice.apply(arguments);\n
\t\tif (args.length < 2) {\n
\t\t\treturn true; // end transition\n
\t\t}\n
\n
\t\treturn (function(a, b) {\n
\t\t\tif (a === b) {\n
\t\t\t\treturn true; // catch the most you can\n
\t\t\t} else if (a === null || b === null || typeof a === "undefined" ||\n
\t\t\t\t\ttypeof b === "undefined" ||\n
\t\t\t\t\tQUnit.objectType(a) !== QUnit.objectType(b)) {\n
\t\t\t\treturn false; // don\'t lose time with error prone cases\n
\t\t\t} else {\n
\t\t\t\treturn bindCallbacks(a, callbacks, [ b, a ]);\n
\t\t\t}\n
\n
\t\t\t// apply transition with (1..n) arguments\n
\t\t}(args[0], args[1]) && arguments.callee.apply(this, args.splice(1, args.length - 1)));\n
\t};\n
\n
\treturn innerEquiv;\n
\n
}());\n
\n
/**\n
 * jsDump Copyright (c) 2008 Ariel Flesler - aflesler(at)gmail(dot)com |\n
 * http://flesler.blogspot.com Licensed under BSD\n
 * (http://www.opensource.org/licenses/bsd-license.php) Date: 5/15/2008\n
 *\n
 * @projectDescription Advanced and extensible data dumping for Javascript.\n
 * @version 1.0.0\n
 * @author Ariel Flesler\n
 * @link {http://flesler.blogspot.com/2008/05/jsdump-pretty-dump-of-any-javascript.html}\n
 */\n
QUnit.jsDump = (function() {\n
\tfunction quote( str ) {\n
\t\treturn \'"\' + str.toString().replace(/"/g, \'\\\\"\') + \'"\';\n
\t}\n
\tfunction literal( o ) {\n
\t\treturn o + \'\';\n
\t}\n
\tfunction join( pre, arr, post ) {\n
\t\tvar s = jsDump.separator(),\n
\t\t\tbase = jsDump.indent(),\n
\t\t\tinner = jsDump.indent(1);\n
\t\tif ( arr.join ) {\n
\t\t\tarr = arr.join( \',\' + s + inner );\n
\t\t}\n
\t\tif ( !arr ) {\n
\t\t\treturn pre + post;\n
\t\t}\n
\t\treturn [ pre, inner + arr, base + post ].join(s);\n
\t}\n
\tfunction array( arr, stack ) {\n
\t\tvar i = arr.length, ret = new Array(i);\n
\t\tthis.up();\n
\t\twhile ( i-- ) {\n
\t\t\tret[i] = this.parse( arr[i] , undefined , stack);\n
\t\t}\n
\t\tthis.down();\n
\t\treturn join( \'[\', ret, \']\' );\n
\t}\n
\n
\tvar reName = /^function (\\w+)/;\n
\n
\tvar jsDump = {\n
\t\tparse: function( obj, type, stack ) { //type is used mostly internally, you can fix a (custom)type in advance\n
\t\t\tstack = stack || [ ];\n
\t\t\tvar parser = this.parsers[ type || this.typeOf(obj) ];\n
\t\t\ttype = typeof parser;\n
\t\t\tvar inStack = inArray(obj, stack);\n
\t\t\tif (inStack != -1) {\n
\t\t\t\treturn \'recursion(\'+(inStack - stack.length)+\')\';\n
\t\t\t}\n
\t\t\t//else\n
\t\t\tif (type == \'function\')  {\n
\t\t\t\t\tstack.push(obj);\n
\t\t\t\t\tvar res = parser.call( this, obj, stack );\n
\t\t\t\t\tstack.pop();\n
\t\t\t\t\treturn res;\n
\t\t\t}\n
\t\t\t// else\n
\t\t\treturn (type == \'string\') ? parser : this.parsers.error;\n
\t\t},\n
\t\ttypeOf: function( obj ) {\n
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
\t\t\t} else if (typeof obj.setInterval !== undefined && typeof obj.document !== "undefined" && typeof obj.nodeType === "undefined") {\n
\t\t\t\ttype = "window";\n
\t\t\t} else if (obj.nodeType === 9) {\n
\t\t\t\ttype = "document";\n
\t\t\t} else if (obj.nodeType) {\n
\t\t\t\ttype = "node";\n
\t\t\t} else if (\n
\t\t\t\t// native arrays\n
\t\t\t\ttoString.call( obj ) === "[object Array]" ||\n
\t\t\t\t// NodeList objects\n
\t\t\t\t( typeof obj.length === "number" && typeof obj.item !== "undefined" && ( obj.length ? obj.item(0) === obj[0] : ( obj.item( 0 ) === null && typeof obj[0] === "undefined" ) ) )\n
\t\t\t) {\n
\t\t\t\ttype = "array";\n
\t\t\t} else {\n
\t\t\t\ttype = typeof obj;\n
\t\t\t}\n
\t\t\treturn type;\n
\t\t},\n
\t\tseparator: function() {\n
\t\t\treturn this.multiline ?\tthis.HTML ? \'<br />\' : \'\\n\' : this.HTML ? \'&nbsp;\' : \' \';\n
\t\t},\n
\t\tindent: function( extra ) {// extra can be a number, shortcut for increasing-calling-decreasing\n
\t\t\tif ( !this.multiline ) {\n
\t\t\t\treturn \'\';\n
\t\t\t}\n
\t\t\tvar chr = this.indentChar;\n
\t\t\tif ( this.HTML ) {\n
\t\t\t\tchr = chr.replace(/\\t/g,\'   \').replace(/ /g,\'&nbsp;\');\n
\t\t\t}\n
\t\t\treturn new Array( this._depth_ + (extra||0) ).join(chr);\n
\t\t},\n
\t\tup: function( a ) {\n
\t\t\tthis._depth_ += a || 1;\n
\t\t},\n
\t\tdown: function( a ) {\n
\t\t\tthis._depth_ -= a || 1;\n
\t\t},\n
\t\tsetParser: function( name, parser ) {\n
\t\t\tthis.parsers[name] = parser;\n
\t\t},\n
\t\t// The next 3 are exposed so you can use them\n
\t\tquote: quote,\n
\t\tliteral: literal,\n
\t\tjoin: join,\n
\t\t//\n
\t\t_depth_: 1,\n
\t\t// This is the list of parsers, to modify them, use jsDump.setParser\n
\t\tparsers: {\n
\t\t\twindow: \'[Window]\',\n
\t\t\tdocument: \'[Document]\',\n
\t\t\terror: \'[ERROR]\', //when no parser is found, shouldn\'t happen\n
\t\t\tunknown: \'[Unknown]\',\n
\t\t\t\'null\': \'null\',\n
\t\t\t\'undefined\': \'undefined\',\n
\t\t\t\'function\': function( fn ) {\n
\t\t\t\tvar ret = \'function\',\n
\t\t\t\t\tname = \'name\' in fn ? fn.name : (reName.exec(fn)||[])[1];//functions never have name in IE\n
\t\t\t\tif ( name ) {\n
\t\t\t\t\tret += \' \' + name;\n
\t\t\t\t}\n
\t\t\t\tret += \'(\';\n
\n
\t\t\t\tret = [ ret, QUnit.jsDump.parse( fn, \'functionArgs\' ), \'){\'].join(\'\');\n
\t\t\t\treturn join( ret, QUnit.jsDump.parse(fn,\'functionCode\'), \'}\' );\n
\t\t\t},\n
\t\t\tarray: array,\n
\t\t\tnodelist: array,\n
\t\t\t\'arguments\': array,\n
\t\t\tobject: function( map, stack ) {\n
\t\t\t\tvar ret = [ ], keys, key, val, i;\n
\t\t\t\tQUnit.jsDump.up();\n
\t\t\t\tif (Object.keys) {\n
\t\t\t\t\tkeys = Object.keys( map );\n
\t\t\t\t} else {\n
\t\t\t\t\tkeys = [];\n
\t\t\t\t\tfor (key in map) { keys.push( key ); }\n
\t\t\t\t}\n
\t\t\t\tkeys.sort();\n
\t\t\t\tfor (i = 0; i < keys.length; i++) {\n
\t\t\t\t\tkey = keys[ i ];\n
\t\t\t\t\tval = map[ key ];\n
\t\t\t\t\tret.push( QUnit.jsDump.parse( key, \'key\' ) + \': \' + QUnit.jsDump.parse( val, undefined, stack ) );\n
\t\t\t\t}\n
\t\t\t\tQUnit.jsDump.down();\n
\t\t\t\treturn join( \'{\', ret, \'}\' );\n
\t\t\t},\n
\t\t\tnode: function( node ) {\n
\t\t\t\tvar open = QUnit.jsDump.HTML ? \'&lt;\' : \'<\',\n
\t\t\t\t\tclose = QUnit.jsDump.HTML ? \'&gt;\' : \'>\';\n
\n
\t\t\t\tvar tag = node.nodeName.toLowerCase(),\n
\t\t\t\t\tret = open + tag;\n
\n
\t\t\t\tfor ( var a in QUnit.jsDump.DOMAttrs ) {\n
\t\t\t\t\tvar val = node[QUnit.jsDump.DOMAttrs[a]];\n
\t\t\t\t\tif ( val ) {\n
\t\t\t\t\t\tret += \' \' + a + \'=\' + QUnit.jsDump.parse( val, \'attribute\' );\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t\treturn ret + close + open + \'/\' + tag + close;\n
\t\t\t},\n
\t\t\tfunctionArgs: function( fn ) {//function calls it internally, it\'s the arguments part of the function\n
\t\t\t\tvar l = fn.length;\n
\t\t\t\tif ( !l ) {\n
\t\t\t\t\treturn \'\';\n
\t\t\t\t}\n
\n
\t\t\t\tvar args = new Array(l);\n
\t\t\t\twhile ( l-- ) {\n
\t\t\t\t\targs[l] = String.fromCharCode(97+l);//97 is \'a\'\n
\t\t\t\t}\n
\t\t\t\treturn \' \' + args.join(\', \') + \' \';\n
\t\t\t},\n
\t\t\tkey: quote, //object calls it internally, the key part of an item in a map\n
\t\t\tfunctionCode: \'[code]\', //function calls it internally, it\'s the content of the function\n
\t\t\tattribute: quote, //node calls it internally, it\'s an html attribute value\n
\t\t\tstring: quote,\n
\t\t\tdate: quote,\n
\t\t\tregexp: literal, //regex\n
\t\t\tnumber: literal,\n
\t\t\t\'boolean\': literal\n
\t\t},\n
\t\tDOMAttrs:{//attributes to dump from nodes, name=>realName\n
\t\t\tid:\'id\',\n
\t\t\tname:\'name\',\n
\t\t\t\'class\':\'className\'\n
\t\t},\n
\t\tHTML:false,//if true, entities are escaped ( <, >, \\t, space and \\n )\n
\t\tindentChar:\'  \',//indentation unit\n
\t\tmultiline:true //if true, items in a collection, are separated by a \\n, else just a space.\n
\t};\n
\n
\treturn jsDump;\n
}());\n
\n
// from Sizzle.js\n
function getText( elems ) {\n
\tvar ret = "", elem;\n
\n
\tfor ( var i = 0; elems[i]; i++ ) {\n
\t\telem = elems[i];\n
\n
\t\t// Get the text from text nodes and CDATA nodes\n
\t\tif ( elem.nodeType === 3 || elem.nodeType === 4 ) {\n
\t\t\tret += elem.nodeValue;\n
\n
\t\t// Traverse everything else, except comment nodes\n
\t\t} else if ( elem.nodeType !== 8 ) {\n
\t\t\tret += getText( elem.childNodes );\n
\t\t}\n
\t}\n
\n
\treturn ret;\n
}\n
\n
//from jquery.js\n
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
 * QUnit.diff("the quick brown fox jumped over", "the quick fox jumps over") == "the  quick <del>brown </del> fox <del>jumped </del><ins>jumps </ins> over"\n
 */\n
QUnit.diff = (function() {\n
\tfunction diff(o, n) {\n
\t\tvar ns = {};\n
\t\tvar os = {};\n
\t\tvar i;\n
\n
\t\tfor (i = 0; i < n.length; i++) {\n
\t\t\tif (ns[n[i]] == null) {\n
\t\t\t\tns[n[i]] = {\n
\t\t\t\t\trows: [],\n
\t\t\t\t\to: null\n
\t\t\t\t};\n
\t\t\t}\n
\t\t\tns[n[i]].rows.push(i);\n
\t\t}\n
\n
\t\tfor (i = 0; i < o.length; i++) {\n
\t\t\tif (os[o[i]] == null) {\n
\t\t\t\tos[o[i]] = {\n
\t\t\t\t\trows: [],\n
\t\t\t\t\tn: null\n
\t\t\t\t};\n
\t\t\t}\n
\t\t\tos[o[i]].rows.push(i);\n
\t\t}\n
\n
\t\tfor (i in ns) {\n
\t\t\tif ( !hasOwn.call( ns, i ) ) {\n
\t\t\t\tcontinue;\n
\t\t\t}\n
\t\t\tif (ns[i].rows.length == 1 && typeof(os[i]) != "undefined" && os[i].rows.length == 1) {\n
\t\t\t\tn[ns[i].rows[0]] = {\n
\t\t\t\t\ttext: n[ns[i].rows[0]],\n
\t\t\t\t\trow: os[i].rows[0]\n
\t\t\t\t};\n
\t\t\t\to[os[i].rows[0]] = {\n
\t\t\t\t\ttext: o[os[i].rows[0]],\n
\t\t\t\t\trow: ns[i].rows[0]\n
\t\t\t\t};\n
\t\t\t}\n
\t\t}\n
\n
\t\tfor (i = 0; i < n.length - 1; i++) {\n
\t\t\tif (n[i].text != null && n[i + 1].text == null && n[i].row + 1 < o.length && o[n[i].row + 1].text == null &&\n
\t\t\tn[i + 1] == o[n[i].row + 1]) {\n
\t\t\t\tn[i + 1] = {\n
\t\t\t\t\ttext: n[i + 1],\n
\t\t\t\t\trow: n[i].row + 1\n
\t\t\t\t};\n
\t\t\t\to[n[i].row + 1] = {\n
\t\t\t\t\ttext: o[n[i].row + 1],\n
\t\t\t\t\trow: i + 1\n
\t\t\t\t};\n
\t\t\t}\n
\t\t}\n
\n
\t\tfor (i = n.length - 1; i > 0; i--) {\n
\t\t\tif (n[i].text != null && n[i - 1].text == null && n[i].row > 0 && o[n[i].row - 1].text == null &&\n
\t\t\tn[i - 1] == o[n[i].row - 1]) {\n
\t\t\t\tn[i - 1] = {\n
\t\t\t\t\ttext: n[i - 1],\n
\t\t\t\t\trow: n[i].row - 1\n
\t\t\t\t};\n
\t\t\t\to[n[i].row - 1] = {\n
\t\t\t\t\ttext: o[n[i].row - 1],\n
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
\treturn function(o, n) {\n
\t\to = o.replace(/\\s+$/, \'\');\n
\t\tn = n.replace(/\\s+$/, \'\');\n
\t\tvar out = diff(o === "" ? [] : o.split(/\\s+/), n === "" ? [] : n.split(/\\s+/));\n
\n
\t\tvar str = "";\n
\t\tvar i;\n
\n
\t\tvar oSpace = o.match(/\\s+/g);\n
\t\tif (oSpace == null) {\n
\t\t\toSpace = [" "];\n
\t\t}\n
\t\telse {\n
\t\t\toSpace.push(" ");\n
\t\t}\n
\t\tvar nSpace = n.match(/\\s+/g);\n
\t\tif (nSpace == null) {\n
\t\t\tnSpace = [" "];\n
\t\t}\n
\t\telse {\n
\t\t\tnSpace.push(" ");\n
\t\t}\n
\n
\t\tif (out.n.length === 0) {\n
\t\t\tfor (i = 0; i < out.o.length; i++) {\n
\t\t\t\tstr += \'<del>\' + out.o[i] + oSpace[i] + "</del>";\n
\t\t\t}\n
\t\t}\n
\t\telse {\n
\t\t\tif (out.n[0].text == null) {\n
\t\t\t\tfor (n = 0; n < out.o.length && out.o[n].text == null; n++) {\n
\t\t\t\t\tstr += \'<del>\' + out.o[n] + oSpace[n] + "</del>";\n
\t\t\t\t}\n
\t\t\t}\n
\n
\t\t\tfor (i = 0; i < out.n.length; i++) {\n
\t\t\t\tif (out.n[i].text == null) {\n
\t\t\t\t\tstr += \'<ins>\' + out.n[i] + nSpace[i] + "</ins>";\n
\t\t\t\t}\n
\t\t\t\telse {\n
\t\t\t\t\tvar pre = "";\n
\n
\t\t\t\t\tfor (n = out.n[i].row + 1; n < out.o.length && out.o[n].text == null; n++) {\n
\t\t\t\t\t\tpre += \'<del>\' + out.o[n] + oSpace[n] + "</del>";\n
\t\t\t\t\t}\n
\t\t\t\t\tstr += " " + out.n[i].text + nSpace[i] + pre;\n
\t\t\t\t}\n
\t\t\t}\n
\t\t}\n
\n
\t\treturn str;\n
\t};\n
}());\n
\n
// for CommonJS enviroments, export everything\n
if ( typeof exports !== "undefined" || typeof require !== "undefined" ) {\n
\textend(exports, QUnit);\n
}\n
\n
// get at whatever the global object is, like window in browsers\n
}( (function() {return this;}.call()) ));\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>43559</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>qunit.js</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
