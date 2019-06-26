/*global window, rJS, RSVP, URI */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, document) {
  "use strict";
  function data_lake(context, evt) {
    var link = document.createElement('a');
    link.href = window.location.origin + "/erp5/web_site_module/fif_data_runner/#/?page=fifdata";
    link.click();
  }

  rJS(window)
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareJob('data_lake', function (evt) {
      return data_lake(this, evt);
    })
    .declareMethod("render", function () {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return gadget.updateHeader({
            page_title: 'Wendelin Data Lake Sharing Platform'
          });
        })
        .push(undefined, function (error) {
          throw error;
        });
    })
    .onEvent('submit', function (evt) {
      if (evt.target.name === 'data-lake') {
        return this.data_lake(evt);
      } else {
        throw new Error('Unknown form');
      }
    });
}(window, rJS, RSVP, document));