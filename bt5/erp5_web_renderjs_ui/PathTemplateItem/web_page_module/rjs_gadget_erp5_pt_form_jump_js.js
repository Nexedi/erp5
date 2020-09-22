/*jslint nomen: true, indent: 2, maxerr: 3 */
/*global window, rJS, RSVP, calculatePageTitle */
(function (window, rJS, RSVP, calculatePageTitle) {
  "use strict";

  function checkValidity() {
    return this.getDeclaredGadget("erp5_form")
      .push(function (declared_gadget) {
        return declared_gadget.checkValidity();
      });
  }

  function getContent() {
    return this.getDeclaredGadget("erp5_form")
      .push(function (sub_gadget) {
        return sub_gadget.getContent();
      });
  }

  function submitDialog() {
    var gadget = this;

    return gadget.getDeclaredGadget("erp5_form")
      .push(function (sub_gadget) {
        return sub_gadget.getContent();
      })
      .push(function (data) {
        return gadget.submitContent(
          gadget.state.jio_key,
          gadget.state.erp5_document._embedded._view._actions.put.href,  // most likely points to Base_jumpToRelatedObject
          data
        );
      })
      .push(function (result) {  // success redirect handler
        var splitted_jio_key_list,
          command,
          result_dict = {};

        if (!result.jio_key) {
          return;
        }
        if (gadget.state.jio_key === result.jio_key) {
          if ((!result.view) || (result.view === 'view')) {
            // Do not redirect to a specific view
            // It may probably mean that there is no document to jump to
            // don't update navigation history when not really redirecting
            command = 'cancel_dialog_with_history';
          } else {
            command = 'display_with_history';
            result_dict.jio_key = gadget.state.jio_key;
            result_dict.view = result.view;
            result_dict.page = "jump";
            result_dict.jump_view = gadget.state.view;
          }
        } else {

          splitted_jio_key_list = result.jio_key.split('/');
          if (splitted_jio_key_list.length < 2) {
            // When going to a module, stick to the current document context,
            // ie, display current document panel/header, but display the module form_list
            // This is implemented by the page "jump"
            command = 'display_with_history';
            result_dict.jio_key = gadget.state.jio_key;
            result_dict.view = result.view;
            result_dict.page = "jump";
            result_dict.jump_view = gadget.state.view;
          } else {
            command = 'push_history';
            result_dict.jio_key = result.jio_key;
            result_dict.view = result.view;
          }
        }

        // forced document change thus we update history
        return gadget.redirect({
          command: command,
          options: result_dict
        });
      });
  }


  var gadget_klass = rJS(window);

  gadget_klass

    /////////////////////////////////////////////////////////////////
    // acquisition
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("submitContent", "submitContent")

    .declareMethod('triggerSubmit', function () {
      return;
    })
    .declareMethod('checkValidity', checkValidity, {mutex: 'changestate'})
    .declareMethod('getContent', getContent, {mutex: 'changestate'})

    .declareMethod('render', function render(options) {
      return this.changeState({
        jio_key: options.jio_key,
        view: options.view,
        erp5_document: options.erp5_document,
        form_definition: options.form_definition,
        erp5_form: options.erp5_form || {},
        action_view: options.action_view
      });
    })

    .declareJob('submit', function () {
      return submitDialog.apply(this);
    })

    .onStateChange(function onStateChange() {
      if (this.state.action_view) {
        throw new Error('nutnut ' + this.state.action_view);
      }
      var form_gadget = this;
      return new RSVP.Queue()
        .push(function () {
          // Render the erp5_from
          return form_gadget.getDeclaredGadget("erp5_form");
        })
        .push(function (erp5_form) {
          var form_options = form_gadget.state.erp5_form;
          // pass own form options to the embedded form
          form_options.erp5_document = form_gadget.state.erp5_document;
          form_options.form_definition = form_gadget.state.form_definition;
          form_options.view = form_gadget.state.view;
          form_options.jio_key = form_gadget.state.jio_key;
          return erp5_form.render(form_options);
        })
        .push(function () {
          // Render the headers
          return RSVP.all([
            form_gadget.getUrlFor({command: 'cancel_dialog_with_history'}),
            calculatePageTitle(form_gadget, form_gadget.state.erp5_document)
          ]);
        })
        .push(function (all_result) {
          return form_gadget.updateHeader({
            cancel_url: all_result[0],
            page_title: all_result[1]
          });
        })
        .push(function () {
          return form_gadget.submit();
        });
    });

}(window, rJS, RSVP, calculatePageTitle));
