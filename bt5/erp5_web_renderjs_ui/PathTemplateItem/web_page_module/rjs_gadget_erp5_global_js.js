/*global window, RSVP */
/*jslint indent: 2, maxerr: 3, nomen: true, unparam: true */
(function (window, RSVP) {
  "use strict";

  window.calculatePageTitle = function (gadget, erp5_document) {
    return new RSVP.Queue()
      .push(function () {
        var title = erp5_document.title,
          portal_type = erp5_document._links.type.name;
        if (/ Module$/.test(erp5_document._links.type.href)) {
          return portal_type;
        }
        return portal_type + ': ' + title;
      });
  };

}(window, RSVP));
