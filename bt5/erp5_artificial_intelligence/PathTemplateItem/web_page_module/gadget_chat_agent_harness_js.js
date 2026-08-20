/*global window, rJS, RSVP, FormData, jIO, fetch, TextDecoder, AbortController */
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

  //XXX is it correct ?
  function fetchStream(url, options, onDelta) {
    var controller = new AbortController();
    return new RSVP.Promise(function (resolve, reject) {
      var decoder = new TextDecoder("utf-8"),
        buffer = "",
        final_chunk = null;

      function handleLine(line) {
        var chunk = JSON.parse(line);
        if (chunk.type === "delta") {
          onDelta(chunk.content);
        } else {
          final_chunk = chunk;
        }
      }

      function readNext(reader) {
        reader.read().then(function (step) {
          var lines, i, line;
          if (step.done) {
            line = buffer.trim();
            buffer = "";
            if (line) {
              handleLine(line);
            }
            if (final_chunk) {
              return resolve(final_chunk);
            }
            return reject(new Error("processTask: LLM stream ended without a final chunk"));
          }
          buffer += decoder.decode(step.value, { stream: true });
          lines = buffer.split("\n");
          buffer = lines.pop();
          for (i = 0; i < lines.length; i += 1) {
            line = lines[i].trim();
            if (line) {
              handleLine(line);
            }
          }
          return readNext(reader);
        }, reject);
      }

      fetch(url, {
        method: options.method,
        credentials: options.credentials,
        body: options.body,
        signal: controller.signal
      })
        .then(function (response) {
          if (!response.ok) {
            throw new Error("processTask: LLM call failed with status " + response.status);
          }
          return readNext(response.body.getReader());
        })
        .then(null, reject);
    }, function () {
      controller.abort();
    });
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
          return gadget_chat_ui.render(options);
        })
        .push(function () {
          gadget.element.setAttribute('data-chat-state', options.chat_state);
          if (options.chat_state === 'not_yet_responded') {
            return gadget.processTask(200);
          }
        });
    })
    .allowPublicAcquisition('notifyCommentPosted', function () {
      var gadget = this;
      gadget.element.setAttribute('data-chat-state', 'not_yet_responded');
      return gadget.processTask(200);
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
    .declareJob('processTask', function (max_loop_count) {
      var gadget = this,
        gadget_chat_ui,
        queue_loop = new RSVP.Queue(),
        tool_definition_list = gadget.tool_list.map(function (tool) {
          return { type: "function", "function": tool.definition };
        }).concat(gadget.remote_tool_definition_list),
        running_tool_message_list = [];

      function loop_call(loop_count, message_list, pending_tool_call_list) {
        var has_tool_call = Boolean(
            pending_tool_call_list && pending_tool_call_list.length
          ),
          tool_call = has_tool_call ? pending_tool_call_list[0] : null,
          client_tool = tool_call ? findClientTool(tool_call.function.name, gadget.tool_list) : null;
        if (loop_count >= max_loop_count) {
          throw new Error("processTask: too many iterations");
        }
        if (tool_call) {
          gadget.element.setAttribute('data-chat-state', 'tool-running');
          if (client_tool) {
            queue_loop
              .push(function () {
                return runClientToolCall(tool_call, gadget.tool_list);
            })
             .push(function (client_tool_result) {
               var result_content = 'args:' + (tool_call.function.arguments ? tool_call.function.arguments: '') + '\n' + 'result:' + client_tool_result.content,
                 tool_message = {
                   role: "tool",
                   tool_call_id: tool_call.id,
                   name: tool_call.function.name,
                   content: truncateToolOutput(result_content)
                 },
                 next_client_message_list = message_list.concat([tool_message]);
              running_tool_message_list = running_tool_message_list.concat([tool_message]);
              return gadget_chat_ui.showToolCallList(running_tool_message_list)
                .push(function () {
                  return loop_call(
                    loop_count + 1,
                    next_client_message_list,
                    pending_tool_call_list.slice(1)
                  );
                });
            });
          } else {
            queue_loop
              .push(function () {
                return gadget.jio_putAttachment(
                  gadget.options.request_options.document_id,
                  gadget.options.request_options.process_url,
                  { tool_call: JSON.stringify(tool_call) }
                );
              })
              .push(function (evt) {
                return jIO.util.readBlobAsText(evt.target.response);
              })
              .push(function (text_evt) {
                var result = JSON.parse(text_evt.target.result),
                  result_content = 'args:' + (tool_call.function.arguments  ? tool_call.function.arguments: '') + '\n' + 'result:' + result.content,
                  tool_message = {
                    role: "tool",
                    tool_call_id: tool_call.id,
                    name: tool_call.function.name,
                    content: truncateToolOutput(result_content)
                  },
                  next_message_list = message_list.concat([tool_message]);
                running_tool_message_list = running_tool_message_list.concat([tool_message]);
                return gadget_chat_ui.showToolCallList(running_tool_message_list)
                  .push(function () {
                    return loop_call(
                      loop_count + 1,
                      next_message_list,
                      pending_tool_call_list.slice(1)
                    );
                  });
              });
          }
          return;
        }
        gadget.element.setAttribute('data-chat-state', 'processing');
        queue_loop
          .push(function () {
            var form_data = new FormData();
            form_data.append("message_list", JSON.stringify(message_list));
            form_data.append("tool_definition_list", JSON.stringify(tool_definition_list));
            return fetchStream(
              gadget.options.request_options.process_url,
              { method: "POST", credentials: "same-origin", body: form_data },
              function (delta_content) {
                return gadget_chat_ui.appendStreamingDelta(delta_content);
              }
            );
          })
          .push(function (stream_result) {
            return gadget_chat_ui.finalizeStreamingContent(stream_result ? stream_result.content : '')
              .push(function () {
                if (stream_result.tool_calls && stream_result.tool_calls.length) {
                  return loop_call(
                    loop_count + 1,
                    message_list.concat([{
                      role: "assistant",
                      content: stream_result.content,
                      tool_calls: stream_result.tool_calls
                    }]),
                    stream_result.tool_calls
                  );
                }
                return gadget_chat_ui.getStreamingRawText()
                  .push(function (raw_text) {
                    stream_result.content = raw_text;
                    return gadget.jio_putAttachment(
                      gadget.options.request_options.document_id,
                      gadget.options.request_options.process_url,
                      {
                        message_list: JSON.stringify(message_list),
                        finalize_result: JSON.stringify(stream_result)
                      }
                    );
                  })
                  .push(function () {
                    return gadget.notifySubmitted({message: 'Completed', status: "success"});
                  })
                  .push(function () {
                    gadget.element.setAttribute('data-chat-state', 'responded');
                    return RSVP.all([
                      gadget_chat_ui.clearStreamingPreview(),
                      gadget_chat_ui.setAllowSubmit(true),
                      gadget_chat_ui.resetEditor()
                    ]);
                  });
              });
          });
      }
      queue_loop
        .push(function () {
          return gadget.notifySubmitted({message: 'Processing', status: "success"});
        })
        .push(function () {
          return gadget.getDeclaredGadget("gadget_chat_ui");
        })
        .push(function (result) {
          gadget_chat_ui = result;
          return gadget_chat_ui.getMessageList();
        })
        .push(function (message_list) {
          return gadget.compactMessageList(message_list);
        })
        .push(function (message_list) {
          // XXXXXX seems bad to do locally
          var last_comment = message_list[message_list.length - 1].content,
            skill_list = window.ChatSkills.matchSkillList(last_comment).concat(
              window.ChatSkills.matchSkillListFrom(last_comment, gadget.remote_skill_list)
            ),
            skill_message_list = (skill_list || []).map(function (skill) {
              return { role: "system", content: skill.instructions };
            });
          loop_call(0, skill_message_list.concat(message_list));
        });
      return queue_loop;
    });
}(window, rJS, RSVP));
