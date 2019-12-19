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
          gadget.state.erp5_document._embedded._view._actions.put.href,  // most likely points to Base_callDialogMethod
          data
        );
      })
      .push(function (result) {  // success redirect handler
        console.log(result);
        throw new Error("couscous");
        var splitted_jio_key_list,
          splitted_current_jio_key_list,
          command,
          i;

        if (!result.jio_key) {
          return;
        }
        if (gadget.state.jio_key === result.jio_key) {
          // don't update navigation history when not really redirecting
          return gadget.redirect({command: 'cancel_dialog_with_history'});
        }
        // Check if the redirection goes to a same parent's subdocument.
        // In this case, do not add current document to the history
        // example: when cloning, do not keep the original document in history
        splitted_jio_key_list = result.jio_key.split('/');
        splitted_current_jio_key_list = gadget.state.jio_key.split('/');
        command = 'display_with_history';
        if (splitted_jio_key_list.length === splitted_current_jio_key_list.length) {
          for (i = 0; i < splitted_jio_key_list.length - 1; i += 1) {
            if (splitted_jio_key_list[i] !== splitted_current_jio_key_list[i]) {
              command = 'push_history';
            }
          }
        } else {
          command = 'push_history';
        }

        // forced document change thus we update history
        return gadget.redirect({
          command: command,
          options: {
            "jio_key": result.jio_key,
            "view": result.view
            // do not mingle with editable because it isn't necessary
          }
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
        erp5_form: options.erp5_form || {}
      });
    })

    .declareJob('submit', function () {
      return submitDialog.apply(this);
    })

    .onStateChange(function onStateChange() {
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
          form_options.editable = true; // dialog is always editable
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
