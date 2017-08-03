/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("jio_put", "jio_put")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("render", function (options) {
      var gadget = this;
      return gadget.getDeclaredGadget('form_view')
        .push(function (form_gadget) {
          return form_gadget.render({
            erp5_document: {"_embedded": {"_view": {
              "my_title": {
                  "description": "The name of a document in ERP5",
                  "title": "Title",
                  "default": "",
                  "css_class": "",
                  "required": 0,
                  "editable": 1,
                  "key": "title",
                  "hidden": 0,
                  "type": "StringField"
                },
                "my_reference": {
                  "description": "The name of a document in ERP5",
                  "title": "Reference",
                  "default": 1,
                  "css_class": "",
                  "required": 0,
                  "editable": 1,
                  "key": "reference",
                  "hidden": 0,
                  "type": "StringField"
                },
                "my_file": {
                  "title": "File",
                  "desription": "this will be imported",
                  "default": "",
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "text_content",
                  "hidden": 0,
                  "type": "FileField"
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
                  [["my_title"], ["my_reference"], ["my_file"]]
                ]]
              }
            });
        })
        .push(function () {
          return gadget.updateHeader({
            submit_action: true,
            page_title: "Import"
          });
        });
    })

    .declareMethod("triggerSubmit", function () {
      var gadget = this;
      return gadget.getDeclaredGadget('form_view')
        .push(function (form_gadget) {
          return form_gadget.getContent();
        })
        .push(function (doc) {
          debugger;
          return gadget.jio_put(gadget.state.jio_key, doc);
        });
    });

}(window, rJS, RSVP));
