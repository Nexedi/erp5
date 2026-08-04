"""
A minimal UMD-style script exposing one global, used only by the Zelenium
test for the library_inspect tool (testOfficeJSHarnessAILibraryInspectTool.zpt).
Fetched by gadget_officejs_harness_ai_sandbox_worker_js.js's loadLibraries(),
which evals classic/UMD sources and auto-detects whichever global newly
appeared - same-origin and fixed content, so the test doesn't depend on any
real external library staying reachable or unchanged.

resolveEntry() in the sandbox worker requires an https:// URL, so this only
works against an https instance (true of every real deployment this test
runs against).
"""
request = context.REQUEST
request.RESPONSE.setHeader('Content-Type', 'application/javascript')
return (
    '(function () {\n'
    '  self.FakeTestLibrary = {\n'
    '    double: function (n) { return n * 2; },\n'
    '    VERSION: "1.0.0"\n'
    '  };\n'
    '}());\n'
)
