/*globals window, document, RSVP, rJS, loopEventListener*/
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, RSVP, rJS) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // ready
    /////////////////////////////////////////////////////////////////
    // Init local properties
    .ready(function (g) {
      g.props = {};
      g.props.region = [];
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
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod('allDocs', 'jio_allDocs')
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("jio_post", "jio_post")

    .allowPublicAcquisition('updateHeader', function () {
      return;
    })

    .declareMethod('triggerSubmit', function () {
      this.props.element.querySelector('button').click();
    })

    .declareMethod("render", function (options) {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return gadget.updateHeader({
            page_title: "New Organisation",
            add_action: true
          });
        })
        .push(function () {
          return gadget.getDeclaredGadget("organisation_form");
        })
        .push(function (form_gadget) {
          return form_gadget.render(options);
        });
    })


    /////////////////////////////////////////
   // Form submit
   /////////////////////////////////////////

    .declareService(function () {
      var form_gadget = this,
        doc_tmp,
        organisation_exist;
      function formSubmit() {
        return form_gadget.notifySubmitting()
          .push(function () {
            return form_gadget.getDeclaredGadget("organisation_form");
          })
          .push(function (trade_form) {
            return trade_form.getContent();
          })
          .push(function (doc) {
            doc_tmp = doc;
            return form_gadget.allDocs({
              query: 'portal_type:("Organisation") AND title_lowercase: "'
                  + doc_tmp.organisation_title.toLowerCase() + '"',
              limit: [0, 2]
            });
          })
          .push(function (result) {
            if (result.data.total_rows === 0) {
              doc_tmp.parent_relative_url = "organisation_module";
              doc_tmp.portal_type = "Organisation";
              doc_tmp.title_lowercase =
                doc_tmp.organisation_title.toLowerCase();
              return form_gadget.jio_post(doc_tmp);
            }
            organisation_exist = 1;
            form_gadget.props.element.querySelector('.warning').innerHTML
              = "This organization already exists";
            return form_gadget.notifySubmitted();
          })
          .push(function () {
            if (organisation_exist !== 1) {
              return RSVP.all([
                form_gadget.notifySubmitted(),
                form_gadget.redirect({command: 'display',
                  options: {jio_key: "organisation_module", page: "view"}
                  })
              ]);
            }
            organisation_exist = 0;
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
}(window, RSVP, rJS));
