/*global window, rJS, RSVP, document, localStorage */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  window.callFunction = function (options) {
    var fun = window[options.fun];
    return fun.apply(fun, options.argument_list);
  };
  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("updateDocument", "updateDocument")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", 'notifySubmitted')

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("render", function (options) {
      return this.changeState({
        key: options.key,
        value: options.value,
        first_render: true
      });
    })
    .declareMethod("evalCode", function (code) {
      return eval(code);
    })
    .onStateChange(function (modified_dict) {
      this.element.querySelector('script').textContent = this.state.value;
      if (!modified_dict.hasOwnProperty('first_render')) {
        throw new Error('Sorry, it is not possible to dynamically change the iodide content');
      }
      var iodide = document.createElement("script");
      iodide.src = "iodide_master.js";
      this.element.appendChild(iodide);

    })
    .declareMethod("getContent", function () {
      var dict = {};
      dict[this.state.key] = localStorage.getItem('AUTOSAVE: untitled');
      return dict;
    });
}(window, rJS, RSVP));