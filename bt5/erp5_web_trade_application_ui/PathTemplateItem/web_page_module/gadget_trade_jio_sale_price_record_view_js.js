/*globals window, RSVP, rJS, promiseEventListener, loopEventListener,
document, getSequentialID*/
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, document, RSVP, rJS, promiseEventListener) {
  "use strict";

  rJS(window)
    .ready(function (g) {
      g.props = {};
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
        });
    })
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("setSetting", "setSetting")
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("jio_post", "jio_post")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod('allDocs', 'jio_allDocs')

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
          return gadget.getDeclaredGadget("sale_price_record_form");
        })
        .push(function (form_gadget) {
          return form_gadget.render(options);
        })
        .push(function () {
          var btn;
          btn = document.createElement("input");
          btn.setAttribute('name', 'create_sale_record');
          btn.setAttribute('type', 'submit');
          btn.setAttribute("value", "Create Sale Record");
          gadget.props.element.querySelector('.right').appendChild(btn);
          return gadget.updateHeader({
            page_title: "Sale Price Record" + " " +
              gadget.options.doc.doc_id,
            save_action: true
          });
        });
    })

   /////////////////////////////////////////
   // Form submit
   /////////////////////////////////////////

    .declareService(function () {
      var form_gadget = this,
        doc_tmp;

      function formSubmit() {
        return form_gadget.notifySubmitting()
          .push(function () {
            return form_gadget.getDeclaredGadget("sale_price_record_form");
          })
          .push(function (erp5_form) {
            return erp5_form.getContent();
          })
          .push(function (doc) {
            doc_tmp = doc;
            doc.parent_relative_url = "sale_price_record_module";
            doc.portal_type = "Sale Price Record";
            doc.doc_id = form_gadget.options.doc.doc_id;
            doc.record_revision =  form_gadget.options.doc.record_revision || 1;
            return form_gadget.jio_put(form_gadget.options.jio_key, doc);
          })
          .push(function () {
            return form_gadget.allDocs({
              query: 'portal_type:("Organisation") AND title_lowercase: "'
                  + doc_tmp.next_owner.toLowerCase() + '"',
              limit: [0, 2]
            });
          })
          .push(function (result) {
            if (result.data.total_rows === 0) {
              var doc = {
                parent_relative_url : "organisation_module",
                portal_type : "Organisation",
                organisation_title : doc_tmp.next_owner_title,
                title_lowercase : doc_tmp.next_owner_title.toLowerCase(),
                organisation_reference : doc_tmp.next_owner_reference,
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
              return form_gadget.jio_post(doc);
            }
          })
          .push(function () {
            return RSVP.all([
              form_gadget.notifySubmitted(),
              form_gadget.redirect({command: 'display',
                options: {jio_key: "sale_price_record_module", page: "view"}
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


    /////////////////////////////////////////
    // Create Sale Record
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this;
      if (gadget.props.element.querySelector('[name=create_sale_record]')
          === null) {
        return;
      }
      return new RSVP.Queue()
        .push(function () {
          return promiseEventListener(
            gadget.props.element
              .querySelector('[name=create_sale_record]'),
            'click',
            false
          );
        })
        .push(function () {
          return getSequentialID(gadget, 'SR');
        })
        .push(function (result) {
          var doc = {
            // XXX Hardcoded
            parent_relative_url: "sale_record_module",
            portal_type: "Sale Record",
            doc_id: result,
            record_revision: 1,
            price: gadget.options.doc.base_price,
            quantity_unit: gadget.options.doc.quantity_unit,
            product: gadget.options.doc.product,
            next_owner: gadget.options.doc.next_owner,
            previous_owner: gadget.options.doc.previous_owner,
            previous_location: gadget.options.doc.previous_location,
            price_currency: gadget.options.doc.price_currency,
            contract_no: gadget.options.doc.contract_no,
            batch: gadget.options.doc.batch,
            comment: gadget.options.doc.comment
          };
          return gadget.jio_post(doc);
        })
        .push(function (response) {
          return gadget.redirect({command: 'display',
            options: {jio_key: response, page: "view"}
            });
        });
    }
      );



}(window, document, RSVP, rJS, promiseEventListener));
