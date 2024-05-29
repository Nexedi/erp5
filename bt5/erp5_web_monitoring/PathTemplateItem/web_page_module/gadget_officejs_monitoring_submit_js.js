/*global document, window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 10, maxlen: 80 */
(function (document, window, rJS, RSVP) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("redirect", "redirect")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("handle_submit", function (argument_list, options) {
      switch (options.options.portal_type) {
      case "Instance Tree":
        //TODO do the old parameter gadget save here and fix it
        return this.redirect({command: 'reload'});
      case "Opml":
        console.log("opml submit argument_list, options:", argument_list, options);
        //TODO fix submit
        var gadget = this,
          doc,
          opml_gadget;
        return new RSVP.Queue()
          .push(function () {
            return gadget.getDeclaredGadget('opml_gadget');
          })
          .push(function (g) {
            opml_gadget = g;
            return gadget.getDeclaredGadget('form_view');
          })
          .push(function (form_gadget) {
            return form_gadget.getContent();
          })
          .push(function (form_doc) {
            doc = form_doc;
            if (doc.password !== gadget.state.password) {
              // password was modified, update on backend
              doc.new_password = doc.password;
              doc.confirm_new_password = doc.new_password;
              doc.password = gadget.state.password;
              doc.verify_password = 1;
            } else {
              doc.verify_password = (doc.verify_password === "on") ? 1 : 0;
            }
            return opml_gadget.checkOPMLForm(doc);
          })
          .push(function (state) {
            if (state) {
              return gadget.notifySubmitting()
                .push(function () {
                  var verify_opml = doc.title === "" || doc.title === undefined ||
                      doc.verify_password === 1;
                  if (gadget.state.active === false && doc.active === "on") {
                    verify_opml = true;
                  }
                  doc.title = gadget.state.opml_title;
                  return opml_gadget.saveOPML(doc, verify_opml);
                })
                .push(function (state) {
                  var msg = {message: 'Document Updated', status: 'success'};
                  if (!state.status) {
                    msg = {message: 'Document update failed', status: "error"};
                  }
                  return RSVP.all([
                    gadget.notifySubmitted(msg),
                    state
                  ]);
                })
                .push(function (result) {
                  if (result[1].status) {
                    return gadget.changeState({
                      "password": doc.password
                    });
                  }
                });
            }
          });
      default:
        return this.redirect({command: 'reload'});
      }
    });

}(document, window, rJS, RSVP));