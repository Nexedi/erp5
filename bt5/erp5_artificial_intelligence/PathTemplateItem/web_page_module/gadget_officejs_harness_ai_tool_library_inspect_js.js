/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  rJS(window)
    .declareMethod('getDefinition', function () {
      return {
        name: "library_inspect",
        description: "Download a library (if not already cached) and report what it actually exposes - " +
          "its own and prototype property/method names - so you can check its real API surface before " +
          "writing code against it instead of guessing. Accepts any https:// URL to a UMD/IIFE script or " +
          "an .mjs ES module (the requesting website must allow cross-origin fetches, e.g. most CDNs do " +
          "- there is no proxy to work around one that doesn't).",
        allow_repeat: true,
        parameters: {
          type: "object",
          properties: {
            libraries: {
              type: "array",
              description: "https:// URLs to inspect, e.g. [\"https://cdn.jsdelivr.net/npm/nanoid@5/bin/index.js\"].",
              items: { type: "string" }
            }
          },
          required: ["libraries"]
        }
      };
    })
    .declareMethod('render', function () {
      return;
    })
    .declareMethod('execute', function (args) {
      return new RSVP.Queue(window.ChatToolCommon.runSandboxJob("library_inspect", { libraries: args.libraries }))
        .push(function (result) {
          if (!result.ok) { return "ERROR: " + result.error; }
          return result.libraries.map(function (lib) {
            if (lib.error) { return lib.name + " - ERROR: " + lib.error; }
            return lib.name + (lib.global ? " (global \"" + lib.global + "\")" : "") + ", " + lib.type +
              ": " + lib.description + "\n  " + lib.url +
              (lib.members.length ? "\n  members: " + lib.members.join(", ") : "");
          }).join("\n\n");
        });
    });
}(window, rJS, RSVP));
