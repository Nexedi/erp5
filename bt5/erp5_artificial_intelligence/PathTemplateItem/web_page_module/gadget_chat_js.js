/*global window, rJS, RSVP, FormData, URI, jIO, domsugar, fetch, TextDecoder, AbortController, marked */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, marked) {
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

  function formatPost(post) {
    var date = new Date(post.date);
    post.date_formatted = date.toLocaleString();
    post.date_relative = date.toLocaleString();
    return post;
  }


  function getPostDomList(post, translationAttachment) {
    var content_element = post.response ?
        domsugar("div", [
          domsugar("div", { "class": "post-markdown", html: marked.parse(post.text) }),
          domsugar("pre", { "class": "chat-hidden-field" }, [post.text])
        ]) :
        domsugar("div", [domsugar("pre", [post.text])]),
      dom_list = [
      domsugar("strong", [post.user]),
      /*
      domsugar("time", {
        datetime: post.date,
        title: post.date_formatted
      },
        [post.date_relative]
      ),*/
      domsugar("br"),
      content_element
    ];
    if (post.attachment_link) {
      dom_list.push(domsugar("br"));
      dom_list.push(domsugar("strong", [translationAttachment]));
      dom_list.push(domsugar("a", { href: post.attachment_link }, [post.attachment_name]));
    }
    return [
      domsugar("li", {
        "class": post.response ? "post-answer" : "post-question"
      }, dom_list),
      domsugar("hr", { id: "post_item" })
    ];
  }

  function getToolCallDiv(tool_message) {
    return domsugar("div", { "class": "post-tool-entry" }, [
      domsugar("strong", ["Tool: " + tool_message.name]),
      domsugar("br"),
      tool_message.content
    ]);
  }

  function getToolCallSummaryText(count) {
    return "Tool calls (" + count + ")";
  }

  function getToolCallLiList(tool_message_list) {
    if (!tool_message_list.length) {
      return [];
    }
    return [
      domsugar("li", { "class": "post-tool" }, [
        domsugar("details", {}, [
          domsugar("summary", [getToolCallSummaryText(tool_message_list.length)])
        ].concat(tool_message_list.map(getToolCallDiv)))
      ])
      //domsugar("hr")
    ];
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
    .declareAcquiredMethod("translate", "translate")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")
    .declareAcquiredMethod("redirect", "redirect")

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
      return gadget.declareGadget(options.editor_options.editor,  {
        element: gadget.element.querySelector('.chat-editor'),
        scope: "editor",
        sandbox: "public"
      })
      .push(function () {
        return gadget.translate("Post Comment");
        })
      .push(function (translation) {
        gadget.element.querySelector("[data-i18n='[value]Post Comment']").value = translation;
        return gadget.changeState({
          'editor_state': 'initialise',
          'allow_submit': true,
          'render_comment': true ? gadget.options.request_options.get_url : false,
          'chat_state': gadget.options.chat_state
        });
      });
    })
    .allowPublicAcquisition('notifySubmit', function notifySubmit(e) {
      return this.submitPostComment(e);
    })
    .onStateChange(function (modification_dict) {
      var gadget = this,
        queue = new RSVP.Queue();
      if (modification_dict.hasOwnProperty("allow_submit")) {
        var submitButton = gadget.element.querySelector("input[type=submit]");
        if (modification_dict.allow_submit) {
          submitButton.disabled = false;
          submitButton.classList.remove("ui-disabled");
        } else {
          submitButton.disabled = true;
          submitButton.classList.add("ui-disabled");
        }
      }
      if (modification_dict.hasOwnProperty("editor_state")) {
        if (modification_dict.editor_state == 'initialise') {
          queue
            .push(function () {
              return gadget.getDeclaredGadget("editor");
            })
            .push(function (editor) {
              return editor.render(gadget.options.editor_options.options);
            });
        }
      }
      if (modification_dict.hasOwnProperty("render_comment") && modification_dict.render_comment) {
        queue
          .push(function () {
            return RSVP.all([
              gadget.jio_getAttachment(
                gadget.options.request_options.document_id,
                gadget.options.request_options.get_url
              ),
              gadget.translate("Attachment:")
            ]);
          })
          .push(
            function (post_list_and_translation) {
              var post_list = post_list_and_translation[0].map(formatPost),
                translationAttachment = post_list_and_translation[1][1];
              return post_list.map(function (post) {
                var tool_message_list = JSON.parse(post.report_text_content_list || "[]");
                return getToolCallLiList(tool_message_list)
                  .concat(getPostDomList(post, translationAttachment));
              });
          })
          .push(function (dom_list) {
            var all_dom_list = [], post_list_element, i;
            for (i = 0; i < dom_list.length; i += 1) {
              all_dom_list = all_dom_list.concat(dom_list[i]);
            }
            post_list_element = gadget.element.querySelector("#post_list");
            domsugar(post_list_element, all_dom_list);
         });
       }
      if (modification_dict.hasOwnProperty("chat_state") && modification_dict.chat_state == 'not_yet_responded') {
        queue
          .push(function () {
            return gadget.processTask(200);
        });
      }
      return queue;
    })
    .declareMethod('getMessageList', function () {
      var gadget = this,
        li_list = gadget.element.querySelectorAll(
          "#post_list li.post-question, #post_list li.post-answer"
        ),
        message_list = [],
        i, li, content_element;
      for (i = 0; i < li_list.length; i += 1) {
        li = li_list[i];
        content_element = li.querySelector('pre.chat-hidden-field') || li.querySelector('pre');
        message_list.push({
          role: li.classList.contains("post-answer") ? "assistant" : "user",
          content: content_element ? content_element.textContent : ""
        });
      }
      return message_list;
    })
    .declareMethod('appendPost', function (post) {
      var gadget = this,
        post_list_element = gadget.element.querySelector("#post_list"),
        dom_list = getPostDomList(formatPost(post));
      post_list_element.appendChild(dom_list[0]);
      post_list_element.appendChild(dom_list[1]);
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
    .declareJob('submitPostComment', function () {
      var gadget = this,
        queue = null;

      return gadget.getDeclaredGadget("editor")
        .push(function (e) {
          return e.getContent();
        })
        .push(function (content) {
          if (content.comment === '') {
            return gadget.translate("Post content can not be empty!")
                .push(function (translated_message) {
                  return gadget.notifySubmitted({message: translated_message});
                })
          }
          queue = gadget.changeState({
            allow_submit: false,
            editor_state: 'posting'
            })
            .push(function () {
              var choose_file_html_element = gadget.element.querySelector('#attachment'),
                file_blob = choose_file_html_element.files[0],
                url = gadget.options.request_options.post_url,
                comment_text = content.comment,
                form_data_json = {},
                post;
              form_data_json.data = comment_text || "";
              form_data_json.file = "";
              choose_file_html_element.value = "";

              post = {
                date: new Date().toISOString(),
                text: comment_text,
                response: false
              };

              return new RSVP.Queue()
                .push(function () {
                  return gadget.appendPost(post);
                })
                .push(function () {
                  if (file_blob) {
                    return jIO.util.readBlobAsDataURL(file_blob);
                  }
                })
                .push(function (data_url_evt) {
                  if (data_url_evt) {
                    form_data_json.file = {
                      url: data_url_evt.target.result,
                      file_name: file_blob.name
                    };
                  }
                  return gadget.jio_putAttachment(
                    gadget.options.request_options.document_id,
                    url,
                    form_data_json
                  );
                })
                .push(function (evt) {
                  var location = evt.target.getResponseHeader("X-Location"),
                    uri,
                    redirect_jio_key;
                  if (location) {
                    uri = new URI(location);
                    redirect_jio_key = uri.segment(2);
                  }
                  if (redirect_jio_key && (gadget.options.request_options.document_id != redirect_jio_key)) {
                    return gadget.redirect({
                      command: 'display',
                      options: {
                        "jio_key": redirect_jio_key
                      }
                    });
                  }
                  return RSVP.all([
                    gadget.changeState({
                      editor_state: 'initialise',
                      chat_state: 'not_yet_responded'
                    })
                  ]);
                });
            }, function (e) {
               return RSVP.all([
                 gadget.changeState({
                   allow_submit: true,
                   editor_state: 'initialise'
                 }),
                 gadget.notifySubmitted({message: "Error:" + e, status: "error"})
               ]);
            });
          return queue;
        });
    })
    .declareJob('processTask', function (max_loop_count, skill_list) {
      var gadget = this,
        queue_loop = new RSVP.Queue(),
        tool_li = null,
        tool_details = null,
        tool_summary = null,
        tool_count = 0,
        post_list = gadget.element.querySelector("#post_list"),
        streaming_element,
        content_element,
        tool_definition_list = gadget.tool_list.map(function (tool) {
          return { type: "function", "function": tool.definition };
        }).concat(gadget.remote_tool_definition_list);



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
          if (!tool_li) {
            tool_summary = domsugar("summary", [getToolCallSummaryText(0)]);
            tool_details = domsugar("details", {}, [tool_summary]);
            tool_li = domsugar("li", { "class": "post-tool" }, [tool_details]);
            post_list.appendChild(tool_li);
          }
          if (client_tool) {
            console.log('***************************** call browser tool cool');
            queue_loop
              .push(function () {
                return runClientToolCall(tool_call, gadget.tool_list);
            })
             .push(function (client_tool_result) {
               var result_content = 'args:' + (tool_call.function.arguments ? tool_call.function.arguments: '') + '\n' + 'result:' + client_tool_result.content,
                 next_client_message_list = message_list.concat([{
                 role: "tool",
                 tool_call_id: tool_call.id,
                 name: tool_call.function.name,
                 content: truncateToolOutput(result_content)
               }]);
              tool_count += 1;
              tool_summary.textContent = getToolCallSummaryText(tool_count);
              tool_details.appendChild(getToolCallDiv({ name: tool_call.function.name, content: result_content}));
              return loop_call(
                loop_count + 1,
                next_client_message_list,
                pending_tool_call_list.slice(1)
              );
            });
          } else {
            console.log('xxxxxxxxxxxxxxxxxxxxx call server tool cool');

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
                  next_message_list = message_list.concat([{
                    role: "tool",
                    tool_call_id: tool_call.id,
                    name: tool_call.function.name,
                    content: truncateToolOutput(result_content)
                  }]);
                tool_count += 1;
                tool_summary.textContent = getToolCallSummaryText(tool_count);
                tool_details.appendChild(getToolCallDiv({ name: tool_call.function.name, content: result_content }));
                return loop_call(
                  loop_count + 1,
                  next_message_list,
                  pending_tool_call_list.slice(1)
                );
              });
          }
          return;
        }

        queue_loop
          .push(function () {
            var form_data = new FormData(),
              raw_text = "";
            console.log('************************** call with llm');

            form_data.append("message_list", JSON.stringify(message_list));
            form_data.append("tool_definition_list", JSON.stringify(tool_definition_list));
            return fetchStream(
              gadget.options.request_options.process_url,
              { method: "POST", credentials: "same-origin", body: form_data },
              function (delta_content) {
                if (!content_element) {
                  streaming_element = getPostDomList(formatPost({
                    date: new Date().toISOString(),
                    text: "",
                    response: true
                  }));
                  post_list.appendChild(streaming_element[0]);
                  post_list.appendChild(streaming_element[1]);
                  content_element = streaming_element[0].querySelector(".post-markdown");
                }
                // seems a bad idea, bad performance
                raw_text += delta_content;
                content_element.innerHTML = marked.parse(streaming_element[0].querySelector('pre').innerHTML + raw_text);
              }
            );
          })
          .push(function (stream_result) {
            if (streaming_element) {
              streaming_element[0].querySelector('pre').innerHTML += stream_result? stream_result.content: '';
            }
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
            stream_result['content'] = streaming_element[0].querySelector('pre').innerHTML;
            return gadget.jio_putAttachment(
              gadget.options.request_options.document_id,
              gadget.options.request_options.process_url,
              {
                message_list: JSON.stringify(message_list),
                finalize_result: JSON.stringify(stream_result)
              })
              .push(function (evt) {
                console.log('no more tool call');
                return gadget.notifySubmitted({message: 'end', status: "success"})
                  .push(function () {
                    return gadget.changeState({
                      allow_submit: true,
                      chat_state: 'responded',
                      editor_state: 'initialise'
                    });
                  });
               });
          });
      }

      queue_loop
        .push(function () {
          return gadget.notifySubmitted({message: 'processing', status: "success"});
        })
        .push(function () {
          return gadget.getMessageList();
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
          return loop_call(0, skill_message_list.concat(message_list));
        });
      return queue_loop;
    })
    .onEvent('submit', function () {
      return this.submitPostComment();
    });
}(window, rJS, RSVP, marked));
