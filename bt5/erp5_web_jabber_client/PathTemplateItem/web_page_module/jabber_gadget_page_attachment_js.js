/*global window, rJS*/
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('render', function (options) {
      return this.changeState({
        jio_key: options.jio_key,
        first_render: true
      });
    })

    .onStateChange(function (modification_dict) {
      var gadget = this,
        url_for_queue,
        queue;

      if (modification_dict.hasOwnProperty('first_render')) {
        queue = gadget.getDeclaredGadget('form_dialog')
          .push(function (form_gadget) {
            return form_gadget.render({
              erp5_document: {'_embedded': {'_view': {
                your_text: {
                  description: '',
                  title: 'Text',
                  default: '',
                  css_class: '',
                  required: 1,
                  editable: 1,
                  key: 'your_text',
                  hidden: 0,
                  type: "TextAreaField"
                }
              }}},
              form_definition: {
                group_list: [[
                  "center",
                  [["your_text"]]
                ]]
              }
            });
          });
      }
      if (modification_dict.hasOwnProperty('jio_key')) {
        url_for_queue = gadget.getUrlFor({command: 'change',
                                          options: {page: 'jabberclient_dialog'}});
        if (queue === undefined) {
          queue = url_for_queue;
        } else {
          queue.push(function () {
            return url_for_queue;
          });
        }
        queue
          .push(function (url) {
            return gadget.updateHeader({
              cancel_url: url,
              page_title: gadget.state.jio_key
            });
          });
      }

      return queue;
    })

    .allowPublicAcquisition("submitContent", function submitContent(param_list) {
      var gadget = this,
        content = param_list[0];
      return gadget.jio_putAttachment(
        gadget.state.jio_key,
        'MESSAGE',
        content.your_text
      )
        .push(function () {
          return gadget.redirect({
            command: 'display',
            options: {
              jio_key: gadget.state.jio_key,
              page: 'jabberclient_dialog'
            }
          });
        });
    });

}(window, rJS));