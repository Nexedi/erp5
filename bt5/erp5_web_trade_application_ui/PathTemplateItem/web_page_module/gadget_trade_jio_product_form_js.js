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
      g.props.quantity_unit = [];
      g.props.product_line = [];
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
        product_title_disabled,
        relative_url,
        editable = 1;
      page_gadget.options = options;
      if (page_gadget.options.doc.product_title !== undefined &&
          page_gadget.options.doc.product_title !== "") {
        product_title_disabled = 1;
      }
      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            page_gadget.allDocs({
              query: 'portal_type:' +
                '"Category" AND relative_url: "quantity_unit/%"',
              select_list: ["title", "logical_path", "category_relative_url"],
              // sort_on: [["id", "ascending"]],
              limit: [0, 1234567890]
            }),

            page_gadget.allDocs({
              query: 'portal_type: "Category"' +
                'AND relative_url: "product_line/%"',
              select_list: ["title", "logical_path", "category_relative_url"],
            // sort_on: [["id", "ascending"]],
              limit: [0, 1234567890]
            })
          ]);
        })
        .push(function (all_result) {
          var i;
          for (i = 0; i < all_result[0].data.total_rows; i += 1) {
            title =  all_result[0].data.rows[i]
              .value.logical_path || all_result[0].data.rows[i]
              .value.title;
            relative_url = all_result[0].data.rows[i]
              .value.category_relative_url;
            page_gadget.props.quantity_unit.push([title, relative_url]);
          }

          page_gadget.props.product_line.push(["", ""]);
          for (i = 0; i < all_result[1].data.total_rows; i += 1) {
            title = all_result[1].data.rows[i]
              .value.logical_path || all_result[1].data.rows[i]
              .value.title;
            relative_url = all_result[1].data.rows[i]
              .value.category_relative_url;
            page_gadget.props.product_line.push([title, relative_url]);
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
                "title": "Product Title",
                "default": page_gadget.options.doc.product_title,
                "css_class": "",
                "required": 1,
                "editable": editable,
                "key": "product_title",
                "hidden": 0,
                "type": "StringField",
                "disabled" : product_title_disabled
              },
              "product_line": {
                "description": "",
                "title": "Product or Material Line",
                "default": page_gadget.options.doc.product_line,
                "items": page_gadget.props.product_line,
                "css_class": "",
                "required": 1,
                "editable": editable,
                "key": "product_line",
                "hidden": 0,
                "type": "ListField"
              },
              "quantity_unit": {
                "description": "",
                "title": "Quantity Unit",
                "default": page_gadget.options.doc.quantity_unit,
                "items": page_gadget.props.quantity_unit,
                "css_class": "",
                "required": 1,
                "editable": editable,
                "key": "quantity_unit",
                "hidden": 0,
                "type": "ListField"
              },
              "reference": {
                "description": "",
                "title": "Product Reference",
                "default": page_gadget.options.doc.product_reference,
                "css_class": "",
                "required": 1,
                "editable": editable,
                "key": "product_reference",
                "hidden": 0,
                "type": "StringField"
              }
            }}},
            form_definition: {
              group_list: [
                ["center",
                  [
                    ["title"], ["product_line"],
                    ["quantity_unit"], ["reference"]
                  ]
                  ]
              ]
            }
          });
        });
    });
}(window, RSVP, rJS));
