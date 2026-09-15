/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  var POLL_INTERVAL = 1000;

  rJS(window)
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("requestProcessTask", "requestProcessTask")

    .declareMethod('render', function (options) {
      var gadget = this;
      gadget.options = options;
      return gadget.getDeclaredGadget("gadget_chat_ui")
        .push(function (gadget_chat_ui) {
          gadget.gadget_chat_ui = gadget_chat_ui;
          return gadget_chat_ui.render(options);
        })
        .push(function () {
          if (options.chat_state == 'planned') {
            return gadget.requestProcessTask(
              gadget.options.jio_key,
              {}
            )
            .push(function () {
              return gadget.pollTask();
            });
          }
          if (options.chat_state === 'processing') {
            return gadget.pollTask();
          }
        });
    })
    .allowPublicAcquisition('notifyCommentPosted', function () {
      var gadget = this;
      return gadget.requestProcessTask(
        gadget.options.jio_key,
        {}
      )
        .push(function () {
          return gadget.pollTask();
        });
    })
    .declareJob('pollTask', function () {
      var gadget = this,
        gadget_chat_ui = gadget.gadget_chat_ui,
        queue_loop = gadget_chat_ui.blockEditor();
      function check() {
        queue_loop
          .push(function () {
            return RSVP.delay(POLL_INTERVAL);
          })
          .push(function () {
            return gadget.jio_getAttachment(
              gadget.options.jio_key,
              gadget.options.status_url
            );
          })
          .push(function (result) {
            queue_loop
              .push(function () {
                return gadget_chat_ui.showMessage(result);
              });
            if (result.done) {
              queue_loop
                .push(function () {
                  return gadget_chat_ui.resetEditor();
                });
            } else {
              queue_loop
                .push(check);
            }
          });
      }
      check();
      return queue_loop;

    });
}(window, rJS, RSVP));
