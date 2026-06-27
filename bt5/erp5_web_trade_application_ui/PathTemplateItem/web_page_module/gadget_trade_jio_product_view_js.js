/*globals window, rJS, RSVP, loopEventListener*/
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, rJS, RSVP) {
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
    .declareMethod("render", function (options) {
      var gadget = this;
      gadget.options = options;
      return new RSVP.Queue()
        .push(function () {
          return gadget.getDeclaredGadget("product_form");
        })
        .push(function (form_gadget) {
          return form_gadget.render(options);
        })
        .push(function () {
          return gadget.updateHeader({
            page_title: "Product" + " " + gadget.options.doc.product_reference,
            save_action: true
          });
        });
    })

   /////////////////////////////////////////
   // Form submit
   /////////////////////////////////////////

    .declareService(function () {
      var form_gadget = this;
      function formSubmit() {
        return form_gadget.notifySubmitting()
          .push(function () {
            return form_gadget.getDeclaredGadget("product_form");
          })
          .push(function (erp5_form) {
            return erp5_form.getContent();
          })
          .push(function (doc) {
            doc.parent_relative_url = "product_module";
            doc.portal_type = "Product";
            doc.title_lowercase = doc.product_title.toLowerCase();
            return form_gadget.jio_put(form_gadget.options.jio_key, doc);
          })
          .push(function () {
            return RSVP.all([
              form_gadget.notifySubmitted(),
              form_gadget.redirect({command: 'display',
                options: {jio_key: "product_module",
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
    });
}(window, rJS, RSVP));