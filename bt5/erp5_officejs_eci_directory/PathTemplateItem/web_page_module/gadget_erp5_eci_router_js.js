/*jslint nomen: true, indent: 2, maxerr: 3 */
/*global window, rJS, RSVP, Boolean */
(function (window, rJS, RSVP, Boolean) {
  "use strict";

  rJS(window)

    .declareAcquiredMethod("getUrlFor", "getUrlFor")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('getCommandUrlForList', function (options_list) {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          var cmd_index = "index";
          var result_list = options_list.map(function (opt) {
            if (opt.command === cmd_index) {
              return gadget.getUrlFor({command: "display", options: {
                  jio_key: opt.options.jio_key,
                  page: "eci_" + opt.options.query.split(":")[1].split('"')[1],
                  view: "view"
                }
              });
            }
          }).filter(Boolean);
          if (result_list.length) {
            return RSVP.all(result_list);
          }
          return gadget.getDeclaredGadget("router")
            .push(function (router) {
              return router.getCommandUrlForList.apply(router, [options_list]);
            });
        });
    })
    .declareMethod('getCommandUrlFor', function () {
      var argument_list = arguments,
        dict = argument_list[0],
        key,
        portal;

      // XXX better way than to extract from query like this?
      if (dict.command === "index") {
        //key = dict.options.jio_key;
        //portal = dict.options.query.split(":")[1].split('"')[1];
        //return "#/" + key + "?page=afs_" + portal + "&view=view";
        return this.getUrlFor({command: "index", options: {
          jio_key: dict.options.jio_key,
          page: "afs_" + dict.options.query.split(":")[1].split('"')[1],
          view: "view"
        }});
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
    });

}(window, rJS, RSVP, Boolean));