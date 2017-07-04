/*jslint nomen: true, indent: 2, maxerr: 3 */
/*global window, rJS */
(function (window, rJS) {
  "use strict";

  rJS(window)
    /*
    .ready(function (g) {
      return g.getDeclaredGadget("router")
        .push(function (my_default_router) {
          return my_default_router.start();
        });
    })
    */

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('getCommandUrlFor', function () {
      var argument_list = arguments,
        dict = argument_list[0],
        key,
        portal;

      // XXX better way than to extract from query like this?
      if (dict.command === "index") {
        key = dict.options.jio_key;
        portal = dict.options.query.split(":")[1].split('"')[1];
        return "#/" + key + "?page=afs_" + portal + "&view=view";
      }
      return this.getDeclaredGadget("router")
        .push(function (router) {
          return router.getCommandUrlFor.apply(router, argument_list);
        });
    })
    .declareMethod('start', function () {
      var argument_list = arguments;
      return this.getDeclaredGadget("router")
        .push(function (router) {
          return router.start.apply(router, argument_list);
        });
    })
    .declareMethod('route', function () {
      var argument_list = arguments;
      return this.getDeclaredGadget("router")
        .push(function (router) {
          return router.route.apply(router, argument_list);
        });
    })
    .declareMethod('getUrlParameter', function () {
      var argument_list = arguments;
      return this.getDeclaredGadget("router")
        .push(function (router) {
          return router.getUrlParameter.apply(router, argument_list);
        });
    })
    .declareMethod('redirect', function () {
      var argument_list = arguments;
      return this.getDeclaredGadget("router")
        .push(function (router) {
          return router.redirect.apply(router, argument_list);
        });
    });

}(window, rJS));