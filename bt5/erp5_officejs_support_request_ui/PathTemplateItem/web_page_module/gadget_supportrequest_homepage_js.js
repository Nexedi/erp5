/*global window, rJS, RSVP, URI*/
/*jslint indent: 2, maxerr: 3, nomen: true */
(function (window, rJS, RSVP, URI) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // handle acquisition
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")

    .allowPublicAcquisition('updateHeader', function () {
      return;
    })
    .allowPublicAcquisition('getUrlParameter', function (argument_list) {
      return this.getUrlParameter(argument_list)
        .push(function (result) {
          if ((result === undefined) && (
              (argument_list[0] === 'field_listbox_support_request_sort_list:json') ||
                (argument_list[0] === 'field_listbox_task_report_sort_list:json')
            )) {
            return [['modification_date', 'descending']];
          }
          return result;
        });
    })
    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function () {
      var gadget = this;
      // We want to force the user to log in right after opening the app if not already logged in.
      // This can be done by access something which needs credential in the home page, which must force user to login.
      // The line in below is a way to cheat, because there has nothing to do with this fetched information.
      // When we truely show some confidential things in the homepage on future, we can remove this line.
      gadget.jio_getAttachment('support_request_module', 'links');
      return gadget.updateHeader({page_title: 'Support Requests Home Page'});
    })
    .onEvent('submit', function () {
      var form_gadget = this,
        form_id,
        action;

      return form_gadget.notifySubmitting()
        .push(function () {
          return form_gadget.jio_getAttachment('support_request_module', 'links');
        })
        .push(function (links) {
          var create_content_url = links._links.action_object_new_content_action.href;
          return form_gadget.jio_getAttachment('support_request_module', create_content_url);
        })
        .push(function (erp5_doc) {
          action = erp5_doc._embedded._view._actions.put;
          form_id = erp5_doc._embedded._view.form_id;
        })
        .push(function () {
          var data = {};

          data[form_id.key] = form_id['default'];
          // XXX Hardcoded
          data.dialog_id = form_id['default'];
          data.dialog_method = action.action;
          //XXX hack for redirect, difined in form
          data.field_your_portal_type = "Support Request";

          return form_gadget.jio_putAttachment(
            "support_request_module",
            action.href,
            data
          );
        })
        .push(function (evt) {
          var location = evt.target.getResponseHeader("X-Location"),
            jio_key,
            list = [],
            message;
          try {
            message = JSON.parse(evt.target.response).portal_status_message;
          } catch (ignore) {
          }
          list.push(form_gadget.notifySubmitted(message));

          if (location === undefined || location === null) {
            // No redirection, stay on the same document
            list.push(form_gadget.redirect({command: 'change', options: {view: "view", page: undefined, editable: form_gadget.state.editable}}));
          } else {
            jio_key = new URI(location).segment(2);
            if (form_gadget.state.id === jio_key) {
              // Do not update navigation history if dialog redirect to the same document
              list.push(form_gadget.redirect({command: 'change', options: {jio_key: jio_key, view: "view", page: undefined, editable: form_gadget.state.editable}}));
            } else {
              list.push(form_gadget.redirect({command: 'push_history', options: {jio_key: jio_key, editable: form_gadget.state.editable}}));
            }
          }
          return RSVP.all(list);
        });
    });
}(window, rJS, RSVP, URI));