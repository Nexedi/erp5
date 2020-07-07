/*global rJS, window, navigator, RSVP*/
/*jslint nomen: true, maxlen:80, indent:2*/
(function (rJS, window, navigator, RSVP) {
  'use strict';

  rJS(window)
    .declareAcquiredMethod("getTranslationList", "getTranslationList")
    .declareAcquiredMethod("nofitySubmited", "nofitySubmited")
    .declareMethod('render', function (options) {
      return this.changeState({
        rss_url: options.rss_url
      });
    })
    .declareMethod('getContent', function () {
      return {"your_rss_url": this.state.rss_url};
    })
    .onEvent(
      'click',
      function (evt) {
        var gadget = this,
          root = this.element,
          button_text;
        evt.preventDefault();
        return gadget.getTranslationList(["Copied"])
          .push(function (result) {
            button_text = result[0];
            return navigator.clipboard.writeText(gadget.state.rss_url);
          })
          .push(function () {
            return gadget.nofitySubmited(button_text);
          });
      },
      false,
      false
    );

}(rJS, window, navigator, RSVP));