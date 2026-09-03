/*global window, rJS, RSVP, jIO */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  var COMPACT_THRESHOLD = 50,
    KEEP_RECENT = 20,
    MAX_TOOL_OUTPUT_LINES = 200;

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
        return {
          tool_call_id: tool_call.id,
          name: tool_call.function.name,
          content: typeof result === "string" ? result : JSON.stringify(result)
        };
      }, function (e) {
      result = "Error running tool \"" + tool_call.function.name + "\": " + e.message;
      return {
        tool_call_id: tool_call.id,
        name: tool_call.function.name,
        content: typeof result === "string" ? result : JSON.stringify(result)
      };
    });
  }

  rJS(window)
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")

    .declareMethod('render', function (options) {
      var gadget = this;
      gadget.options = options;
      gadget.tool_list = window.ChatTools.createToolList(gadget.element, options.hateoas_url);
      gadget.remote_tool_definition_list = (options.tool_list || []).map(
        function (tool) {
          return typeof tool === "string" ? JSON.parse(tool) : tool;
        }
      );
      gadget.remote_skill_list = (options.skill_list || []).map(
        function (skill) {
          return typeof skill === "string" ? JSON.parse(skill) : skill;
        }
      );
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

      return gadget.jio_putAttachment(
        gadget.options.request_options.document_id,
        gadget.options.request_options.process_url,
        { compact_message_list: JSON.stringify(old_message_list) }
      )
        .push(function (evt) {
          return jIO.util.readBlobAsText(evt.target.response);
        })
        .push(function (text_evt) {
          var result = JSON.parse(text_evt.target.result);
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
        total_text = "",
        tool_definition_list = gadget.tool_list.map(function (tool) {
          return { type: "function", "function": tool.definition };
        }).concat(gadget.remote_tool_definition_list);

      function loop_call(loop_count, message_list, pending_tool_call_list) {
        var has_tool_call = Boolean(
            pending_tool_call_list && pending_tool_call_list.length
          ),
          tool_call = has_tool_call ? pending_tool_call_list[0] : null;
        if (loop_count >= max_loop_count) {
          throw new Error("processTask: too many iterations");
        }

        if (tool_call) {
          queue_loop
            .push(function () {
              return runClientToolCall(tool_call, gadget.tool_list);
            })
            .push(function (client_tool_result) {
              var result_content = 'args:' + (tool_call.function.arguments ? tool_call.function.arguments : '') + '\n' + 'result:' + client_tool_result.content,
                next_message_list = message_list.concat([{
                  role: "tool",
                  tool_call_id: tool_call.id,
                  name: tool_call.function.name,
                  content: truncateToolOutput(result_content)
                }]);
              tool_message_list.push({ name: tool_call.function.name, content: result_content });
              return RSVP.all([
                next_message_list,
                gadget.gadget_chat_ui.showMessage({ content: total_text, tool_message_list: tool_message_list })
              ]);
            })
            .push(function (resulit_list) {
              return loop_call(
                loop_count + 1,
                resulit_list[0],
                pending_tool_call_list.slice(1)
              );
            });
          return;
        }

        queue_loop
          .push(function () {
            return gadget.jio_putAttachment(
              gadget.options.request_options.document_id,
              gadget.options.request_options.process_url,
              {
                message_list: JSON.stringify(message_list),
                tool_definition_list: JSON.stringify(tool_definition_list)
              }
            );
          })
          .push(function (evt) {
            return jIO.util.readBlobAsText(evt.target.response);
          })
          .push(function (text_evt) {
            var result = JSON.parse(text_evt.target.result);
            total_text += result.content || '';
            if (result.tool_calls && result.tool_calls.length) {
              return gadget.gadget_chat_ui.showMessage({ content: total_text , tool_message_list: tool_message_list })
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
              gadget.gadget_chat_ui.showMessage({ content: total_text , tool_message_list: tool_message_list }),
              gadget.notifySubmitted({message: 'Completed', status: "success"}),
              gadget.gadget_chat_ui.resetEditor()
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
            skill_list = window.ChatSkills.matchSkillList(last_comment).concat(
              window.ChatSkills.matchSkillListFrom(last_comment, gadget.remote_skill_list)
            ),
            skill_message_list = (skill_list || []).map(function (skill) {
              return { role: "system", content: skill.instructions };
            });
          return loop_call(0, skill_message_list.concat(message_list));
        });
      return queue_loop;
    });
}(window, rJS, RSVP));
