/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
/**
Page Form is a top-level gadget (a "Page") taking care of rendering form
and handling data send&receive.
*/
(function (window, rJS, RSVP) {
  "use strict";

  rJS(window)

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updatePanel", "updatePanel")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlForList", "getUrlForList")

    .declareMethod("render", function render(options) {
      var gadget = this,
        promise_queue = new RSVP.Queue(),
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
          return gadget.getUrlForList(parameter_list);
        })
        .push(function (href_list) {
          new_state.extra_menu_dict = {
            'Link' : {
              'icon': 'link',
              'action_list': [{
                'title' : 'Contribute',
                'class_name' : 'ui-btn-icon-left ui-icon-file'
              }],
              'href_list': href_list
            }
          };
          return gadget.changeState(new_state);
        });
    })

    .onStateChange(function onStateChange() {
      return this.updatePanel({
        extra_menu_dict: this.state.extra_menu_dict
      });
    });
}(window, rJS, RSVP));