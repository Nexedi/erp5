/*global window, rJS */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS) {
  "use strict";

  // A tool result longer than this is cut: the model sees its start and its
  // end, and reads the rest with read_tool_output.
  var TOOL_OUTPUT_MAX_CHARS = 40000,
    // How many cut tool results are kept, the oldest are dropped.
    TOOL_OUTPUT_KEEP_COUNT = 20;

  rJS(window)
    .declareMethod('getDefinition', function () {
      return {
        name: "read_tool_output",
        description: "Read an earlier tool result that was cut because it was too large: it says " +
          "\"[Output too large: ...]\" and gives an output_id. The full results are kept " +
          "only until this page is closed or reloaded, and the oldest are dropped. One " +
          "call returns at most " + window.ChatToolCommon.TEXT_WINDOW_CHARS +
          " chars: search with `pattern`, then read around the matches with min_chars, " +
          "instead of reading it all.",
        parameters: {
          type: "object",
          properties: {
            output_id: { type: "string", description: "The output_id given in the cut result, eg. \"output_1\"." },
            min_chars: { type: "integer", description: "Char offset to start reading from (default 0)." },
            max_chars: { type: "integer", description: "Char offset to stop at (default and maximum: min_chars + " +
              window.ChatToolCommon.TEXT_WINDOW_CHARS + ")." },
            pattern: { type: "string", description: "Search the whole result instead of reading it: a case-insensitive regular " +
              "expression. Returns each match with its char offset and " +
              window.ChatToolCommon.TEXT_SEARCH_CONTEXT_CHARS + " chars of context on each side, at most " +
              window.ChatToolCommon.TEXT_SEARCH_MAX_MATCHES +
              " matches. min_chars and max_chars are ignored." }
          },
          required: ["output_id"]
        }
      };
    })
    .declareMethod('render', function () {
      // Full text of the cut tool results, by output_id.
      this.text_dict = {};
      this.output_id_list = [];
      this.output_count = 0;
    })
    // The content of a tool result as it is sent to the model: as is if it is
    // not longer than TOOL_OUTPUT_MAX_CHARS, otherwise its start and its end
    // with a notice, the full text being kept for execute.
    .declareMethod('limitToolOutput', function (content) {
      var gadget = this,
        half = TOOL_OUTPUT_MAX_CHARS / 2,
        output_id;
      if (typeof content !== "string" || content.length <= TOOL_OUTPUT_MAX_CHARS) {
        return content;
      }
      gadget.output_count += 1;
      output_id = "output_" + gadget.output_count;
      gadget.text_dict[output_id] = content;
      gadget.output_id_list.push(output_id);
      if (gadget.output_id_list.length > TOOL_OUTPUT_KEEP_COUNT) {
        delete gadget.text_dict[gadget.output_id_list.shift()];
      }
      return "[Output too large: " + content.length + " chars, only the first and the last " +
        half + " are shown. The full output is kept as output_id \"" + output_id + "\": call " +
        "read_tool_output to read another part of it or to search it.]\n\n" +
        content.slice(0, half) + "\n\n[... " + (content.length - 2 * half) + " chars not shown ...]\n\n" +
        content.slice(content.length - half);
    })
    .declareMethod('execute', function (args) {
      var text = this.text_dict[args.output_id];
      if (typeof text !== "string") {
        return "ERROR: no output \"" + args.output_id + "\" is kept. Only the outputs cut in " +
          "this page are kept, the oldest are dropped: run the tool again if you need it.";
      }
      if (args.pattern) {
        return window.ChatToolCommon.searchText(text, args.pattern);
      }
      return window.ChatToolCommon.readTextWindow(text, args.min_chars, args.max_chars);
    });
}(window, rJS));
