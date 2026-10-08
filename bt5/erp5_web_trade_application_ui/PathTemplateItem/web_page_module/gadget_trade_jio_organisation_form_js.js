/*globals window, document, RSVP, rJS,promiseEventListener, loopEventListener*/
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

    .allowPublicAcquisition("inputChange", function () {
      return;
    })
    .declareMethod('triggerSubmit', function () {
      this.props.element.querySelector('button').click();
    })

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("getContent", function () {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return gadget.getDeclaredGadget("trade_form");
        })
        .push(function (trade_form) {
          return trade_form.getContent({"format": "json"});
        })
        .push(function (result) {
          return result;
        });
    })

    .declareMethod("render", function (options) {
      var page_gadget = this,
        title,
        queue,
        relative_url,
        editable = 1,
        organisation_title_disabled = 0;
      page_gadget.options = options;
      if (page_gadget.options.doc.organisation_title !== undefined &&
          page_gadget.options.doc.organisation_title !== "") {
        organisation_title_disabled = 1;
      }
      queue =  new RSVP.Queue();
      queue
        .push(function () {
          return page_gadget.allDocs({
            query: 'portal_type:' +
              '"Category" AND relative_url: "region/%"',
            select_list: ["title", "logical_path", "category_relative_url"],
               // sort_on: [["id", "ascending"]],
            limit: [0, 1234567890]
          });
        })
        .push(function (result) {
          var i;
          page_gadget.props.region.push(["", ""]);
          for (i = 0; i < result.data.total_rows; i += 1) {
            title = result.data.rows[i]
              .value.logical_path || result.data.rows[i]
              .value.title;
            relative_url = result.data.rows[i]
              .value.category_relative_url;
            page_gadget.props.region.push([title, relative_url]);
          }
          return;
        })
        .push(function () {
          return page_gadget.getDeclaredGadget("trade_form");
        })
        .push(function (form_gadget) {
          return form_gadget.render({
            erp5_document: {"_embedded": {"_view": {

              "title": {
                "description": "",
                "title": "Organisation Title",
                "default": page_gadget.options.doc.organisation_title,
                "css_class": "",
                "required": 1,
                "editable": editable,
                "key": "organisation_title",
                "hidden": 0,
                "type": "StringField",
                "disabled" : organisation_title_disabled
              },

              "reference": {
                "description": "",
                "title": "Organisation Reference",
                "default": page_gadget.options.doc.organisation_reference,
                "css_class": "",
                "required": 1,
                "editable": editable,
                "key": "organisation_reference",
                "hidden": 0,
                "type": "StringField"
              },

              "telephone": {
                "description": "",
                "title": "Default Telephone",
                "default":
                  page_gadget.options.doc.default_telephone_coordinate_text,
                "css_class": "",
                "required": 0,
                "editable": editable,
                "key": "default_telephone_coordinate_text",
                "hidden": 0,
                "type": "StringField"
              },

              "address_city": {
                "description": "",
                "title": "Default Address City",
                "default": page_gadget.options.doc.default_address_city,
                "css_class": "",
                "required": 1,
                "editable": editable,
                "key": "default_address_city",
                "hidden": 0,
                "type": "StringField"
              },

              "region": {
                "description": "",
                "title": "Region",
                "default": page_gadget.options.doc.default_address_region,
                "items": page_gadget.props.region,
                "css_class": "",
                "required": 1,
                "editable": editable,
                "key": "default_address_region",
                "hidden": 0,
                "type": "ListField"
              },

              "address_street": {
                "description": "",
                "title": "Default Address",
                "default":
                  page_gadget.options.doc.default_address_street_address,
                "css_class": "",
                "required": 1,
                "editable": editable,
                "key": "default_address_street_address",
                "hidden": 0,
                "type": "StringField"
              },

              "postal_code": {
                "description": "",
                "title": "Postal Code",
                "default": page_gadget.options.doc.default_address_zip_code,
                "css_class": "",
                "required": 0,
                "editable": editable,
                "key": "default_address_zip_code",
                "hidden": 0,
                "type": "StringField"
              },

              "email": {
                "description": "",
                "title": "Email",
                "default":
                  page_gadget.options.doc.default_email_coordinate_text,
                "css_class": "",
                "required": 0,
                "editable": editable,
                "key": "default_email_coordinate_text",
                "hidden": 0,
                "type": "StringField"
              }
            }}},
            form_definition: {
              group_list: [
                ["center",
                  [
                    ["title"], ["reference"], ["telephone"],
                    ["address_city"], ["region"], ["address_street"],
                    ["postal_code"], ["email"]
                  ]
                  ]
              ]
            }
          });
        });
      return queue;
    });
}(window, RSVP, rJS));
