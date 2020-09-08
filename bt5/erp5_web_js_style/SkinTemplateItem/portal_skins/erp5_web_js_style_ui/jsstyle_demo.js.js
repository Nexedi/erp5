/*globals window, document, RSVP, rJS, domsugar*/
/*jslint indent: 2, maxlen: 80*/
(function () {
  "use strict";

  rJS(window)
    .declareMethod("render", function (parsed_content) {
      var state = {
        language_list: JSON.stringify(parsed_content.language_list || []),
        page_title: parsed_content.page_title || "",
        html_content: parsed_content.html_content || "",
      };
      return this.changeState(state);
    })

    .onStateChange(function (modification_dict) {
      var gadget = this,
        language_list,
        child_list,
        i;

      console.log('modif', modification_dict);

      if (modification_dict.hasOwnProperty('page_title')) {
        document.title = gadget.state.page_title;
      }
      if (modification_dict.hasOwnProperty('html_content')) {
        domsugar(gadget.element.querySelector('main'), {
          html: domsugar('div', {html: gadget.state.html_content}).querySelector('div.input').firstChild.innerHTML
        });
      }
      if (modification_dict.hasOwnProperty('language_list')) {
        language_list = JSON.parse(gadget.state.language_list);
        child_list = [];
        for (i = 0; i < language_list.length; i += 1) {
          child_list.push(domsugar('li', [domsugar('a', {
            text: language_list[i].text,
            href: language_list[i].href
          })]));
        }
        domsugar(gadget.element.querySelector('nav#language'), [domsugar('ul', child_list)]);

      }
    });

}());