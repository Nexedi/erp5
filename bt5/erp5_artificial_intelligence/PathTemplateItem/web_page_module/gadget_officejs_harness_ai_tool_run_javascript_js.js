/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  rJS(window)
    .declareMethod('getDefinition', function () {
      return {
        name: "run_javascript",
        description: "Run JavaScript in an isolated sandbox (a web worker: no DOM, no access to the " +
          "page, no cookies) and return its result, with its console output. Use it for a " +
          "computation or to reshape data, not for what another tool does. The code can " +
          "not see the other tools or their results: to process a result, write the data " +
          "the code needs into it. To get data from the web, use http_request, not fetch() " +
          "in the code.",
        parameters: {
          type: "object",
          properties: {
            code: { type: "string", description: "Body of an async function: `await` works, and `return` gives the result, which " +
              "must be JSON serializable. It receives `utils` (b64encode, b64decode, describe, " +
              "wat2wasm) and `lib`. Eg. \"var total = 0; for (var i = 0; i < 10; i += 1) { " +
              "total += i; } return total;\"." },
            libraries: {
              type: "array",
              items: { type: "string" },
              description: "https:// URLs of scripts to load before the code runs (UMD/IIFE script or .mjs " +
                "ES module). Each one is in lib[url], and under its usual global name. To learn " +
                "the API of a library, return Object.keys(lib[url]) first, instead of guessing."
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
