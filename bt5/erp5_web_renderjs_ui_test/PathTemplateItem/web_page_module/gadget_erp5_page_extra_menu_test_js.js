/*global window, rJS, RSVP, ensureArray*/
/*jslint nomen: true, indent: 2, maxerr: 3 */
/**
Page Form is a top-level gadget (a "Page") taking care of rendering form
and handling data send&receive.
*/
(function (window, rJS, RSVP, ensureArray) {
  "use strict";

  rJS(window)

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updatePanel", "updatePanel")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlForList", "getUrlForList")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")

    .declareMethod("render", function render(options) {
      var gadget = this,
        new_state = {
          options: options
        },
        parameter_list = [{
          command: 'display_erp5_action_with_history',
          options: {
            jio_key: 'document_module',
            page: 'contribute_file',
            keep_history: true
          }
        }];
      return gadget.updateHeader({page_title: "Extra Menu"})
        .push(function () {
          if (options.jio_key) {
            return gadget.jio_getAttachment(options.jio_key,
                                            options.view);
          }
        })
        .push(function (result) {
          new_state.erp5_document = result;
          return gadget.getUrlForList(parameter_list);
        })
        .push(function (href_list) {
          new_state.extra_menu_list = [{
            'title' : 'Contribute',
            'href': href_list[0],
            'active': true
          }];
          return gadget.changeState(new_state);
        });
    })

    .onStateChange(function onStateChange() {
      var gadget = this;
      return gadget.updatePanel({
        extra_menu_list: gadget.state.extra_menu_list,
        jio_key: gadget.state.options.jio_key,
        erp5_document: gadget.state.erp5_document,
        view_list: []
      });
    });
}(window, rJS, RSVP, ensureArray));