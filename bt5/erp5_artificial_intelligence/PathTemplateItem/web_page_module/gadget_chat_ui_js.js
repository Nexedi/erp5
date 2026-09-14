/*global window, rJS, RSVP, domsugar, marked, URI, jIO */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, marked) {
  "use strict";


  marked.setOptions({breaks: true});

  function formatPost(post) {
    var date = new Date(post.date);
    post.date_formatted = date.toLocaleString();
    post.date_relative = date.toLocaleString();
    return post;
  }

  function getPostDom(post, translationAttachment) {
    var content_element = post.response ?
        domsugar("div", [
        domsugar("div", { "class": "post-markdown", html: marked.parse(post.text) }),
        domsugar("pre", { "class": "chat-hidden-field" }, [post.text])
      ]) :
        domsugar("div", [domsugar("pre", [post.text])]),
        dom_list = [
        content_element
      ];
    if (post.attachment_link) {
      dom_list.push(domsugar("strong", [translationAttachment]));
      dom_list.push(domsugar("a", { href: post.attachment_link }, [post.attachment_name]));
    }
    return domsugar("li", {
      "class": post.response ? "post-answer" : "post-question"
    }, dom_list);
  }

  function getTypingIndicatorDom() {
    return domsugar("span", { "class": "chat-typing-indicator" }, [
      domsugar("span"),
      domsugar("span"),
      domsugar("span")
    ]);
  }

  function getAssistantMessageDiv(assistant_message) {
    return domsugar("div", { "class": "post-tool-entry post-assistant-entry" }, [
      domsugar("strong", ["Assistant"]),
      domsugar("br"),
      assistant_message.content || ""
    ]);
  }

  function getToolCallDiv(tool_message) {
    return domsugar("div", { "class": "post-tool-entry" }, [
      domsugar("strong", ["Tool: " + tool_message.name]),
      domsugar("br"),
      domsugar("div", { "class": "post-markdown", html: marked.parse(tool_message.content || "") })
    ]);
  }

  function getAgentMessageDiv(agent_message) {
    return agent_message.role === "assistant" ?
      getAssistantMessageDiv(agent_message) :
      getToolCallDiv(agent_message);
  }

  function getToolCallSummaryText(count) {
    return "Tool calls (" + count + ")";
  }

  function getToolCallDom(tool_message_list, details_open) {
    if (!tool_message_list || !tool_message_list.length) {
      return;
    }
    return domsugar("li", { "class": "post-tool" }, [
      domsugar("details", details_open ? { open: "open" } : {}, [
        domsugar("summary", [getToolCallSummaryText(tool_message_list.length)])
      ].concat(tool_message_list.map(getAgentMessageDiv)))
    ]);
  }

  rJS(window)
    .declareAcquiredMethod("translate", "translate")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("notifyCommentPosted", "notifyCommentPosted")
    .declareAcquiredMethod("getCommentPostList", "getCommentPostList")
    .declareAcquiredMethod("postComment", "postComment")

    .declareMethod('render', function (options) {
      var gadget = this;
      gadget.options = options;
      return gadget.declareGadget(options.editor_options.editor, {
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
              gadget.getCommentPostList(gadget.options.jio_key),
              gadget.translate("Attachment:")
            ]);
          })
          .push(
            function (post_list_and_translation) {
              var post_list = post_list_and_translation[0].map(formatPost),
                translationAttachment = post_list_and_translation[1][1];
              return post_list.map(function (post) {
                var tool_call_dom = getToolCallDom(JSON.parse(post.tool_message_list || "[]"), false),
                  post_dom;
                post_dom = getPostDom(post, translationAttachment);
                if (tool_call_dom) {
                  post_dom.appendChild(tool_call_dom);
                }
                return post_dom;
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
      return queue;
    })
    .declareMethod('appendPost', function (post) {
      var gadget = this,
        post_list_element = gadget.element.querySelector("#post_list"),
        dom = getPostDom(formatPost(post));
      post_list_element.appendChild(dom);
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
    .declareMethod('blockEditor', function () {
      return this.changeState({
        allow_submit: false,
        editor_state: 'pending'
      });
    })
    .declareMethod('resetEditor', function () {
      return this.changeState({
        allow_submit: true,
        editor_state: 'initialise'
      });
    })
    .declareMethod('showMessage', function (message) {
      var gadget = this,
        tool_message_list = message.tool_message_list || [],
        post_tool,
        details_open,
        tool_call_element,
        markdown_element;
      if (!gadget.new_message_element) {
        gadget.new_message_element = getPostDom(formatPost({
          date: new Date().toISOString(),
          text: "",
          response: true
        }));
        gadget.element.querySelector("#post_list").appendChild(gadget.new_message_element);
      }
      markdown_element = gadget.new_message_element.querySelector(".post-markdown");
      if (message.hasOwnProperty('content') && message.content) {
        details_open = false;
        markdown_element.innerHTML = marked.parse(message.content);
        gadget.new_message_element.querySelector('pre.chat-hidden-field').innerHTML = message.content;
      } else {
        details_open = true;
        markdown_element.innerHTML = "";
        markdown_element.appendChild(getTypingIndicatorDom());
      }
      if (tool_message_list.length) {
        tool_call_element = getToolCallDom(tool_message_list, details_open);
        post_tool  = gadget.new_message_element.querySelector('.post-tool');
        if (post_tool) {
          gadget.new_message_element.removeChild(post_tool);
        }
        gadget.new_message_element.appendChild(tool_call_element);
      }
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
              });
          }
          queue = gadget.changeState({
            allow_submit: false,
            editor_state: 'posting'
          })
            .push(function () {
              var choose_file_html_element = gadget.element.querySelector('#attachment'),
                file_blob = choose_file_html_element.files[0],
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
                  return gadget.postComment(
                    gadget.options.jio_key,
                    form_data_json
                  );
                })
                .push(function (evt) {
                  var location = evt.target.getResponseHeader("X-Location"),
                    uri,
                    redirect_jio_key;
                  gadget.new_message_element = null;
                  if (location) {
                    uri = new URI(location);
                    redirect_jio_key = uri.segment(2);
                  }
                  if (redirect_jio_key && (gadget.options.jio_key != redirect_jio_key)) {
                    return gadget.redirect({
                      command: 'display',
                      options: {
                        "jio_key": redirect_jio_key
                      }
                    });
                  }
                  return gadget.changeState({
                    editor_state: 'initialise',
                    allow_submit: true
                  })
                    .push(function () {
                      return gadget.notifyCommentPosted();
                    });
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
    .onEvent('submit', function () {
      return this.submitPostComment();
    });
}(window, rJS, RSVP, marked));
