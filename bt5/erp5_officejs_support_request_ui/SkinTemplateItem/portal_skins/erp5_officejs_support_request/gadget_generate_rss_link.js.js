/*global rJS, window, navigator*/
/*jslint nomen: true, maxlen:80, indent:2*/
(function (rJS, window, navigator) {
  'use strict';

  rJS(window)
    .declareAcquiredMethod("getTranslationList", "getTranslationList")
    .declareAcquiredMethod("notifySubmit", "notifySubmit")
    .declareMethod('render', function (options) {
      return this.changeState({
        rss_url: options.rss_url
      });
    })
    .declareMethod('getContent', function () {
      var gadget = this,
        button_text;
      return gadget.getTranslationList(["Copied"])
        .push(function (result) {
          button_text = result[0];
          return navigator.clipboard.writeText(gadget.state.rss_url);
        })
        .push(function () {
          return gadget.notifySubmit(button_text);
        });
    });
}(rJS, window, navigator));