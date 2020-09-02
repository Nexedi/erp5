/*globals window, document, RSVP, rJS*/
/*jslint indent: 2, maxlen: 80*/
(function () {
  "use strict";

  rJS(window)
    .declareMethod("render", function (parsed_content) {
      var gadget = this,
        div = document.createElement('div');
      console.log(parsed_content);
      div.innerHTML = parsed_content.html_content;

      document.title = parsed_content.page_title;
      gadget.element.querySelector('main').innerHTML = div.querySelector('div.input').firstChild.innerHTML;
    });

}());