/*globals window, document, RSVP, rJS,promiseEventListener*/
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
    })
    // Assign the element to a variable
    .ready(function (g) {
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
        });
    })
    .allowPublicAcquisition("inputChange", function () {
      return;
    })

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_post", "jio_post")
    .declareAcquiredMethod("setSetting", "setSetting")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod('allDocs', 'jio_allDocs')

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
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
        editable,
        daily_organisation_input_flag_editable = 1,
        daily_purchase_input_flag_editable = 1,
        daily_production_input_flag_editable = 1,
        daily_sale_input_flag_editable = 1;
      page_gadget.options = options;
      editable = 1;
      if (page_gadget.options.doc.date === undefined) {
        page_gadget.options.doc.date = new Date().toISOString().split('T')[0];
      }
      if (page_gadget.options.doc.daily_organisation_input_flag) {
        daily_organisation_input_flag_editable = 0;
      }
      if (page_gadget.options.doc.daily_purchase_input_flag) {
        daily_purchase_input_flag_editable = 0;
      }
      if (page_gadget.options.doc.daily_production_input_flag) {
        daily_production_input_flag_editable = 0;
      }
      if (page_gadget.options.doc.daily_sale_input_flag) {
        daily_sale_input_flag_editable = 0;
      }

      return new RSVP.Queue()
        .push(function () {
          return page_gadget.getDeclaredGadget("trade_form");
        })
        .push(function (form_gadget) {
          return form_gadget.render({
            erp5_document: {"_embedded": {"_view": {
              "organisation": {
                "description": "",
                "title": "Organisation",
                "default": page_gadget.options.doc.next_owner,
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "next_owner",
                "hidden": 0,
                "type": "StringField"
              },
              "date": {
                "description": "",
                "title": "Input Date",
                "default": page_gadget.options.doc.date,
                "css_class": "",
                "required": 1,
                "date_only": 1,
                "subfield_year_key": "year",
                "subfield_month_key": "month",
                "subfield_day_key": "day",
                "timezone_style": 0,
                "editable": editable,
                "date_only_style": 1,
                "key": "date",
                "hidden": 0,
                "type": "DateTimeField"
              },
              "daily_organisation_input_flag": {
                "description": "",
                "title": "Organisation data input is completed",
                "default": page_gadget.options.doc.
                  daily_organisation_input_flag,
                "css_class": "",
                "required": 1,
                "editable": daily_organisation_input_flag_editable,
                "key": "daily_organisation_input_flag",
                "hidden": 0,
                "type": "CheckBoxField"
              },
              "daily_purchase_input_flag": {
                "description": "",
                "title": "Purchase data input is completed",
                "default": page_gadget.options.doc.daily_purchase_input_flag,
                "css_class": "",
                "required": 1,
                "editable": daily_purchase_input_flag_editable,
                "key": "daily_purchase_input_flag",
                "hidden": 0,
                "type": "CheckBoxField"
              },
              "daily_production_input_flag": {
                "description": "",
                "title": "Production data input is completed",
                "default": page_gadget.options.doc.daily_production_input_flag,
                "css_class": "",
                "required": 1,
                "editable": daily_production_input_flag_editable,
                "key": "daily_production_input_flag",
                "hidden": 0,
                "type": "CheckBoxField"
              },
              "daily_sale_input_flag": {
                "description": "",
                "title": "Sales data input is completed",
                "default": page_gadget.options.doc.daily_sale_input_flag,
                "css_class": "",
                "required": 1,
                "editable": daily_sale_input_flag_editable,
                "key": "daily_sale_input_flag",
                "hidden": 0,
                "type": "CheckBoxField"
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
                "type": "StringField"
              }
            }}},
            form_definition: {
              group_list: [
                ["top",
                  [["organisation"], ["date"],
                    ["daily_organisation_input_flag"],
                    ["daily_purchase_input_flag"],
                    ["daily_production_input_flag"],
                    ["daily_sale_input_flag"],
                    ["comment"]]
                  ]
              ]
            }
          });
        });
    });

}(window, RSVP, rJS));
