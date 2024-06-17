/*global window, rJS */
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, rJS) {
  "use strict";

  rJS(window)
    .setState({
      erp5_url: "https://panel.rapid.space/hateoas/"
    })
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("setSetting", "setSetting")

    /////////////////////////////////////////
    // Form submit
    /////////////////////////////////////////
    .onEvent('submit', function () {
      var gadget = this,
        master_url;
      return gadget.getDeclaredGadget('form_view')
        .push(function (form_gadget) {
          return form_gadget.getContent();
        })
        .push(function (content) {
          master_url = content.erp5_url;
          return gadget.setSetting("hateoas_url", master_url);
        })
        .push(function () {
          return gadget.redirect({command: "display", options: {
            page: "ojsm_import_export",
            auto_sync: "erp5",
            url: master_url
          }});
        });
    })

    .declareMethod("triggerSubmit", function () {
      return this.element.querySelector('button[type="submit"]').click();
    })

    .declareMethod("render", function () {
      var gadget = this;

      return gadget.getDeclaredGadget('form_view')
        .push(function (form_gadget) {
          return form_gadget.render({
            erp5_document: {
              "_embedded": {"_view": {
                "my_erp5_url": {
                  "description": "",
                  "title": "Connection Url",
                  "default": gadget.state.erp5_url,
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "erp5_url",
                  "hidden": 0,
                  "type": "StringField"
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
                "top",
                [["my_erp5_url"]]
              ]]
            }
          });
        })
        .push(function () {
          return gadget.getUrlFor({command: 'display', options: {page: 'ojsm_import_export'}});
        })
        .push(function (url) {
          return gadget.updateHeader({
            page_title: "Connect To ERP5 Storage",
            back_url: url,
            submit_action: true,
            panel_action: false
          });
        });
    });
}(window, rJS));
