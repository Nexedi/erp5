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

  /** Return true if the value truly represents an empty value.

  Calling isEmpty(x) is more robust than expression !x.
  */
  function isEmpty(value) {
    return (value === undefined ||
            value === null ||
            value.length === 0);
  }
  window.isEmpty = isEmpty;

  /** Make sure that returned object is an Array instance.
  */
  function ensureArray(obj) {
    if (Array.isArray(obj)) {return obj; }
    if (isEmpty(obj)) {return []; }
    return [obj];
  }
  window.ensureArray = ensureArray;

  /** Return first non-empty variable or the last one.

  Calling getNonEmpy(a, b, "") is more robust way of writing a || b || "".
  Variables coercing to false (e.g 0) do not get skipped anymore.
  */
  function getFirstNonEmpty() {
    var i;
    if (arguments.length === 0) {
      return null;
    }
    for (i = 0; i < arguments.length; i++) {
      if (!isEmpty(arguments[i])) {
        return arguments[i];
      }
    }
    if (arguments.length === 1) {
      return arguments[0];
    }
    return arguments[arguments.length - 1];
  }
  window.getFirstNonEmpty = getFirstNonEmpty;

}(window, RSVP));