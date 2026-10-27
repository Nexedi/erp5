/*global window, rJS, RSVP, domsugar, marked, URI, jIO */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, marked) {
  "use strict";


  marked.setOptions({breaks: true});

  var COMMENT_POLL_INTERVAL = 3000,
    ATTACHMENT_TEXT_MAX_LENGTH = 5 * 1024 * 1024,
    ATTACHMENT_IMAGE_MAX_BYTES = 5 * 1024 * 1024;

  function parseDataUri(data_uri) {
    var match = /^data:([^;,]*)(?:;[^,]*)?,([\s\S]*)$/.exec(data_uri || "");
    return match ? { mime: match[1], base64: match[2] } : null;
  }

  function isImageMimeType(mime) {
    return (/^image\//).test(mime || "");
  }

  function isTextMimeType(mime) {
    return (/^text\//).test(mime || "") ||
      (/^application\/(json|xml|javascript|x-sh)$/).test(mime || "");
  }

  function base64ByteLength(base64) {
    var padding = (/={1,2}$/.exec(base64 || "") || [""])[0].length;
    return Math.floor((base64 || "").length * 3 / 4) - padding;
  }

  function decodeBase64ToText(base64) {
    var binary = window.atob(base64), bytes = new Uint8Array(binary.length), i;
    for (i = 0; i < binary.length; i += 1) {
      bytes[i] = binary.charCodeAt(i);
    }
    return new window.TextDecoder("utf-8", { fatal: false }).decode(bytes);
  }

  function getAttachmentContentPart(attachment_name, data_uri) {
    var parsed = parseDataUri(data_uri), text, truncated;
    if (!parsed) {
      return null;
    }
    if (isImageMimeType(parsed.mime)) {
      if (base64ByteLength(parsed.base64) > ATTACHMENT_IMAGE_MAX_BYTES) {
        return { type: "text", skipped: true, text: "[Attachment: " + attachment_name +
          " - image too large to send (" +
          Math.round(base64ByteLength(parsed.base64) / 1024) + "KB), skipped]" };
      }
      return { type: "image_url", image_url: { url: data_uri } };
    }
    if (isTextMimeType(parsed.mime)) {
      text = decodeBase64ToText(parsed.base64);
      truncated = text.length > ATTACHMENT_TEXT_MAX_LENGTH;
      return { type: "text", text: "[Attachment: " + attachment_name + "]\n" +
        text.slice(0, ATTACHMENT_TEXT_MAX_LENGTH) + (truncated ? "\n[... truncated ...]" : "") };
    }
    if (parsed.mime === "application/pdf") {
      return { type: "text", skipped: true, text: "[Attachment: " + attachment_name +
        " - a PDF, not sent inline. Call the pdf_to_text tool with file_name=\"" + attachment_name +
        "\" to read its text content]" };
    }
    return { type: "text", skipped: true, text: "[Attachment: " + attachment_name + " (" +
      (parsed.mime || "unknown type") + ") - not shown, unsupported type]" };
  }

  function formatPost(post) {
    var date = new Date(post.date);
    post.date_formatted = date.toLocaleString();
    post.date_relative = date.toLocaleString();
    return post;
  }

  function getPostDom(post) {
    var content_element = post.response ?
        domsugar("div", [
        domsugar("div", { "class": "post-markdown", html: marked.parse(post.text) }),
        domsugar("pre", { "class": "chat-hidden-field" }, [post.text])
      ]) :
        domsugar("div", [domsugar("pre", [post.text])]),
        dom_list = [
        content_element
      ],
      attachment_children,
      attachment_part;
    if (post.attachment_link) {
      attachment_children = [
        domsugar("a", { href: post.attachment_link, download: post.attachment_name }, [post.attachment_name])
      ];
      attachment_part = getAttachmentContentPart(post.attachment_name, post.attachment_link);
      if (attachment_part && attachment_part.skipped) {
        attachment_children.push(domsugar("span", { "class": "post-attachment-warning" }, [attachment_part.text]));
      }
      dom_list.push(domsugar("div", { "class": "post-attachment" }, attachment_children));
    }
    dom_list.push(domsugar("time", { datetime: post.date, title: post.date }, [
      (post.response && post.author_title) ? (post.author_title + " · " + post.date_formatted) : post.date_formatted
    ]));
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
      domsugar("div", { "class": "post-tool-content" }, [assistant_message.content || ""])
    ]);
  }

  function getSubMessageDiv(sub_message) {
    var label = sub_message.role === "tool" ?
        ("Tool: " + sub_message.name) :
        (sub_message.role === "assistant" ? "Assistant" : "Task");
    return domsugar("div", { "class": "post-tool-entry post-tool-sub-entry" }, [
      domsugar("strong", [label]),
      domsugar("br"),
      domsugar("div", { "class": "post-markdown post-tool-content", html: marked.parse(sub_message.content || "") })
    ]);
  }

  function getToolCallDiv(tool_message) {
    var dom_list = [
      domsugar("strong", ["Tool: " + tool_message.name]),
      domsugar("br"),
      domsugar("div", { "class": "post-markdown post-tool-content", html: marked.parse(tool_message.content || "") })
    ];
    if (tool_message.sub_message_list && tool_message.sub_message_list.length) {
      dom_list.push(domsugar("details", { "class": "post-tool-sub-list" }, [
        domsugar("summary", ["Sub-agent trace (" + tool_message.sub_message_list.length + ")"])
      ].concat(tool_message.sub_message_list.map(getSubMessageDiv))));
    }
    return domsugar("div", { "class": "post-tool-entry" }, dom_list);
  }

  function getAgentMessageDiv(agent_message) {
    return agent_message.role === "assistant" ?
      getAssistantMessageDiv(agent_message) :
      getToolCallDiv(agent_message);
  }

  function getToolCallSummaryText(count) {
    return "Tool calls (" + count + ")";
  }

  var EXECUTION_PLAN_STATUS_ICON = {
    pending: "☐",
    in_progress: "⟳",
    done: "☑",
    failed: "✗",
    skipped: "⊘"
  };

  function getExecutionPlanStepListDom(step_list) {
    return domsugar("ol", { "class": "execution-plan-step-list" }, step_list.map(function (step) {
      var li_children = [
        domsugar("span", { "class": "execution-plan-step-status" }, [EXECUTION_PLAN_STATUS_ICON[step.status] || EXECUTION_PLAN_STATUS_ICON.pending]),
        domsugar("span", { "class": "execution-plan-step-title" }, [step.title])
      ];
      if (step.note) {
        li_children.push(domsugar("div", { "class": "execution-plan-step-note" }, [step.note]));
      }
      return domsugar("li", { "class": "execution-plan-step execution-plan-step-" + step.status }, li_children);
    }));
  }

  function getExecutionPlanDom(plan) {
    if (!plan || !plan.step_list || !plan.step_list.length) {
      return null;
    }
    return domsugar("div", { "class": "execution-plan" }, [
      domsugar("strong", { "class": "execution-plan-goal" }, ["Plan: " + (plan.goal || "")]),
      getExecutionPlanStepListDom(plan.step_list)
    ]);
  }

  function appendPlanAndToolDom(post_dom, post) {
    var plan_dom = getExecutionPlanDom(post.execution_plan ? JSON.parse(post.execution_plan) : null),
      tool_call_dom = getToolCallDom(JSON.parse(post.tool_message_list || "[]"), false);
    if (plan_dom) {
      post_dom.appendChild(plan_dom);
    }
    if (tool_call_dom) {
      post_dom.appendChild(tool_call_dom);
    }
    return post_dom;
  }

  // Live refresh of the in-progress message bubble's plan while a turn is
  // still running (before it has its own stored snapshot) - mirrors how the
  // tool-call list is appended to incrementally in showMessage below.
  function refreshMessageExecutionPlan(message_element, plan) {
    var old_plan_element = message_element.querySelector('.execution-plan'),
      new_plan_dom = getExecutionPlanDom(plan),
      reference_node;
    if (old_plan_element) {
      old_plan_element.parentNode.removeChild(old_plan_element);
    }
    if (new_plan_dom) {
      reference_node = message_element.querySelector('.post-tool') || message_element.querySelector('time');
      message_element.insertBefore(new_plan_dom, reference_node || null);
    }
  }

  function getToolCallDom(tool_message_list, details_open) {
    var details_attr;
    if (!tool_message_list || !tool_message_list.length) {
      return;
    }
    details_attr = details_open ? { open: "open", "class": "post-tool-pending" } : {};
    return domsugar("li", { "class": "post-tool" }, [
      domsugar("details", details_attr, [
        domsugar("summary", [getToolCallSummaryText(tool_message_list.length)])
      ].concat(tool_message_list.map(getAgentMessageDiv)))
    ]);
  }

  rJS(window)
    .declareAcquiredMethod("translate", "translate")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("notifyCommentPosted", "notifyCommentPosted")
    .declareAcquiredMethod("notifyCancelRequested", "notifyCancelRequested")
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
        var submitButton = gadget.element.querySelector("input[type=submit]"),
          cancelButton = gadget.element.querySelector("#cancel_button");
        if (modification_dict.allow_submit) {
          submitButton.disabled = false;
          submitButton.classList.remove("ui-disabled");
          cancelButton.style.display = "none";
        } else {
          submitButton.disabled = true;
          submitButton.classList.add("ui-disabled");
          cancelButton.style.display = gadget.options.enable_cancel ? "inline-block" : "none";
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
            return gadget.getCommentPostList(gadget.options.jio_key);
          })
          .push(
            function (post_list) {
              return post_list.map(formatPost).map(function (post) {
                return appendPlanAndToolDom(getPostDom(post), post);
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
    .onLoop(function () {
      var gadget = this;
      if (gadget.options.disable_comment_poll) {
        return;
      }
      return gadget.getCommentPostList(gadget.options.jio_key)
        .push(function (post_list) {
          return gadget.getMessageList()
            .push(function (rendered_list) {
              var new_post_list = post_list.slice(rendered_list.length);
              return new_post_list.reduce(function (sub_queue, post) {
                return sub_queue.push(function () {
                  return gadget.appendPost(post);
                });
              }, new RSVP.Queue());
            });
        });
    }, COMMENT_POLL_INTERVAL)
    .declareMethod('appendPost', function (post) {
      var gadget = this,
        post_list_element = gadget.element.querySelector("#post_list"),
        dom = appendPlanAndToolDom(getPostDom(formatPost(post)), post);
      post_list_element.appendChild(dom);
    })
    .declareMethod('getMessageList', function () {
      var gadget = this,
        li_list = gadget.element.querySelectorAll(
          "#post_list li.post-question, #post_list li.post-answer"
        ),
        message_list = [],
        i, li, content_element, attachment_element, content, attachment_part;
      for (i = 0; i < li_list.length; i += 1) {
        li = li_list[i];
        content_element = li.querySelector('pre.chat-hidden-field') || li.querySelector('pre');
        content = content_element ? content_element.textContent : "";
        attachment_element = li.querySelector('.post-attachment a');
        attachment_part = attachment_element ?
          getAttachmentContentPart(attachment_element.textContent, attachment_element.getAttribute('href')) :
          null;
        message_list.push({
          role: li.classList.contains("post-answer") ? "assistant" : "user",
          content: attachment_part ?
            (attachment_part.type === "image_url" ?
              [{ type: "text", text: content }, attachment_part] :
              content + "\n\n" + attachment_part.text) :
            content
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
      this.new_message_element = null;
      this.rendered_tool_message_count = 0;
      return this.changeState({
        allow_submit: true,
        editor_state: 'initialise'
      });
    })
    .declareMethod('showMessage', function (message) {
      var gadget = this,
        tool_message_list = message.tool_message_list || [],
        details_open,
        details_element,
        markdown_element,
        time_element,
        rendered_count,
        i;
      if (!gadget.new_message_element) {
        gadget.new_message_element = getPostDom(formatPost({
          date: new Date().toISOString(),
          text: "",
          response: true,
          author_title: message.author_title || "Assistant"
        }));
        gadget.rendered_tool_message_count = 0;
        gadget.element.querySelector("#post_list").appendChild(gadget.new_message_element);
      } else if (message.author_title) {
        time_element = gadget.new_message_element.querySelector("time");
        time_element.textContent = message.author_title + " · " +
          new Date(time_element.getAttribute("datetime")).toLocaleString();
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
        details_element = gadget.new_message_element.querySelector('.post-tool > details');
        rendered_count = gadget.rendered_tool_message_count || 0;
        if (!details_element) {
          gadget.new_message_element.appendChild(getToolCallDom(tool_message_list, details_open));
          gadget.rendered_tool_message_count = tool_message_list.length;
        } else {
          for (i = rendered_count; i < tool_message_list.length; i += 1) {
            details_element.appendChild(getAgentMessageDiv(tool_message_list[i]));
          }
          if (tool_message_list.length !== rendered_count) {
            details_element.querySelector('summary').textContent =
              getToolCallSummaryText(tool_message_list.length);
            gadget.rendered_tool_message_count = tool_message_list.length;
          }
          details_element.open = details_open;
          details_element.classList.toggle('post-tool-pending', details_open);
        }
      }
      if (message.hasOwnProperty('execution_plan')) {
        refreshMessageExecutionPlan(gadget.new_message_element, message.execution_plan);
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
                response: false,
                author_title: ""
              };

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
                    post.attachment_link = data_url_evt.target.result;
                    post.attachment_name = file_blob.name;
                  }
                  return gadget.appendPost(post);
                })
                .push(function () {
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
    })
    .onEvent('click', function (evt) {
      if (!evt.target || evt.target.id !== 'cancel_button') {
        return;
      }
      return this.notifyCancelRequested();
    }, false, false);
}(window, rJS, RSVP, marked));
