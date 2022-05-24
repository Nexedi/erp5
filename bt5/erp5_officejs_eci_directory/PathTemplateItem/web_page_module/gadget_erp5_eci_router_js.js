/*jslint nomen: true, indent: 2, maxerr: 3 */
/*global window, rJS, RSVP, Boolean */
(function (window, rJS, RSVP, Boolean) {
  "use strict";

  rJS(window)

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
    .declareMethod('notify', function (param_list) {
      return this.getDeclaredGadget('router')
        .push(function (router) {
          return router.notify(param_list);
        });
    })
    .declareMethod('redirect', function () {
      var argument_list = arguments;
      return this.getDeclaredGadget("router")
        .push(function (router) {
          return router.redirect.apply(router, argument_list);
        });
    })
    .declareMethod('getCommandUrlFor', function () {
      var argument_list = arguments;
      return this.getDeclaredGadget("router")
        .push(function (router) {
          return router.getCommandUrlFor.apply(router, argument_list);
        });
    })
    .declareMethod('getCommandUrlForList', function () {
      var argument_list = arguments,
        i;
      for (i = 0; i < argument_list[0].length; i += 1) {
        if (argument_list[0][i].hasOwnProperty('options')) {
          if (! argument_list[0][i].options.hasOwnProperty('page') && argument_list[0][i].options.query) {
            argument_list[0][i].options.page = "eci_" + argument_list[0][i].options.query.split(":")[1].split('"')[1];
          }
        }
      }
      return this.getDeclaredGadget("router")
        .push(function (router) {
          return router.getCommandUrlForList.apply(router, argument_list);
        });
    });

}(window, rJS, RSVP, Boolean));