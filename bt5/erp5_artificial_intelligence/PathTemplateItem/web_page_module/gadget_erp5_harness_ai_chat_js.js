/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  var POLL_INTERVAL = 1000;
  var STATE_POLL_INTERVAL = 3000;

  rJS(window)
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("requestProcessTask", "requestProcessTask")
    .declareAcquiredMethod("refreshPanel", "refreshPanel")
    .declareAcquiredMethod("getTaskStatus", "getTaskStatus")

    .declareMethod('render', function (options) {
      var gadget = this;
      gadget.options = options;
      return gadget.getDeclaredGadget("gadget_chat_ui")
        .push(function (gadget_chat_ui) {
          gadget.gadget_chat_ui = gadget_chat_ui;
          return gadget_chat_ui.render(options);
        })
        .push(function () {
          if (options.chat_state == 'planned' && false) {
            return gadget.requestProcessTask(
              gadget.options.jio_key,
              {}
            )
            .push(function () {
              return gadget.pollTask();
            });
          }
        });
    })
    .allowPublicAcquisition('notifyCommentPosted', function () {
      return;
      /*
      var gadget = this;
      return gadget.requestProcessTask(
        gadget.options.jio_key,
        {}
      )
        .push(function () {
          return gadget.pollTask();
        });
      */
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
            return gadget.getTaskStatus(gadget.options.jio_key);
          })
          .push(function (result) {
            queue_loop
              .push(function () {
                return gadget_chat_ui.showMessage(result);
              });
            if (result.done) {
              queue_loop
                .push(function () {
                  return gadget.refreshPanel();
                })
                .push(function () {
                  gadget.is_processing = false;
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

    })
    .onLoop(function () {
      var gadget = this;
      if (gadget.is_processing) {
        return;
      }
      return gadget.jio_getAttachment(
        gadget.options.jio_key,
        gadget.options.view
      )
        .push(function (erp5_document) {
          var simulation_state = erp5_document._embedded._view.my_simulation_state['default'];
          if (simulation_state === 'processing' && !gadget.is_processing) {
            gadget.is_processing = true;
            return gadget.pollTask();
          }
        });
    }, STATE_POLL_INTERVAL);
}(window, rJS, RSVP));
