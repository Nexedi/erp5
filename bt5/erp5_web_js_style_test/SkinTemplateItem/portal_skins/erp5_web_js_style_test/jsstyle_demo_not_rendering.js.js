/*globals window, rJS*/
/*jslint indent: 2, maxlen: 80*/
(function (window, rJS) {
  "use strict";

  rJS(window)
    .declareMethod("render", function () {
      throw new Error('Demo error during render');
    });

}(window, rJS));