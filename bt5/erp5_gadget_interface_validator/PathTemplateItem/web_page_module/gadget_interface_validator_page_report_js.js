/*global window, rJS*/
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS) {
  "use strict";

  rJS(window)
   /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlForList", "getUrlForList")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .allowPublicAcquisition('updateHeader', function () {
      return;
    })

    .declareMethod("render", function (options) {
      return this.changeState(options);
    })

    .onStateChange(function () {
      var gadget = this;

      return gadget.getUrlForList([{
        command: 'display_stored_state',
        options: {page: 'validator_result_list'}
      }, {
        command: 'selection_previous'
      }, {
        command: 'selection_next'
      }])
        .push(function (url_list) {
          return gadget.updateHeader({
            selection_url: url_list[0],
            // previous_url: url_list[1],
            // next_url: url_list[2],
            page_title: gadget.state.jio_key
          });
        })
        .push(function () {
          return gadget.getDeclaredGadget('form_view');
        })
        .push(function (form_gadget) {
          return form_gadget.render({
            erp5_document: {"_embedded": {"_view": {
              "title": {
                description: "",
                title: "Title",
                "default": gadget.state.jio_key,
                css_class: "",
                required: null,
                editable: 0,
                key: "title",
                hidden: 0,
                type: "StringField"
              },
              "text_content": {
                description: "",
                title: "State",
                "default": gadget.state.jio_key,
                css_class: "",
                required: null,
                editable: 0,
                url: "gadget_interface.html",
                sandbox: "",
                renderjs_extra: JSON.stringify({
                  gadget_to_check_url: gadget.state.jio_key,
                  summary: false
                }),
                key: "text_content",
                hidden: 0,
                type: "GadgetField"
              }
            }},
              "_links": {
                "type": {
                  // form_list display portal_type in header
                  name: ""
                }
              }
              },
            form_definition: {
              group_list: [[
                "center", [["title"], ["text_content"]]
              ]]
            }
          });
        });
    });

}(window, rJS));