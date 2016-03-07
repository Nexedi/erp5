/*global window, rJS, RSVP, loopEventListener*/
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, loopEventListener) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // ready
    /////////////////////////////////////////////////////////////////
    // Init local properties
    .ready(function (g) {
      g.props = {};
    })

    // Assign the element to a variable
    .ready(function (g) {
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
        });
    })

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("redirect", "redirect")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('triggerSubmit', function () {
      this.props.element.querySelector('button').click();
    })
    .declareMethod("render", function () {
      var page_gadget = this;
      return page_gadget.updateHeader({
        page_title: 'New Contact',
        submit_action: true
      })
        .push(function () {
          // Ensure user is connected...
          return page_gadget.jio_allDocs();
        })
        .push(function () {
          return page_gadget.getDeclaredGadget("erp5_form");
        })
        .push(function (form_gadget) {
          return form_gadget.render({
            erp5_document: {"_embedded": {"_view": {
              "jid": {
                "description": "",
                "title": "Jabber ID",
                "default": "",
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "jid",
                "hidden": 0,
                "type": "StringField"
              }
            }}},
            form_definition: {
              group_list: [[
                "center",
                [["jid"]]
              ]]
            }
          });
        });
    })

    .declareService(function () {
      var form_gadget = this;

      function formSubmit() {
        return form_gadget.notifySubmitting()
          .push(function () {
            return form_gadget.getDeclaredGadget("erp5_form");
          })
          .push(function (erp5_form) {
            return erp5_form.getContent();
          })
          .push(function (content_dict) {
            return form_gadget.jio_put(
              'SUBSCRIBE',
              content_dict
            );
          })
          .push(function () {
            return RSVP.all([
              form_gadget.notifySubmitted(),
              form_gadget.redirect({command: 'display', options: {page: 'contact'}})
            ]);
          })
          .push(undefined, function (error) {
            return form_gadget.notifySubmitted()
              .push(function () {
                throw error;
              });
          });
      }

      // Listen to form submit
      return loopEventListener(
        form_gadget.props.element.querySelector('form'),
        'submit',
        false,
        formSubmit
      );
    });

}(window, rJS, RSVP, loopEventListener));