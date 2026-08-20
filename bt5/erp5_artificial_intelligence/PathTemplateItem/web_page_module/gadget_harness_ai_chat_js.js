/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  var POLL_INTERVAL = 1000;

  rJS(window)
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")

    .declareMethod('render', function (options) {
      var gadget = this;
      gadget.options = options;
      return gadget.getDeclaredGadget("gadget_chat_ui")
        .push(function (gadget_chat_ui) {
          gadget.gadget_chat_ui = gadget_chat_ui;
          return gadget_chat_ui.render(options);
        })
        .push(function () {
          gadget.element.setAttribute('data-chat-state', options.chat_state);
          if (options.chat_state === 'pending') {
            return gadget.pollTask();
          }
        });
    })
    .allowPublicAcquisition('notifyCommentPosted', function () {
      var gadget = this;
      gadget.element.setAttribute('data-chat-state', 'pending');
      return gadget.jio_putAttachment(
        gadget.options.request_options.document_id,
        gadget.options.request_options.process_url,
        {}
      )
        .push(function () {
          return gadget.pollTask();
        });
    })
    .declareJob('pollTask', function () {
      var gadget = this,
        gadget_chat_ui = gadget.gadget_chat_ui,
        queue_loop = new RSVP.Queue();

      function check() {
        queue_loop
          .push(function () {
            return gadget.jio_getAttachment(
              gadget.options.request_options.document_id,
              gadget.options.request_options.status_url
            );
          })
          .push(function (status) {
            gadget.element.setAttribute('data-chat-state', status.simulation_state);
            return new RSVP.Queue()
              .push(function () {
                if (status.tool_message_list && status.tool_message_list.length) {
                  return gadget_chat_ui.showToolCallList(status.tool_message_list);
                }
              })
              .push(function () {
                if (status.streaming_content) {
                  return gadget_chat_ui.showStreamingContent(status.streaming_content);
                }
              })
              .push(function () {
                if (status.responded) {
                  return gadget_chat_ui.clearPostList()
                    .push(function () {
                      return gadget_chat_ui.clearStreamingPreview();
                    })
                    .push(function () {
                      return gadget_chat_ui.setAllowSubmit(true);
                    })
                    .push(function () {
                      return gadget_chat_ui.resetEditor();
                    })
                    .push(function () {
                      return gadget_chat_ui.refreshHistory();
                    })
                    .push(function () {
                      gadget.element.setAttribute('data-chat-state', 'responded');
                    });
                }
                queue_loop
                  .push(function () {
                    return RSVP.delay(2000);
                  })
                  .push(function () {
                    return check();
                  });
              });
          });
      }
      check();
      return queue_loop;

    });
}(window, rJS, RSVP));
