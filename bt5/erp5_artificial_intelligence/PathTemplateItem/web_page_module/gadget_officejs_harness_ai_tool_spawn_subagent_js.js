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
          "that tool directly.",
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
        tool_definition_list_json;

      function subagentLoopCall(loop_count, message_list, pending_tool_call_list) {
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
              return RSVP.all(pending_tool_call_list.map(function (tool_call) {
                return window.ChatToolCommon.runClientToolCall(tool_call, tool_list);
              }));
            })
            .push(function (client_tool_result_list) {
              var next_message_list = message_list, i, tool_call, client_tool_result;
              for (i = 0; i < pending_tool_call_list.length; i += 1) {
                tool_call = pending_tool_call_list[i];
                client_tool_result = client_tool_result_list[i];
                next_message_list = next_message_list.concat([{
                  role: "tool",
                  tool_call_id: tool_call.id,
                  name: tool_call.function.name,
                  content: client_tool_result.content
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
            return gadget.requestProcessTask(
              document_id,
              {
                message_list: JSON.stringify(message_list),
                tool_definition_list: tool_definition_list_json
              }
            );
          })
          .push(function (result) {
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
          subagentLoopCall(0, [{ role: "user", content: args.task }]);
        });

      return queue_loop;
    });
}(window, rJS, RSVP));
