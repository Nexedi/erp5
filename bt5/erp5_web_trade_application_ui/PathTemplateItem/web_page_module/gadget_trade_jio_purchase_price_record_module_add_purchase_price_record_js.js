/*globals window, RSVP, rJS, getWorkflowState, getSequentialID,
 loopEventListener*/
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, RSVP, rJS) {
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
    .declareAcquiredMethod("setSetting", "setSetting")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("jio_post", "jio_post")
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod('allDocs', 'jio_allDocs')
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
      var form_gadget = this,
        doc_id,
        doc_tmp;

      function formSubmit() {
        return form_gadget.notifySubmitting()
          .push(function () {
            return getSequentialID(form_gadget, 'PPR');
          })
          .push(function (result) {
            doc_id = result;
            return doc_id;
          })
          .push(function () {
            return form_gadget.getDeclaredGadget("purchase_price_record_form");
          })
          .push(function (erp5_form) {
            return erp5_form.getContent();
          })
          .push(function (doc) {
            doc_tmp = doc;
            doc.parent_relative_url = "purchase_price_record_module";
            doc.portal_type = "Purchase Price Record";
            doc.doc_id = doc_id;
            doc.record_revision = 1;
            doc.priced_quantity = 1;
            return form_gadget.jio_post(doc);
          })
          .push(function () {
            return form_gadget.allDocs({
              query: 'portal_type:("Organisation") AND title_lowercase: "'
                  + doc_tmp.previous_owner.toLowerCase() + '"',
              limit: [0, 2]
            });
          })
          .push(function (result) {
            var doc = {
                parent_relative_url : "organisation_module",
                portal_type : "Organisation",
                organisation_title : doc_tmp.previous_owner_title,
                title_lowercase : doc_tmp.previous_owner_title.toLowerCase(),
                organisation_reference : doc_tmp.previous_owner_reference,
                default_telephone_coordinate_text :
                  doc_tmp.default_telephone_coordinate_text,
                default_address_city : doc_tmp.default_address_city,
                default_address_region : doc_tmp.default_address_region,
                default_address_street_address :
                  doc_tmp.default_address_street_address,
                default_address_zip_code : doc_tmp.default_address_zip_code,
                default_email_coordinate_text :
                  doc_tmp.default_email_coordinate_text
              };
            if (result.data.total_rows === 0) {
              return form_gadget.jio_post(doc);
            }
            return form_gadget.jio_put(result.data.rows[0].id, doc);
          })
          .push(function () {
            return form_gadget.allDocs({
              query: 'portal_type:("Product") AND title_lowercase: "'
                  + doc_tmp.product.toLowerCase() + '"',
              limit: [0, 2]
            });
          })
          .push(function (result) {
            var doc = {
                parent_relative_url : "product_module",
                portal_type : "Product",
                product_title : doc_tmp.product_title,
                title_lowercase : doc_tmp.product_title.toLowerCase(),
                product_reference : doc_tmp.product_reference,
                product_line : doc_tmp.product_line,
                quantity_unit : doc_tmp.quantity_unit
              };
            if (result.data.total_rows === 0) {
              return form_gadget.jio_post(doc);
            }
            return form_gadget.jio_put(result.data.rows[0].id, doc);
          })
          .push(function () {
            return RSVP.all([
              form_gadget.notifySubmitted(),
              form_gadget.redirect({command: 'display',
                options: {jio_key: "purchase_price_record_module", page: "view"}
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
      return new RSVP.Queue()
        .push(function () {
          return gadget.updateHeader({
            page_title: "New Purchase Price Record",
            add_action: true
          });
        })
        .push(function () {
          return gadget.getDeclaredGadget("purchase_price_record_form");
        })
        .push(function (form_gadget) {
          return form_gadget.render(options);
        });
    });

}(window, RSVP, rJS));
