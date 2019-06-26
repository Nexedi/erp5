/*global window, rJS */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, calculatePageTitle, jIO) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .allowPublicAcquisition('getUrlFor', function (argument_list) {
      if (argument_list[0].command === 'change') {
        if (argument_list[0].options.page == "action") {
          return this.getUrlFor({command: 'change', options: {page: "fif_action"}});
        }
      }
      return this.getUrlFor.apply(this, argument_list);
    })
    .allowPublicAcquisition('updateHeader', function (argument_list) {
      var header_dict = {
          page_title: "Data Set : " + this.state.document_title,
          selection_url: argument_list[0].selection_url,
          //next_url: argument_list[0].next_url,
          //previous_url: argument_list[0].previous_url,
          actions_url: argument_list[0].actions_url
        };
      return this.updateHeader(header_dict);
    })
    .onStateChange(function () {
      var gadget = this;
      return gadget.getDeclaredGadget('form_view')
        .push(function (form_gadget) {
          return form_gadget.render({
            erp5_document: {"_embedded": {"_view": {
              "my_title" : {
                "description": "The name of a document in ERP5",
                "title": "Title",
                "default": gadget.state.document_title,
                "css_class": "",
                "editable": 1,
                "hidden": 0,
                "key": "field_my_title",
                "required": 0,
                "type": "StringField"
              },
              "my_reference" : {
                "description": "Reference of a page, should be unique to retrieve a page easily",
                "title": "Reference",
                "default": gadget.state.reference,
                "css_class": "",
                "editable": 1,
                "hidden": 0,
                "key": "field_my_reference",
                "required": 0,
                "type": "StringField"
              },
              "my_description" : {
                "description": "The description of the document.",
                "title": "Description",
                "default": gadget.state.description,
                "css_class": "",
                "editable": 1,
                "hidden": 0,
                "key": "field_my_state",
                "required": 0,
                "type": "StringField"
              }
            }},
              "_links": {
                "type": {
                  name: ""
                }
              }
            },
              form_definition: {
                group_list: [
                  [
                    "left",
                    [["my_title"]]
                  ],
                  [
                    "right",
                    [["my_reference"]]
                  ],
                  [
                    "center",
                    [["my_description"]]
                  ]
                ]
              }
            });
        });
    })

    .declareMethod("render", function (options) {
      var gadget = this;
      return gadget.jio_get(options.jio_key)
      .push(function (result) {
        return gadget.changeState({"document_title" : result.title,
                                   "reference" : result.reference,
                                   "description" : result.description})
      .push(function () {
          return gadget.getDeclaredGadget("gadget_fif_page_list_file");
        })
        .push(function (my_gadget) {
          return my_gadget.render(result);
        })
        .push(function () {
          return gadget.getDeclaredGadget("download_access");
        })
        .push(function (my_gadget) {
          return my_gadget.render(gadget.state.reference);
        });
      });
    });
}(window, rJS, RSVP, calculatePageTitle, jIO));









