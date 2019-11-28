/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, rJS, RSVP) {
  "use strict";

  var gadget_klass = rJS(window)

    .declareAcquiredMethod('setSettingList', 'setSettingList')

    .declareMethod('redirect', function (param_list) {
      return this.getDeclaredGadget('erp5_router')
        .push(function (router) {
          return router.redirect(param_list);
        });
    })

    .declareMethod('getUrlParameter', function (param_list) {
      return this.getDeclaredGadget('erp5_router')
        .push(function (router) {
          return router.getUrlParameter(param_list);
        });
    })

    .declareMethod('getCommandUrlFor', function (param_list) {
      return this.getDeclaredGadget('erp5_router')
        .push(function (router) {
          return router.getCommandUrlFor(param_list);
        });
    })

    .declareMethod('getCommandUrlForList', function (param_list) {
      return this.getDeclaredGadget('erp5_router')
        .push(function (router) {
          return router.getCommandUrlForList(param_list);
        });
    })

    .declareMethod('notify', function (param_list) {
      return this.getDeclaredGadget('erp5_router')
        .push(function (router) {
          return router.notify(param_list);
        });
    })

    .declareMethod('start', function () {
      var gadget = this,
        element_list =
          gadget.element.querySelectorAll("[data-renderjs-configuration]"),
        len = element_list.length,
        key,
        value,
        i,
        setting_dict = {},
        queue = new RSVP.Queue();

      for (i = 0; i < len; i += 1) {
        key = element_list[i].getAttribute('data-renderjs-configuration');
        value = element_list[i].textContent;
        setting_dict[key] = value;
      }

      return queue
        .push(function () {
          return gadget.setSettingList(setting_dict);
        })
        .push(function () {
          return gadget.getDeclaredGadget('erp5_router');
        })
        .push(function (router) {
          return router.start();
        });
    });

}(window, rJS, RSVP));