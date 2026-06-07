/*globals window, document, RSVP, rJS, loopEventListener*/
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, RSVP, rJS) {
  "use strict";


  function addNewLine(queue, page_gadget, line_count) {
    queue
      .push(function () {
        var field_element = page_gadget.props
          .element.querySelector(".center");
        field_element.appendChild(document.createElement('hr'));
        return page_gadget.getDeclaredGadget("trade_form");
      })
      .push(function (form_gadget) {
        return form_gadget.render({
          erp5_document: {"_embedded": {"_view": {
            "quantity"  : {
              "description": "",
              "title": "Quantity",
              "default": page_gadget.options.doc["quantity" + line_count],
              "css_class": "",
              "required": 0,
              "editable": 1,
              "key": "quantity" + line_count,
              "hidden": 0,
              "precision": 0,
              "type": "FloatField"
            },
            "quantity_unit": {
              "description": "",
              "title": "Quantity Unit",
              "default": page_gadget.options.doc["quantity_unit" + line_count],
              "items": page_gadget.props.quantity_unit,
              "css_class": "",
              "required": 0,
              "editable": 1,
              "key": "quantity_unit" + line_count,
              "hidden": 0,
              "type": "ListField"
            },
            "batch": {
              "description": "",
              "title": "Batch",
              "default": page_gadget.options.doc["batch" + line_count],
              "css_class": "",
              "required": 0,
              "editable": 1,
              "key": "batch" + line_count,
              "hidden": 0,
              "type": "StringField"
            }
          }}},
          form_definition: {
            group_list: [
              ["center",
                [["quantity"],
                  ["quantity_unit"], ["batch"]
                   ]
                  ]
            ]
          }
        });
      });
  }


  rJS(window)
    /////////////////////////////////////////////////////////////////
    // ready
    /////////////////////////////////////////////////////////////////
    // Init local properties
    .ready(function (g) {
      g.props = {};
      g.props.quantity_unit = [];
      g.props.currency = [];
      g.props.line_count = 2;
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
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("setSetting", "setSetting")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod('allDocs', 'jio_allDocs')
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("jio_put", "jio_put")

    .allowPublicAcquisition("inputChange", function () {
      return;
    })
    .declareMethod('triggerSubmit', function () {
      this.props.element.querySelector('button').click();
    })
    .declareMethod("render", function (options) {
      var page_gadget = this,
        title,
        queue,
        relative_url,
        editable = 1;
      page_gadget.options = options;

      if (page_gadget.options.doc.line_count !== undefined) {
        page_gadget.props.line_count = page_gadget.options.doc.line_count;
      }
      if (page_gadget.options.doc.date === undefined) {
        page_gadget.options.doc.date = new Date().toISOString().split('T')[0];
      }
      queue =  new RSVP.Queue();
      queue.push(function () {
        return RSVP.all([
          page_gadget.allDocs({
            query: 'portal_type:' +
              '"Currency" AND validation_state: "validated"',
            select_list: ["title", "logical_path", "relative_url"],
            // sort_on: [["id", "ascending"]],
            limit: [0, 1234567890]
          }),

          page_gadget.allDocs({
            query: 'portal_type:' +
              '"Category" AND relative_url: "quantity_unit/%"',
            select_list: ["title", "logical_path", "category_relative_url"],
            // sort_on: [["id", "ascending"]],
            limit: [0, 1234567890]
          })
        ]);
      })
        .push(function (all_result) {
          var i;
          for (i = 0; i < all_result[0].data.total_rows; i += 1) {
            title = all_result[0].data.rows[i].value.title;
            relative_url = all_result[0].data.rows[i].value.relative_url;
            page_gadget.props.currency.push([title, relative_url]);
          }

          for (i = 0; i < all_result[1].data.total_rows; i += 1) {
            title =  all_result[1].data.rows[i]
              .value.logical_path || all_result[1].data.rows[i]
              .value.title;
            relative_url = all_result[1].data.rows[i]
              .value.category_relative_url;
            page_gadget.props.quantity_unit.push([title, relative_url]);
          }

          return;
        })
        .push(function () {
          return page_gadget.getDeclaredGadget("trade_form");
        })
        .push(function (form_gadget) {
          return form_gadget.render({
            erp5_document: {"_embedded": {"_view": {
              "product": {
                "description": "",
                "title": "Product or Material Title",
                "default": page_gadget.options.doc.product,
                "css_class": "",
                "required": 1,
                "editable": editable,
                "key": "product",
                "hidden": 0,
                "type": "StringField"
              },
              "previous_owner": {
                "description": "",
                "title": "Supplier",
                "default": page_gadget.options.doc.previous_owner,
                "css_class": "",
                "required": 1,
                "editable": 0,
                "key": "previous_owner",
                "hidden": 0,
                "type": "StringField"
              },
              "next_owner": {
                "description": "",
                "title": "Purchase Organisation",
                "default": page_gadget.options.doc.next_owner,
                "css_class": "",
                "required": 1,
                "editable": 0,
                "key": "next_owner",
                "hidden": 0,
                "type": "StringField"
              },
              "next_location": {
                "description": "",
                "title": "Recipient Warehouse or Bin",
                "default": page_gadget.options.doc.next_location,
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "next_location",
                "hidden": 0,
                "type": "StringField"
              },
              "price": {
                "description": "",
                "title": "Price",
                "default": page_gadget.options.doc.price,
                "css_class": "",
                "required": 1,
                "editable": editable,
                "key": "price",
                "hidden": 0,
                "precision": 2,
                "type": "FloatField"
              },
              "price_quantity_unit": {
                "description": "",
                "title": "Price Quantity Unit",
                "default": page_gadget.options.doc.price_quantity_unit,
                "items": page_gadget.props.quantity_unit,
                "css_class": "",
                "required": 1,
                "editable": editable,
                "key": "price_quantity_unit",
                "hidden": 0,
                "type": "ListField"
              },
              "currency": {
                "description": "",
                "title": "Currency",
                "default": page_gadget.options.doc.price_currency,
                "items": page_gadget.props.currency,
                "css_class": "",
                "required": 1,
                "editable": editable,
                "key": "price_currency",
                "hidden": 0,
                "type": "ListField"
              },
              "quantity": {
                "description": "",
                "title": "Quantity",
                "default": page_gadget.options.doc.quantity,
                "css_class": "",
                "required": 1,
                "editable": editable,
                "key": "quantity",
                "hidden": 0,
                "precision": 0,
                "type": "FloatField"
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
              "batch": {
                "description": "",
                "title": "Batch",
                "default": page_gadget.options.doc.batch,
                "css_class": "",
                "required": 1,
                "editable": editable,
                "key": "batch",
                "hidden": 0,
                "type": "StringField"
              },
              "date": {
                "description": "",
                "title": "Input Date",
                "default": page_gadget.options.doc.date,
                "css_class": "",
                "required": 0,
                "date_only": 1,
                "date_only_style": 1,
                "timezone_style": 0,
                "editable": editable,
                "key": "date",
                "hidden": 0,
                "type": "DateTimeField"
              },
              "comment": {
                "description": "",
                "title": "Comment",
                "default": page_gadget.options.doc.comment,
                "css_class": "",
                "required": 1,
                "editable": editable,
                "key": "comment",
                "hidden": 0,
                "type": "TextAreaField"
              }
            }}},
            form_definition: {
              group_list: [
                ["center",
                  [ ["product"], ["previous_owner"],
                    ["next_owner"], ["next_location"],
                    ["price"], ["price_quantity_unit"],
                    ["currency"], ["quantity"],
                    ["quantity_unit"], ["batch"],
                    ["date"], ["comment"]]
                  ]
              ]
            }
          });
        })
        .push(function () {
          var btn;
          btn = document.createElement("input");
          btn.setAttribute('name', 'add_line');
          btn.setAttribute('type', 'submit');
          btn.setAttribute("value", "Add Line");
          page_gadget.props.element
            .querySelector('.button_add_line').appendChild(btn);
          return page_gadget.updateHeader({
            page_title: "Purchase  Record" + " " +
              page_gadget.options.doc.doc_id,
            save_action: true
          });
        })
        .push(function () {
          var i;
          for (i = 2; i < page_gadget.props.line_count; i += 1) {
            if ((page_gadget.options.doc["quantity" + i] !== undefined
                && page_gadget.options.doc["quantity" + i] !== "")) {
              addNewLine(queue, page_gadget, i);
            }
          }
        });
      return queue;
    })



    /////////////////////////////////////////
    // add line button
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return loopEventListener(
            gadget.props.element.querySelector('[name=add_line]'),
            'click',
            false,
            function () {
              var queue = new RSVP.Queue();
              queue.push(function () {
                addNewLine(queue, gadget, gadget.props.line_count);
                gadget.props.line_count += 1;
                return;
              });
            }
          );
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
            return form_gadget.getDeclaredGadget("trade_form");
          })
          .push(function (trade_form) {
            return trade_form.getContent({"format": "json"});
          })
          .push(function (doc) {
            doc.parent_relative_url = "purchase_record_module";
            doc.portal_type = "Purchase Record";
            doc.next_owner = form_gadget.options.doc.next_owner;
            doc.previous_owner = form_gadget.options.doc.previous_owner;
            doc.doc_id = form_gadget.options.doc.doc_id;
            doc.record_revision =  form_gadget.options.doc.record_revision || 1;
            doc.line_count = form_gadget.props.line_count;
            return form_gadget.jio_put(form_gadget.options.jio_key, doc);
          })
          .push(function () {
            return RSVP.all([
              form_gadget.notifySubmitted(),
              form_gadget.redirect({command: 'display',
                options: {jio_key: "purchase_record_module", page: "view"}
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
}(window, RSVP, rJS));
