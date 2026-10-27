/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";


  var PDFJS_SCRIPT_URL = "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.0.379/pdf.min.mjs",
    PDFJS_WORKER_URL = "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.0.379/pdf.worker.min.mjs",
    PDF_TEXT_DEFAULT_MAX_CHARS = 100000,
    PDF_EXTRACT_SANDBOX_CODE = [
      "var pdfjsLib = lib[" + JSON.stringify(PDFJS_SCRIPT_URL) + "];",
      "pdfjsLib.GlobalWorkerOptions.workerSrc = " + JSON.stringify(PDFJS_WORKER_URL) + ";",
      "var pdf = await pdfjsLib.getDocument({ data: utils.b64decode(args.base64), disableWorker: true }).promise;",
      "var i, page, content, text_list = [];",
      "for (i = 1; i <= pdf.numPages; i += 1) {",
      "  page = await pdf.getPage(i);",
      "  content = await page.getTextContent();",
      "  text_list.push(content.items.map(function (item) { return item.str; }).join(' '));",
      "}",
      "var text = text_list.join('\\n\\n'), truncated = text.length > args.max_chars;",
      "return 'PDF: ' + args.file_name + ' (' + pdf.numPages + ' page' + (pdf.numPages === 1 ? '' : 's') + ')\\n\\n' +",
      "  text.slice(0, args.max_chars) + (truncated ? '\\n... [truncated at ' + args.max_chars + ' chars]' : '');"
    ].join('\n');

  // The attachment link is a "data:<mime>[;base64],<payload>" URI (see
  // gadget_chat_ui_js.js's getAttachmentContentPart/parseDataUri).
  function parseDataUri(data_uri) {
    var match = /^data:([^;,]*)(?:;[^,]*)?,([\s\S]*)$/.exec(data_uri || "");
    return match ? { mime: match[1], base64: match[2] } : null;
  }

  rJS(window)
    .declareAcquiredMethod("getCommentPostList", "getCommentPostList")
    .declareMethod('render', function (options) {
      this.jio_key = options.jio_key;
    })
    .declareMethod('getDefinition', function () {
      return {
        name: "pdf_to_text",
        description: "Extract and return the text content of a PDF attachment the user uploaded in " +
          "this conversation - PDFs are not sent as part of the conversation automatically, call this " +
          "tool to read one. Give the exact attachment file name if more than one PDF has been " +
          "uploaded; without it, the most recently uploaded PDF is used.",
        allow_repeat: true,
        parameters: {
          type: "object",
          properties: {
            file_name: { type: "string", description: "Exact attachment file name. Optional - " +
              "defaults to the most recently uploaded PDF." },
            max_chars: { type: "integer", description: "Truncate the returned text to this many " +
              "characters (default " + PDF_TEXT_DEFAULT_MAX_CHARS + ")." },
            timeout_ms: { type: "integer", description: "Deadline in ms (default 30000, max 120000)." }
          }
        }
      };
    })
    .declareMethod('execute', function (args) {
      var gadget = this;
      return gadget.getCommentPostList(gadget.jio_key)
        .push(function (post_list) {
          var candidate_list = post_list.filter(function (post) {
              return post.attachment_link && (/^data:application\/pdf/i).test(post.attachment_link) &&
                (!args.file_name || post.attachment_name === args.file_name);
            }),
            post,
            parsed;
          if (!candidate_list.length) {
            return "ERROR: no PDF attachment" + (args.file_name ? " named \"" + args.file_name + "\"" : "") +
              " found in this conversation.";
          }
          post = candidate_list[candidate_list.length - 1];
          parsed = parseDataUri(post.attachment_link);
          return new RSVP.Queue(window.ChatToolCommon.runSandboxJob("js", {
            code: PDF_EXTRACT_SANDBOX_CODE,
            args: {
              base64: parsed.base64,
              file_name: post.attachment_name,
              max_chars: args.max_chars || PDF_TEXT_DEFAULT_MAX_CHARS
            },
            libraries: [PDFJS_SCRIPT_URL]
          }, args.timeout_ms || 30000))
            .push(function (result) {
              if (!result.ok) {
                return "ERROR: " + (result.error || JSON.stringify(result)) +
                  (result.stack ? "\n" + result.stack : "") +
                  (result.logs && result.logs.length ? "\n\nconsole:\n" + result.logs.join("\n") : "");
              }
              return result.resultText;
            });
        });
    });
}(window, rJS, RSVP));
