/*jslint indent: 2 */
/*global window, rJS, RSVP, curConfig, svgCanvas */
(function (window, rJS, RSVP) {
  "use strict";

  curConfig.jGraduatePath = "lib/jgraduate/images/";  // XXX images are not loaded at the good place

  rJS(window)
    .ready(function (g) {
      g.props = {};
      var deferred = RSVP.defer();
      svgCanvas.ready(function () {
        deferred.resolve();
      });
      return deferred.promise;
    })
    .declareMethod('render', function (options) {
      [].forEach.call(window.document.head.querySelectorAll("base"), function (el) {
        // XXX GadgetField adds <base> tag to fit to the parent page location, it's BAD to remove them.
        //     In the case of method-draw, all component are loaded dynamicaly through ajax requests in
        //     method-draw "folder". By setting a <base> tag, we change the url resolution behavior, and
        //     we break all dynamic links. So, deleting <base> is required.
        window.document.head.removeChild(el);
      });
      this.props.key = options.key;
      svgCanvas.setSvgString(options.value);
    })
    .declareService(function () {
      if (/(?:^\?|&)auto_focus=(true|1)(?:&|$)/.test(window.location.search)) {
        window.focus();  // should be done by the parent gadget?
      }
    })
    .declareMethod('getContent', function () {
      var form_data = {};
      form_data[this.props.key] = svgCanvas.getSvgString();
      return form_data;
    });

}(window, rJS, RSVP));
