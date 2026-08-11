/*global window, rJS, RSVP, calculatePageTitle, FormData, URI, jIO, domsugar */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, calculatePageTitle) {
  "use strict";

  function formatPost(post) {
    var date = new Date(post.date);
    post.date_formatted = date.toLocaleString();
    post.date_relative = date.toLocaleString();
    return post;
  }

  function escapeHtml(text) {
    return String(text)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  function preformat(text) {
    return "<pre>" + escapeHtml(text) + "</pre>";
  }

  function getPostDomList(post, translationAttachment) {
    var dom_list = [
      domsugar("strong", [post.user]),
      domsugar("time", {
        datetime: post.date,
        title: post.date_formatted
      },
        [post.date_relative]
      ),
      domsugar("br"),
      domsugar("div", {
        'data-gadget-html-viewer-value': preformat(post.text)
      })
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

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("translate", "translate")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("getTranslationList", "getTranslationList")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")
    .declareAcquiredMethod("redirect", "redirect")

    .declareMethod('render', function (options) {
      var gadget = this;
      gadget.options = options;
      gadget.tool_list = window.ChatTools.createToolList(gadget.element);
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
        return gadget.getTranslationList([
            "Comments:",
            "Post Comment"
          ]);
        })
      .push(function (translation_list) {
        var element = gadget.element.querySelector('input[type="submit"]');
        gadget.element.querySelector("[data-i18n='Comments:']").innerText = translation_list[0];
        gadget.element.querySelector("[data-i18n='[value]Post Comment']").value = translation_list[1];
        element.removeAttribute('disabled');
        element.classList.remove('ui-disabled');
        return gadget.changeState({
          'render_editor': true,
          'allow_submit': true,
          'render_comment': true
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
      if (modification_dict.hasOwnProperty("render_editor") && modification_dict.render_editor) {
        queue
          .push(function () {
            return gadget.getDeclaredGadget("editor");
          })
          .push(function (editor) {
            return editor.render(gadget.options.editor_options.options);
          });
      }
      if (modification_dict.hasOwnProperty("render_comment") && modification_dict.render_comment) {
        queue
          .push(function () {
            return RSVP.all([
              gadget.jio_getAttachment(
                gadget.options.request_options.document_id,
                gadget.options.request_options.get_url
              ),
              gadget.getTranslationList(["Attachment:"])
            ]);
          })
          .push(
            function (post_list_and_translation_list) {
              var post_list = post_list_and_translation_list[0].map(formatPost),
                translationAttachment = post_list_and_translation_list[1][1];
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
            return gadget.declarePostHtmlViewerList(
              post_list_element.querySelectorAll('[data-gadget-html-viewer-value]')
            );
         });
       }
    })
    .declareMethod('declarePostHtmlViewerList', function (element_list) {
      var gadget = this,
        call_list = [], i;
      for (i = 0; i < element_list.length; i += 1) {
        call_list.push(
          gadget.declareGadget("gadget_html_viewer.html", {
            element: element_list[i],
            scope: "html_viewer",
            sandbox: "public"
          })
            .push(function (g) {
              return g.render({ value: g.element.getAttribute("data-gadget-html-viewer-value") });
            })
        );
      }
      return RSVP.all(call_list);
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
        content_element = li.querySelector('[data-gadget-html-viewer-value]');
        message_list.push({
          role: li.classList.contains("post-answer") ? "assistant" : "user",
          content: content_element ?
            content_element.getAttribute('data-gadget-html-viewer-value') : ""
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
      return gadget.declarePostHtmlViewerList(
        dom_list[0].querySelectorAll('[data-gadget-html-viewer-value]')
      );
    })
    .declareJob('submitPostComment', function () {
      var gadget = this,
        submitButton = null,
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
          queue = gadget.translate("Posting comment")
            .push(function (message_posting_comment) {
              return RSVP.all([
                gadget.notifySubmitted({message: message_posting_comment}),
                gadget.changeState({
                  allow_submit: false,
                  render_editor: false
                })
              ]);
            })
            .push(function () {
              var choose_file_html_element = gadget.element.querySelector('#attachment'),
                file_blob = choose_file_html_element.files[0],
                url = gadget.options.request_options.post_url,
                comment_text = content.comment,
                skill_list = window.ChatSkills.matchSkillList(comment_text).concat(
                  window.ChatSkills.matchSkillListFrom(comment_text, gadget.remote_skill_list)
                ),
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
                  return RSVP.all([
                    gadget.notifySubmitted({message: 'processing', status: "success"}),
                    gadget.appendPost(post)
                  ]);
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
                .push(function () {
                  return RSVP.all([
                    gadget.changeState({
                      render_editor: true
                    }),
                    gadget.processTask(20, skill_list)
                  ]);
                });
            }, function (e) {
               return RSVP.all([
                 gadget.changeState({allow_submit: true}),
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
        tool_definition_list = gadget.tool_list.map(function (tool) {
          return { type: "function", "function": tool.definition };
        }).concat(gadget.remote_tool_definition_list);

      function findClientTool(name) {
        var i;
        for (i = 0; i < gadget.tool_list.length; i += 1) {
          if (gadget.tool_list[i].definition.name === name) {
            return gadget.tool_list[i];
          }
        }
        return null;
      }

      function runClientToolCall(tool_call) {
        var tool = findClientTool(tool_call.function.name),
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
        } else {
          try {
            result = tool.execute(args);
          } catch (e) {
            result = "Error running tool \"" + tool_call.function.name + "\": " + e.message;
          }
        }
        return {
          tool_call_id: tool_call.id,
          name: tool_call.function.name,
          content: typeof result === "string" ? result : JSON.stringify(result)
        };
      }

      function showToolCallResult(name, content) {
        var post_list_element = gadget.element.querySelector("#post_list");
        if (!tool_li) {
          tool_summary = domsugar("summary", [getToolCallSummaryText(0)]);
          tool_details = domsugar("details", {}, [tool_summary]);
          tool_li = domsugar("li", { "class": "post-tool" }, [tool_details]);
          post_list_element.appendChild(tool_li);
          //post_list_element.appendChild(domsugar("hr"));
        }
        tool_count += 1;
        tool_summary.textContent = getToolCallSummaryText(tool_count);
        tool_details.appendChild(getToolCallDiv({ name: name, content: content }));
      }

      function loop_call(loop_count, message_list, pending_tool_call_list) {
        var has_tool_call = Boolean(
            pending_tool_call_list && pending_tool_call_list.length
          ),
          tool_call = has_tool_call ? pending_tool_call_list[0] : null,
          client_tool = tool_call ? findClientTool(tool_call.function.name) : null,
          request_json;
        if (loop_count >= max_loop_count) {
          throw new Error("processTask: too many iterations");
        }

        if (tool_call && client_tool) {
          queue_loop
            .push(function () {
              return runClientToolCall(tool_call);
          })
           .push(function (client_tool_result) {
             var next_client_message_list = message_list.concat([{
               role: "tool",
               tool_call_id: tool_call.id,
               name: tool_call.function.name,
               content: client_tool_result.content
             }]);
            showToolCallResult(tool_call.function.name, client_tool_result.content);
            return loop_call(
              loop_count + 1,
              next_client_message_list,
              pending_tool_call_list.slice(1)
            );
          });
          return;
        }

        if (tool_call) {
          request_json = {
            tool_call: JSON.stringify(tool_call)
          };
        } else {
          request_json = {
            message_list: JSON.stringify(message_list),
            tool_definition_list: JSON.stringify(tool_definition_list)
          };
        }
        queue_loop
          .push(function () {
            return gadget.jio_putAttachment(
              gadget.options.request_options.document_id,
              gadget.options.request_options.process_url,
              request_json
            );
          })
          .push(function (evt) {
            return jIO.util.readBlobAsText(evt.target.response);
          })
          .push(function (text_evt) {
            var result = JSON.parse(text_evt.target.result),
              next_message_list,
              next_pending_tool_call_list;
            if (has_tool_call) {
              next_message_list = message_list.concat([{
                role: "tool",
                tool_call_id: tool_call.id,
                name: tool_call.function.name,
                content: result.content
              }]);
              next_pending_tool_call_list = pending_tool_call_list.slice(1);
              showToolCallResult(tool_call.function.name, result.content);
              return loop_call(
                loop_count + 1,
                next_message_list,
                next_pending_tool_call_list
              );
            }
            if (result.tool_calls && result.tool_calls.length) {
              next_message_list = message_list.concat([{
                role: "assistant",
                content: result.content,
                tool_calls: result.tool_calls
              }]);
              next_pending_tool_call_list = result.tool_calls;
              return loop_call(
                loop_count + 1,
                next_message_list,
                next_pending_tool_call_list
              );
            }

            return gadget.notifySubmitted({message: 'end', status: "success"})
              .push(function () {
                return gadget.appendPost(result.post);
              })
              .push(function () {
                return gadget.changeState({
                  allow_submit: true
                });
              });
          });
      }

      queue_loop
        .push(function () {
          return gadget.getMessageList();
        })
        .push(function (message_list) {
          var skill_message_list = (skill_list || []).map(function (skill) {
            return { role: "system", content: skill.instructions };
          });
          return loop_call(0, skill_message_list.concat(message_list));
        });
      return queue_loop;
    })
    .onEvent('submit', function () {
      return this.submitPostComment();
    });
}(window, rJS, RSVP, calculatePageTitle));
