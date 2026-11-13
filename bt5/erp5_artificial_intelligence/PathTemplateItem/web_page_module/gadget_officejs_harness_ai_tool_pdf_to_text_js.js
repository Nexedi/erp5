/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";


  var PDFJS_SCRIPT_URL = "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.0.379/pdf.min.mjs",
    PDFJS_WORKER_URL = "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.0.379/pdf.worker.min.mjs",
    PDF_EXTRACT_SANDBOX_CODE = [
      "var pdfjsLib = lib[" + JSON.stringify(PDFJS_SCRIPT_URL) + "];",
      "pdfjsLib.GlobalWorkerOptions.workerSrc = " + JSON.stringify(PDFJS_WORKER_URL) + ";",
      "var pdf = await pdfjsLib.getDocument({ data: utils.b64decode(args.base64), disableWorker: true }).promise;",
      "var i, page, content, text = '', page_start_list = [];",
      "for (i = 1; i <= pdf.numPages; i += 1) {",
      "  page = await pdf.getPage(i);",
      "  content = await page.getTextContent();",
      "  if (i > 1) { text += '\\n\\n'; }",
      "  page_start_list.push(text.length);",
      "  text += content.items.map(function (item) { return item.str + (item.hasEOL ? '\\n' : ' '); }).join('');",
      "}",
      "return { num_pages: pdf.numPages, page_start_list: page_start_list, text: text };"
    ].join('\n');

  // " (pages x-y)" for the chars [start, end) of the extracted text.
  function pageLocator(page_start_list) {
    function pageOf(offset) {
      var page = 0;
      while (page + 1 < page_start_list.length && page_start_list[page + 1] <= offset) {
        page += 1;
      }
      return page + 1;
    }
    return function (start, end) {
      var first = pageOf(start), last = pageOf(Math.max(start, end - 1));
      return first === last ? ", page " + first : ", pages " + first + "-" + last;
    };
  }

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
        description: "Read the text of a PDF the user attached to this conversation: attached PDFs " +
          "are not sent to you otherwise. One call returns at most " +
          window.ChatToolCommon.TEXT_WINDOW_CHARS +
          " chars. For a long PDF, read its start (table of contents), then search it with " +
          "`pattern` and read around the matches with min_chars.",
        allow_repeat: true,
        parameters: {
          type: "object",
          properties: {
            file_name: { type: "string", description: "Exact file name of the attachment (default: the last PDF attached)." },
            min_chars: { type: "integer", description: "Char offset to start reading from (default 0)." },
            max_chars: { type: "integer", description: "Char offset to stop at (default and maximum: min_chars + " +
              window.ChatToolCommon.TEXT_WINDOW_CHARS + ")." },
            pattern: { type: "string", description: "Search the whole text instead of reading it: a case-insensitive regular " +
              "expression (eg. \"deadline|closing date\"). Returns each match with its page, " +
              "char offset and " + window.ChatToolCommon.TEXT_SEARCH_CONTEXT_CHARS +
              " chars of context on each side, at most " + window.ChatToolCommon.TEXT_SEARCH_MAX_MATCHES +
              " matches. min_chars and max_chars are ignored." },
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
            args: { base64: parsed.base64 },
            libraries: [PDFJS_SCRIPT_URL]
          }, args.timeout_ms || 30000))
            .push(function (result) {
              var pdf = result.result,
                locate,
                header;
              if (!result.ok) {
                return "ERROR: " + (result.error || JSON.stringify(result)) +
                  (result.stack ? "\n" + result.stack : "") +
                  (result.logs && result.logs.length ? "\n\nconsole:\n" + result.logs.join("\n") : "");
              }
              locate = pageLocator(pdf.page_start_list);
              header = "PDF: " + post.attachment_name + " (" + pdf.num_pages + " page" +
                  (pdf.num_pages === 1 ? "" : "s") + ", " + pdf.text.length + " chars total)\n\n";
              if (args.pattern) {
                return header + window.ChatToolCommon.searchText(pdf.text, args.pattern, locate);
              }
              return header + window.ChatToolCommon.readTextWindow(pdf.text, args.min_chars, args.max_chars, locate);
            });
        });
    });
}(window, rJS, RSVP));
