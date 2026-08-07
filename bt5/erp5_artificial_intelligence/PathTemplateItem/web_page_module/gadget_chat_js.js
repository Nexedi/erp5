/*global window, rJS, RSVP, calculatePageTitle, FormData, URI, jIO */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, calculatePageTitle) {
  "use strict";

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
      gadget.tool_list = window.ChatTools.createToolList(
        gadget.element.querySelector("#drawing-canvas")
      );
      gadget.remote_tool_definition_list = (options.tool_list || []).map(
        function (tool) {
          return typeof tool === "string" ? JSON.parse(tool) : tool;
        }
      );
      return gadget.changeState(options);
    })
    .allowPublicAcquisition('notifySubmit', function notifySubmit(e) {
      return this.submitPostComment(e);
    })
    .onStateChange(function () {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return gadget.getTranslationList([
            "Comments:",
            "Post Comment"
          ]);
        })
        .push(function (translation_list) {
            var element = gadget.element.querySelector('input[type="submit"]');
            gadget.element.querySelector("[data-i18n='Comments:']").innerText = translation_list[0];
            gadget.element.querySelector("[data-i18n='Post Comment']").innerText = "\u00A0" + translation_list[1];
            gadget.element.querySelector("[data-i18n='[value]Post Comment']").value = translation_list[1];
            element.removeAttribute('disabled');
            element.classList.remove('ui-disabled');
            return gadget.renderCommentList();
          });
    })
    .declareMethod('renderCommentList', function () {
      var gadget = this;
      return gadget.getDeclaredGadget("editor")
        .push(function (editor) {
          return editor.render(gadget.options.editor_options);
        })
        .push(function () {
          return RSVP.all([
            gadget.jio_getAttachment(
              gadget.options.request_options.document_id,
              gadget.options.request_options.get_url
            ),
            gadget.getTranslationList(["By", "Attachment:"])
          ]);
        })
        .push(
          function (post_list_and_translation_list) {
            var post_list = post_list_and_translation_list[0],
              translationBy = post_list_and_translation_list[1][0],
              translationAttachment = post_list_and_translation_list[1][1];
            function getPostWithLinkAndLocalDate(post) {
              var date = new Date(post.date);
              post.date_formatted = date.toLocaleString();
              post.date_relative = date.toLocaleString();
              return post;
            }

            return RSVP.all(post_list.map(getPostWithLinkAndLocalDate))
            .then(function (post_list) {
              function getPostDomList(post) {
                var dom_list = [
                  translationBy + " ",
                  domsugar("strong", [post.user]),
                  " - ",
                  domsugar("time", {
                    datetime: post.date,
                    title: post.date_formatted
                  },
                    [post.date_relative]
                  ),
                  domsugar("br"),
                  domsugar("div", {
                    'data-gadget-html-viewer-value': post.text
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
              return post_list.map(getPostDomList);
            });
        })
        .push(function (dom_list) {
          return gadget.getElement()
            .push(function (element) {
              var all_dom_list = [], gadget_list = [], element_list, i, element;
              for (var i = 0; i < dom_list.length; i += 1) {
                all_dom_list = all_dom_list.concat(dom_list[i]);
              }
              domsugar(element.querySelector("#post_list"), all_dom_list);

              // make gadget html viewer for each post
              element_list = element.querySelector("#post_list").querySelectorAll('[data-gadget-html-viewer-value]');
              for (i = 0; i < element_list.length; i += 1) {
                gadget_list.push(
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

              return RSVP.all(gadget_list);
            });
        });
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

          submitButton = gadget.element.querySelector("input[type=submit]");
          submitButton.disabled = true;
          submitButton.classList.add("ui-disabled");

          function enableSubmitButton() {
            submitButton.disabled = false;
            submitButton.classList.remove("ui-disabled");
          }
          queue = gadget.translate("Posting comment").
            push(function (message_posting_comment) {
              return gadget.notifySubmitted({message: message_posting_comment})
            })
            .push(function () {
              var choose_file_html_element = gadget.element.querySelector('#attachment'),
                file_blob = choose_file_html_element.files[0],
                url = gadget.options.request_options.post_url,
                comment_text = content.comment,
                skill_list = window.ChatSkills.matchSkillList(comment_text),
                form_data_json = {};
              skill_list.forEach(function (skill) {
                comment_text = skill.instructions + "\n\n" + comment_text;
              });
              form_data_json.data = comment_text || "";
              form_data_json.file = "";
              choose_file_html_element.value = "";

              return new RSVP.Queue()
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
                });
            })
            .push(function () {
              return new RSVP.Queue()
                .push(function () {
                  return gadget.notifySubmitted({message: 'processing', status: "success"});
                }).push(function () {
                  return gadget.renderCommentList();
                }).push(function () {
                  return gadget.processTask(20);
              });
            }, function (e) {
              enableSubmitButton();
              return gadget.notifySubmitted({message: "Error:" + e, status: "error"});
            });
          return queue;
        });
    })
    .declareJob('processTask', function (max_loop_count) {
      var gadget = this,
        queue_loop = new RSVP.Queue(),
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

      function loop_call(loop_count, report_path, pending_tool_call_list) {
        var has_tool_call = Boolean(
            pending_tool_call_list && pending_tool_call_list.length
          ),
          tool_call = has_tool_call ? pending_tool_call_list[0] : null,
          request_json;
        if (loop_count >= max_loop_count) {
          throw new Error("processTask: too many iterations");
        }
        if (tool_call) {
          request_json = {
            report_path: report_path,
            tool_call: JSON.stringify(tool_call),
            client_tool_result: findClientTool(tool_call.function.name) ?
              JSON.stringify(runClientToolCall(tool_call)) : undefined
          };
        } else {
          request_json = {
            report_path: report_path,
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
              next_pending_tool_call_list;
            if (has_tool_call) {
              next_pending_tool_call_list = pending_tool_call_list.slice(1);
            } else if (result.pending_tool_call_list &&
                result.pending_tool_call_list.length) {
              next_pending_tool_call_list = result.pending_tool_call_list;
            } else {
              return gadget.notifySubmitted({message: 'end', status: "success"})
                .push(function () {
                  //return gadget.redirect({command: 'reload'});
                  return gadget.renderCommentList();
              });
            }
            return loop_call(
              loop_count + 1,
              result.report_path,
              next_pending_tool_call_list
            );
          });
      }

      loop_call(0);
      return queue_loop;
    })
    .onEvent('submit', function () {
      return this.submitPostComment();
    });
}(window, rJS, RSVP, calculatePageTitle));
