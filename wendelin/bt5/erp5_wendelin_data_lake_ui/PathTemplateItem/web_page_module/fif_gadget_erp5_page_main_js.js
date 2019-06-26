/*global window, rJS, RSVP, URI */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  rJS(window)
    .declareAcquiredMethod("updateHeader", "updateHeader")

    .declareMethod("render", function () {
      var gadget = this;
      return new RSVP.Queue()
        /*.push(function () {
            return gadget.jio_allDocs({
              query: 'portal_type:"Data Array"' +
                     ' AND validation_state:"validated"',
              select_list: ["title", "reference"],
              limit: [0, 1000000]
            });
          })*/
        .push(function () {
          return gadget.getDeclaredGadget("gadget_fif_page_list_dataset");
        })
        .push(function (my_gadget) {
          return my_gadget.render();
        })
        .push(function () {
          return gadget.updateHeader({
            page_title: 'Wendelin Data Lake Sharing Platform'
          });
        })
        .push(undefined, function (error) {
          throw error;
        });
    });
}(window, rJS, RSVP));