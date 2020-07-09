/*global rJS, window, navigator*/
/*jslint nomen: true, maxlen:80, indent:2*/
(function (rJS, window, navigator) {
  'use strict';

  rJS(window)
    .declareAcquiredMethod("getTranslationList", "getTranslationList")
    .declareAcquiredMethod("notifyChange", "notifyChange")
    .declareMethod('render', function (options) {
      return this.changeState({
        rss_url: options.rss_url
      });
    })
    .onStateChange(function () {
      var gadget = this;
      return gadget.getDeclaredGadget('text_field')
        .push(function (text_gadget) {
          return text_gadget.render({
            value: gadget.state.rss_url
          });
        });
    })
    .onEvent('click', function (evt) {
      var tag_name = evt.target.tagName,
        gadget = this,
        button_text;

      if (tag_name !== 'BUTTON') {
        return;
      }

      // Disable any button. It must be managed by this gadget
      evt.preventDefault();

      return gadget.getTranslationList(["Copied"])
        .push(function (result) {
          button_text = result[0];
          return navigator.clipboard.writeText(gadget.state.rss_url);
        })
        .push(function () {
          return gadget.notifyChange({
            "message": button_text,
            "status": "success"
          });
        });
    }, false, false);

})(rJS, window, navigator);