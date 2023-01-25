/*jslint nomen: true, indent: 2, maxerr: 3 */
/*global window, rJS, RSVP, Boolean */
(function (window, rJS, RSVP, Boolean) {
  "use strict";

  rJS(window)
    .declareAcquiredMethod('renderApplication', 'renderApplication')
    .declareAcquiredMethod('jio_get', 'jio_get')
    .allowPublicAcquisition("renderApplication", function (param_list) {
      var gadget = this;
      if (param_list[0].url === "gadget_erp5_page_form.html") {
        return gadget.jio_get(param_list[0].options.jio_key)
          .push(function (result) {
            param_list[0].options.page = 'eci_' + result.portal_type;
            param_list[0].url = param_list[0].url.replace('form', param_list[0].options.page);
            return gadget.renderApplication(...param_list);
          });
      }
      return gadget.renderApplication(...param_list);
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
      var argument_list = arguments;
      return this.getDeclaredGadget("router")
        .push(function (router) {
          return router.getCommandUrlForList.apply(router, argument_list);
        });
    });

}(window, rJS, RSVP, Boolean));