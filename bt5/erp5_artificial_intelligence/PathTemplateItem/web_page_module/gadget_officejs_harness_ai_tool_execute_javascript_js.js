/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  rJS(window)
    .declareMethod('getDefinition', function () {
      return {
        name: "execute_javascript",
        description: "Execute JavaScript and get the result back. Runs in the same isolated sandbox " +
          "worker as run_wasm - no DOM, no cookies, no access to the page or any other tool's state " +
          "(the only network access is the optional library fetch below, done by this worker itself, " +
          "never by your code). Write the body of an async function: `await` is available, and you " +
          "must \"return <value>;\" to produce a result (only JSON-serializable values are usable; " +
          "console output is captured separately and returned alongside the result). A `utils` object " +
          "with b64encode/b64decode/describe/wat2wasm helpers is also available to the code. Pass " +
          "`libraries` (https:// URLs to a UMD/IIFE script or .mjs ES module) to preload third-party " +
          "helpers, available both as their usual global (e.g. a UMD bundle's own global, auto-detected) " +
          "and via `lib[\"<the URL you passed>\"]`. Errors thrown by the " +
          "code are reported back as an error message; a runaway loop is killed at its deadline, which " +
          "costs one worker, not the tab. USE THIS WHEN: you need custom computation or to " +
          "reshape/combine data you already have (e.g. a previous tool's result) that's easier to do in " +
          "code than by hand. DO NOT USE THIS WHEN: an existing tool (an MCP server's tools, draw_*, " +
          "run_wasm) already does what you need, or you need DOM/arbitrary network access - this sandbox " +
          "cannot reach either.",
        parameters: {
          type: "object",
          properties: {
            code: {
              type: "string",
              description: "Async function body, e.g. \"return 1 + 1;\" or " +
                "\"var total = 0; for (var i = 0; i < 10; i++) { total += i; } return total;\"."
            },
            libraries: {
              type: "array",
              description: "https:// URLs to load before running code, e.g. [\"https://cdn.jsdelivr.net/npm/lodash@4.17.21/lodash.min.js\"].",
              items: { type: "string" }
            },
            timeout_ms: { type: "integer", description: "Deadline in ms (default 10000, max 120000)." }
          },
          required: ["code"]
        }
      };
    })
    .declareMethod('render', function () {
      return;
    })
    .declareMethod('execute', function (args) {
      return new RSVP.Queue(window.ChatToolCommon.runSandboxJob("js", { code: args.code, libraries: args.libraries }, args.timeout_ms))
        .push(function (result) {
          var parts = [];
          if (result.logs && result.logs.length) {
            parts.push("console:\n" + result.logs.join("\n"));
          }
          if (result.ok) {
            parts.push("result:\n" + (result.resultText || "(undefined)"));
          } else {
            parts.push("ERROR: " + result.error + (result.stack ? "\n" + result.stack : ""));
          }
          return parts.join("\n\n");
        });
    });
}(window, rJS, RSVP));
