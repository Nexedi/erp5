/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  var SUBAGENT_DEFAULT_MAX_LOOP_COUNT = 2000,
    SUBAGENT_MAX_LOOP_COUNT_CAP = 5000,
    SUBAGENT_EXCLUDED_TOOL_NAME_LIST = ["spawn_subagent", "execution_plan"];

  rJS(window)
    .declareAcquiredMethod("requestProcessTask", "requestProcessTask")
    .declareAcquiredMethod("getToolList", "getToolList")
    .declareAcquiredMethod("compactMessageList", "compactMessageList")
    .declareAcquiredMethod("summarizeToolOutput", "summarizeToolOutput")
    .declareAcquiredMethod("addUsageToTotals", "addUsageToTotals")
    .declareMethod('render', function (options) {
      this.jio_key = options.jio_key;
    })
    .declareMethod('getDefinition', function () {
      return {
        name: "spawn_subagent",
        description: "Delegate a self-contained sub-task to a fresh, independent instance of this " +
          "same agent - same tools (everything except spawn_subagent itself, to prevent runaway " +
          "recursion), but its own separate conversation that starts empty (it has NO access to this " +
          "conversation's history - give it a full, self-contained task description). Runs to " +
          "completion (its own multi-turn tool-calling loop) before this call returns; only its final " +
          "answer comes back - none of its intermediate searches/reads/retries appear in this " +
          "conversation. USE THIS WHEN: a piece of the current task is large or noisy enough to " +
          "isolate (e.g. \"research X and summarize\", \"go create and populate these 5 documents, " +
          "report back what was done\"). DO NOT USE THIS for a trivial one-tool-call task - just call " +
          "that tool directly. WARNING: a sub-agent's own conversation has the exact same context " +
          "size limit as this one - it does NOT give you a bigger context window, only a separate " +
          "one. If the reference material for a sub-task is itself too large to read through in one " +
          "conversation (e.g. a document of hundreds of pages), do not hand the whole thing to a " +
          "single spawn_subagent call and expect it to read all of it sequentially - that just moves " +
          "the same overflow problem one level down. Instead, split the material into bounded chunks " +
          "yourself (e.g. by page range) and make one spawn_subagent call per chunk (\"read pages " +
          "40-60 of document X and extract/summarize Y\"), each starting fresh with no memory of the " +
          "others, then combine their individual (short) results yourself - recursively, in another " +
          "batch of chunked calls, if even those combined results would be too large for one call. " +
          "Do NOT launch a large number of these at once (e.g. dozens or more in one batch) - each " +
          "one is a full separate conversation with the LLM backend, and firing too many in parallel " +
          "can overwhelm it. Keep any one batch to a handful of chunks, and process the rest in " +
          "further batches afterwards.",
        parameters: {
          type: "object",
          properties: {
            task: {
              type: "string",
              description: "Full, self-contained description of what the sub-agent should do."
            },
            max_turns: {
              type: "integer",
              description: "Cap on the sub-agent's own turn count (default 20, max 50)."
            }
          },
          required: ["task"]
        }
      };
    })
    .declareMethod('execute', function (args) {
      var gadget = this,
        queue_loop = new RSVP.Queue(),
        document_id = gadget.jio_key,
        max_loop_count = Math.min(Math.max(Number(args.max_turns) || SUBAGENT_DEFAULT_MAX_LOOP_COUNT, 1), SUBAGENT_MAX_LOOP_COUNT_CAP),
        tool_list,
        tool_definition_list_json,
        last_usage_anchor;

      function subagentLoopCall(loop_count, message_list, pending_tool_call_list) {
        console.log('************call sub agent: ' + loop_count);

        var has_tool_call = Boolean(pending_tool_call_list && pending_tool_call_list.length);

        function subagentError(e) {
          return {
            content: "Error running sub-agent: " + JSON.stringify(e, Object.getOwnPropertyNames(e)),
            message_list: message_list
          };
        }
        if (loop_count >= max_loop_count) {
          return new RSVP.Queue().push(function () {
            return {
              content: "[subagent stopped: exceeded " + max_loop_count + " turns without a final answer]",
              message_list: message_list
            };
          });
        }

        if (has_tool_call) {
          queue_loop
            .push(function () {
              return window.ChatToolCommon.runClientToolCallList(pending_tool_call_list, message_list, tool_list);
            })
            .push(function (client_tool_result_list) {
              var summarize_queue = new RSVP.Queue(),
                summarized_content_list = [];
              client_tool_result_list.forEach(function (client_tool_result, i) {
                summarize_queue
                  .push(function () {
                    return gadget.summarizeToolOutput(client_tool_result.content);
                  })
                  .push(function (summarized_content) {
                    summarized_content_list[i] = summarized_content;
                  });
              });
              return summarize_queue.push(function () {
                return summarized_content_list;
              });
            })
            .push(function (summarized_content_list) {
              var next_message_list = message_list, i, tool_call;
              for (i = 0; i < pending_tool_call_list.length; i += 1) {
                tool_call = pending_tool_call_list[i];
                next_message_list = next_message_list.concat([{
                  role: "tool",
                  tool_call_id: tool_call.id,
                  name: tool_call.function.name,
                  content: summarized_content_list[i]
                }]);
              }
              return subagentLoopCall(
                loop_count + 1,
                next_message_list,
                null
              );
            })
            .push(undefined, subagentError);
          return;
        }

        queue_loop
          .push(function () {
            return gadget.compactMessageList(message_list, undefined, last_usage_anchor);
          })
          .push(function (compacted_message_list) {
            message_list = compacted_message_list;
            return gadget.requestProcessTask(
              document_id,
              {
                message_list: JSON.stringify(message_list),
                tool_definition_list: tool_definition_list_json,
                is_background: "1"
              }
            );
          })
          .push(function (result) {
            gadget.addUsageToTotals(result.usage);
            if (result.usage && result.usage.prompt_tokens) {
              last_usage_anchor = { prompt_tokens: result.usage.prompt_tokens, message_count: message_list.length };
            }
            if (result.tool_calls && result.tool_calls.length) {
              return subagentLoopCall(
                loop_count + 1,
                message_list.concat([{
                  role: "assistant",
                  content: result.content,
                  tool_calls: result.tool_calls
                }]),
                result.tool_calls
              );
            }
            return {
              content: result.content,
              message_list: message_list.concat([{ role: "assistant", content: result.content }])
            };
          })
          .push(undefined, subagentError);
      }

      queue_loop
        .push(function () {
          return gadget.getToolList();
        })
        .push(function (resolved_tool_list) {
          tool_list = resolved_tool_list;
          tool_definition_list_json = JSON.stringify(window.ChatToolCommon.toolDefinitionList(tool_list.filter(function (tool) {
            return SUBAGENT_EXCLUDED_TOOL_NAME_LIST.indexOf(tool.definition.name) === -1;
          })));
          subagentLoopCall(0, [
            { role: "system", content: window.ChatToolCommon.ENVIRONMENT_SYSTEM_PROMPT },
            { role: "system", content: window.ChatToolCommon.TOOL_CALL_REPEAT_SYSTEM_PROMPT },
            { role: "user", content: args.task }
          ]);
        });

      return queue_loop;
    });
}(window, rJS, RSVP));
