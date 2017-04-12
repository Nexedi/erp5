/*global window, rJS */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .allowPublicAcquisition('updateHeader', function (argument_list) {
      return this.updateHeader({
        next_url: argument_list[0].next_url,
        previous_url: argument_list[0].previous_url,
        selection_url: argument_list[0].selection_url,
        page_title: this.state.doc.portal_type + ': ' + this.state.doc.title
      });
    })

    .declareMethod("render", function (options) {
      return this.changeState({
        doc: options.doc
      });
    })

    .onStateChange(function () {
      var gadget = this;
      return gadget.getDeclaredGadget('form_view')
        .push(function (form_gadget) {
          return form_gadget.render({
            erp5_document: {"_embedded": {"_view": {
              "my_title": {
                "description": "The name of a document in ERP5",
                "title": "Title",
                "default": gadget.state.doc.title,
                "css_class": "",
                "required": 1,
                "editable": 0,
                "key": "field_my_title",
                "hidden": 0,
                "type": "StringField"
              },
              "my_reference": {
                "description": "The name of a document in ERP5",
                "title": "Reference",
                "default": gadget.state.doc.reference,
                "css_class": "",
                "required": 0,
                "editable": 0,
                "key": "field_my_reference",
                "hidden": 0,
                "type": "StringField"
              }
            }},
              "_links": {
                "type": {
                  // form_list display portal_type in header
                  name: ""
                }
              }},
            form_definition: {
              group_list: [[
                "left",
                [["my_title"], ["my_reference"]]
              ]]
            }
          });
        });
    });
}(window, rJS));