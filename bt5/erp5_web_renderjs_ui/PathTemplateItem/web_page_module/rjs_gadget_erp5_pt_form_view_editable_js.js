/*global window, rJS, RSVP, calculatePageTitle,
         declareGadgetClassCanHandleListboxClipboardAction */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, calculatePageTitle,
           declareGadgetClassCanHandleListboxClipboardAction) {
  "use strict";

  rJS(window)
    .declareAcquiredMethod("submitContent", "submitContent")
    .declareAcquiredMethod("getUrlForList", "getUrlForList")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("notifyChange", "notifyChange")
    .declareAcquiredMethod('isDesktopMedia', 'isDesktopMedia')
    .declareAcquiredMethod('getUrlParameter', 'getUrlParameter')
    .allowPublicAcquisition("notifyChange", function notifyChange() {
      return this.notifyChange({modified: true});
    })
    /////////////////////////////////////////////////////////////////
    // Proxy methods to the child gadget
    /////////////////////////////////////////////////////////////////
    .declareMethod('checkValidity', function checkValidity() {
      return this.getDeclaredGadget("erp5_form")
        .push(function (declared_gadget) {
          return declared_gadget.checkValidity();
        });
    }, {mutex: 'changestate'})

    .declareMethod('getContent', function getContent() {
      return this.getDeclaredGadget("erp5_form")
        .push(function (declared_gadget) {
          return declared_gadget.getContent();
        });
    }, {mutex: 'changestate'})

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('triggerSubmit', function triggerSubmit() {
      this.element.querySelector('button').click();
    })

    .declareMethod('render', function render(options) {
      var state_dict = {
        jio_key: options.jio_key,
        view: options.view,
        editable: options.editable,
        erp5_document: options.erp5_document,
        form_definition: options.form_definition,
        erp5_form: options.erp5_form || {},
        new_content_action: false,
        delete_action: false,
        save_action: false
      };

      if (options.erp5_document._embedded._view._actions !== undefined) {
        if (options.erp5_document._embedded._view._actions.put !== undefined) {
          state_dict.save_action = true;
        }
      }
      return this.changeState(state_dict);
    })

    .onStateChange(function onStateChange() {
      var gadget = this;

      // render the erp5 form
      return gadget.getDeclaredGadget("erp5_form")
        .push(function (sub_gadget) {
          var form_options = gadget.state.erp5_form;

          form_options.erp5_document = gadget.state.erp5_document;
          form_options.form_definition = gadget.state.form_definition;
          form_options.view = gadget.state.view;
          form_options.jio_key = gadget.state.jio_key;
          form_options.editable = 1;

          return sub_gadget.render(form_options);
        })

        // render the header
        .push(function () {
          var url_for_parameter_list = [
            {command: 'display_dialog_with_history', options: {
              jio_key: gadget.state.jio_key,
              page: "tab",
              view: gadget.state.view
            }},
            {command: 'display_dialog_with_history', options: {
              jio_key: gadget.state.jio_key,
              page: "action",
              view: gadget.state.view
            }},
            {command: 'history_previous'},
            {command: 'selection_previous'},
            {command: 'selection_next'},
            {command: 'display_dialog_with_history', options: {
              jio_key: gadget.state.jio_key,
              page: "export",
              view: gadget.state.view
            }}
          ];
          if (gadget.state.erp5_document._links.action_object_new_content_action) {
            url_for_parameter_list.push({command: 'display_dialog_with_history', options: {
              jio_key: gadget.state.jio_key,
              view: gadget.state.erp5_document._links.action_object_new_content_action.href,
              editable: true
            }});
          }
          return RSVP.all([
            calculatePageTitle(gadget, gadget.state.erp5_document),
            gadget.isDesktopMedia(),
            gadget.getUrlParameter('selection_index'),
            gadget.getUrlForList(url_for_parameter_list)
          ]);
        })
        .push(function (result_list) {
          var url_list = result_list[3],
            header_dict = {
              tab_url: url_list[0],
              actions_url: url_list[1],
              add_url: url_list[6] || '',
              selection_url: url_list[2],
              // Only display previous/next links if url has a selection_index,
              // ie, if we can paginate the result list of the search
              previous_url: result_list[2] ? url_list[3] : '',
              next_url: result_list[2] ? url_list[4] : '',
              page_title: result_list[0]
            };
          if (gadget.state.save_action === true) {
            header_dict.save_action = true;
          }
          if (result_list[1]) {
            header_dict.export_url = (
              gadget.state.erp5_document._links.action_object_jio_report ||
              gadget.state.erp5_document._links.action_object_jio_exchange ||
              gadget.state.erp5_document._links.action_object_jio_print
            ) ? url_list[5] : '';
          }
          return gadget.updateHeader(header_dict);
        });
    })

    .onEvent('submit', function submit() {

      if (this.state.save_action !== true) {
        // If not action is defined on form, do nothing
        return;
      }

      var gadget = this,
        action = gadget.state.erp5_document._embedded._view._actions.put;

      return gadget.getDeclaredGadget("erp5_form")
        .push(function (sub_gadget) {
          return sub_gadget.checkValidity();
        })
        .push(function (is_valid) {
          if (!is_valid) {
            return null;
          }
          return gadget.getContent();
        })
        .push(function (content_dict) {
          if (content_dict === null) {
            return;
          }
          return gadget.submitContent(
            gadget.state.jio_key,
            action.href,
            content_dict
          );
        })
        .push(function (result) {
          if (result.jio_key) {
            // success redirect callback receives jio_key
            return gadget.redirect({command: 'reload'});
          }
        }); // page form handles failures well enough

    }, false, true);

  declareGadgetClassCanHandleListboxClipboardAction(rJS(window));

}(window, rJS, RSVP, calculatePageTitle,
  declareGadgetClassCanHandleListboxClipboardAction));