/*globals window, document, RSVP, rJS, promiseEventListener,
            loopEventListener, getSequentialID,  fillMyInputUserName*/
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, RSVP, rJS, loopEventListener) {
  "use strict";

  rJS(window)
    .ready(function (g) {
      g.props = {};
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
        });
    })
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")
    .declareAcquiredMethod("jio_post", "jio_post")
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .allowPublicAcquisition('updateHeader', function () {
      return;
    })

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('triggerSubmit', function () {
      this.props.element.querySelector('button').click();
    })
   /////////////////////////////////////////
   // Form submit
   /////////////////////////////////////////

    .declareService(function () {
      var form_gadget = this;
      function formSubmit() {
        return form_gadget.notifySubmitting()
          .push(function () {
            return form_gadget.getDeclaredGadget("daily_statement_record_form");
          })
          .push(function (erp5_form) {
            return erp5_form.getContent();
          })
          .push(function (doc) {
            doc.parent_relative_url = "daily_statement_record_module";
            doc.portal_type = "Daily Statement Record";
            doc.doc_id = form_gadget.options.doc.doc_id;
            return form_gadget.jio_put(form_gadget.options.jio_key, doc);
          })
          .push(function () {
            return RSVP.all([
              form_gadget.notifySubmitted(),
              form_gadget.redirect({command: 'display',
                options: {jio_key: "daily_statement_record_module",
                  page: "view"}
                })
            ]);
          });
      }

      // Listen to form submit
      return loopEventListener(
        form_gadget.props.element.querySelector('form'),
        'submit',
        false,
        formSubmit
      );
    })

     .declareMethod("render", function (options) {
      var gadget = this;
      gadget.options = options;
      return new RSVP.Queue()
        .push(function () {
          return gadget.getDeclaredGadget("daily_statement_record_form");
        })
        .push(function (form_gadget) {
          return form_gadget.render(options);
        })
        .push(function () {
          return gadget.updateHeader({
            page_title: "Daily Statement Record"
              + " " + gadget.options.doc.doc_id,
            save_action: true
          });
        });
    });

}(window, RSVP, rJS, loopEventListener));