/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  var COMPACT_THRESHOLD = 50,
    KEEP_RECENT = 20,
    MAX_TOOL_OUTPUT_LINES = 200,
    SUBAGENT_DEFAULT_MAX_LOOP_COUNT = 20,
    SUBAGENT_MAX_LOOP_COUNT_CAP = 50;

  function truncateToolOutput(content) {
    var text = typeof content === "string" ? content : JSON.stringify(content),
      lines = text.split("\n"),
      kept;
    if (lines.length <= MAX_TOOL_OUTPUT_LINES) {
      return text;
    }
    kept = lines.slice(-MAX_TOOL_OUTPUT_LINES).join("\n");
    return "[output truncated: showing last " + MAX_TOOL_OUTPUT_LINES + " of " +
      lines.length + " lines - full output is visible in the tool call panel]\n" + kept;
  }

  function findClientTool(name, tool_list) {
    var i;
    for (i = 0; i < tool_list.length; i += 1) {
      if (tool_list[i].definition.name === name) {
        return tool_list[i];
      }
    }
    return null;
  }

  function runClientToolCall(tool_call, tool_list) {
    var tool = findClientTool(tool_call.function.name, tool_list),
      args = {},
      result;
    try {
      args = tool_call.function.arguments ?
        JSON.parse(tool_call.function.arguments) : {};
    } catch (ignore) {
      args = {};
    }
    if (!tool) {
      result = "Error: no such client tool \"" + tool_call.function.name + "\"";
      return {
        tool_call_id: tool_call.id,
        name: tool_call.function.name,
        content: typeof result === "string" ? result : JSON.stringify(result)
      };
    }
    return new RSVP.Queue()
      .push(function () {
        return tool.execute(args);
      })
      .push(function (result) {

        var message_list = result && typeof result === "object" ? result.message_list : undefined,
          content = message_list ? result.content : result;
        return {
          tool_call_id: tool_call.id,
          name: tool_call.function.name,
          content: typeof content === "string" ? content : JSON.stringify(content),
          message_list: message_list
        };
      }, function (e) {
      result = "Error running tool \"" + tool_call.function.name + "\": " + JSON.stringify(e, Object.getOwnPropertyNames(e));
      return {
        tool_call_id: tool_call.id,
        name: tool_call.function.name,
        content: result
      };
    });
  }

  rJS(window)
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")
    .declareAcquiredMethod("requestProcessTask", "requestProcessTask")
    .declareAcquiredMethod("storeTaskResult", "storeTaskResult")

    .declareMethod('runSubagentTask', function (task, max_turns) {
      var gadget = this,
        queue_loop = new RSVP.Queue(),
        document_id = gadget.options.jio_key,
        max_loop_count = Math.min(Math.max(Number(max_turns) || SUBAGENT_DEFAULT_MAX_LOOP_COUNT, 1), SUBAGENT_MAX_LOOP_COUNT_CAP),
        tool_definition_list = gadget.tool_list
          .filter(function (tool) { return tool.definition.name !== "spawn_subagent"; })
          .map(function (tool) { return { type: "function", "function": tool.definition }; });

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
                return runClientToolCall(tool_call, gadget.tool_list);
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
                  content: truncateToolOutput('args:' + (tool_call.function.arguments ? tool_call.function.arguments : '') + '\n' + 'result:' + client_tool_result.content)
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
                tool_definition_list: JSON.stringify(tool_definition_list),
                is_subagent: "1"
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

      subagentLoopCall(0, [{ role: "user", content: task }]);
      return queue_loop;
    })

    .declareMethod('render', function (options) {
      var gadget = this;
      gadget.options = options;
      gadget.tool_list = window.ChatTools.createToolList(gadget.element, options.hateoas_url);
      gadget.tool_list.push({
        definition: {
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
        },
        execute: function (args) {
          return gadget.runSubagentTask(args.task, args.max_turns);
        }
      });
      return gadget.getDeclaredGadget("gadget_chat_ui")
        .push(function (gadget_chat_ui) {
          gadget.gadget_chat_ui = gadget_chat_ui;
          return gadget_chat_ui.render(options);
        })
        .push(function () {
          if (options.chat_state === 'planned') {
            return gadget.processTask(200);
          }
        });
    })
    .allowPublicAcquisition('notifyCommentPosted', function () {
      return this.processTask(200);
    })
    .declareMethod('compactMessageList', function (message_list) {
      var gadget = this,
        leading_system_count = 0,
        cut_index,
        leading_system_message_list,
        old_message_list,
        recent_message_list;
      if (message_list.length < COMPACT_THRESHOLD) {
        return message_list;
      }
      while (leading_system_count < message_list.length &&
          message_list[leading_system_count].role === "system") {
        leading_system_count += 1;
      }

      cut_index = Math.max(message_list.length - KEEP_RECENT, leading_system_count);
      while (cut_index > leading_system_count &&
          message_list[cut_index].role === "tool") {
        cut_index -= 1;
      }
      leading_system_message_list = message_list.slice(0, leading_system_count);
      old_message_list = message_list.slice(leading_system_count, cut_index);
      recent_message_list = message_list.slice(cut_index);

      if (!old_message_list.length) {
        return message_list;
      }

      return gadget.requestProcessTask(
        gadget.options.jio_key,
        { compact_message_list: JSON.stringify(old_message_list) }
      )
        .push(function (result) {
          if (!result.content) {
            throw new Error("compactMessageList: empty summary");
          }
          return leading_system_message_list.concat([{
            role: "user", //XXXXX this change all message role to user
            content: "[context summary]\n" + result.content
          }], recent_message_list);
        })
        .push(undefined, function () {
          return message_list;
        });
    })
    .declareJob('processTask', function (max_loop_count, skill_list) {
      var gadget = this,
        queue_loop = new RSVP.Queue(),
        tool_message_list = [],
        initial_message_length = 0,
        tool_definition_list = gadget.tool_list.map(function (tool) {
          return { type: "function", "function": tool.definition };
        });

      function loop_call(loop_count, message_list, pending_tool_call_list) {
        var has_tool_call = Boolean(
            pending_tool_call_list && pending_tool_call_list.length
          );
        if (loop_count >= max_loop_count) {
          throw new Error("processTask: too many iterations");
        }

        if (has_tool_call) {
          queue_loop
            .push(function () {
              return RSVP.all(pending_tool_call_list.map(function (tool_call) {
                return runClientToolCall(tool_call, gadget.tool_list);
              }));
            })
            .push(function (client_tool_result_list) {
              var next_message_list = message_list, i, tool_call, client_tool_result, result_content;
              for (i = 0; i < pending_tool_call_list.length; i += 1) {
                tool_call = pending_tool_call_list[i];
                client_tool_result = client_tool_result_list[i];
                result_content = 'args:' + (tool_call.function.arguments ? tool_call.function.arguments : '') + '\n' + 'result:' + client_tool_result.content;
                next_message_list = next_message_list.concat([{
                  role: "tool",
                  tool_call_id: tool_call.id,
                  name: tool_call.function.name,
                  content: truncateToolOutput(result_content),
                  sub_message_list: client_tool_result.message_list
                }]);
                tool_message_list.push({
                  name: tool_call.function.name,
                  content: result_content,
                  sub_message_list: client_tool_result.message_list,
                  'role': 'tole'
                });
              }
              return RSVP.all([
                next_message_list,
                gadget.gadget_chat_ui.showMessage({tool_message_list: tool_message_list })
              ]);
            })
            .push(function (resulit_list) {
              return loop_call(
                loop_count + 1,
                resulit_list[0],
                null
              );
            });
          return;
        }

        queue_loop
          .push(function () {
            return gadget.requestProcessTask(
              gadget.options.jio_key,
              {
                message_list: JSON.stringify(message_list),
                tool_definition_list: JSON.stringify(tool_definition_list),
                initial_message_length: initial_message_length
              }
            );
          })
          .push(function (result) {
            if (result.tool_calls && result.tool_calls.length) {
              tool_message_list.push({
                'role': 'assistant',
                'content': result.content
              })
              return gadget.gadget_chat_ui.showMessage({tool_message_list: tool_message_list })
                .push(function () {
                 return loop_call(
                   loop_count + 1,
                   message_list.concat([{
                    role: "assistant",
                    content: result.content,
                    tool_calls: result.tool_calls
                  }]),
                  result.tool_calls
                );
              });
            }
            return RSVP.all([
              gadget.gadget_chat_ui.showMessage({ content: result.content , tool_message_list: tool_message_list }),
              gadget.notifySubmitted({message: 'Completed', status: "success"}),
              gadget.gadget_chat_ui.resetEditor(),
              gadget.storeTaskResult(
                gadget.options.jio_key,
                {
                  message_list: JSON.stringify(message_list.slice(initial_message_length).concat([result])),
                  content: result.content
                }
              )
            ]);
          });
      }

      queue_loop
        .push(function () {
          return gadget.gadget_chat_ui.blockEditor();
        })
        .push(function () {
          return gadget.notifySubmitted({message: 'Processing', status: "success"});
        })
        .push(function () {
          return gadget.gadget_chat_ui.getMessageList();
        })
        .push(function (message_list) {
          return RSVP.all([
            gadget.gadget_chat_ui.showMessage({}),
            gadget.compactMessageList(message_list)
          ]);
        })
        .push(function (result_list) {
          // XXXXXX seems bad to do locally
          var message_list = result_list[1],
            last_comment = message_list[message_list.length - 1].content,
            skill_list = window.ChatSkills.matchSkillList(last_comment),
            skill_message_list = (skill_list || []).map(function (skill) {
              return { role: "system", content: skill.instructions };
            });
          message_list = skill_message_list.concat(message_list);
          initial_message_length = message_list.length;
          return loop_call(0, message_list);
        });
      return queue_loop;
    });
}(window, rJS, RSVP));
