/*globals window, document, RSVP, rJS, domsugar*/
/*jslint indent: 2, maxlen: 80*/
(function () {
  "use strict";

  rJS(window)
    .setState({
      render_count: 0
    })
    .ready(function () {
      var gadget = this;
      // Check if the gadget is reloaded when changing the language
      return gadget.getPath()
        .push(function (url) {
          return gadget.changeState({gadget_style_url: url});
        });
    })
    .declareMethod("render", function (parsed_content) {
      var state = {
        language_list: JSON.stringify(parsed_content.language_list || []),
        page_title: parsed_content.page_title || "",
        html_content: parsed_content.html_content || "",
        render_count: this.state.render_count + 1
      };
      return this.changeState(state);
    })

    .onStateChange(function (modification_dict) {
      var gadget = this,
        language_list,
        child_list,
        i;

      if (modification_dict.hasOwnProperty('page_title')) {
        document.title = gadget.state.page_title;
      }
      if (modification_dict.hasOwnProperty('html_content')) {
        domsugar(gadget.element.querySelector('main'), {
          html: domsugar('div', {html: gadget.state.html_content}).querySelector('div.input').firstChild.innerHTML
        });
      }
      if (modification_dict.hasOwnProperty('gadget_style_url')) {
        domsugar(gadget.element.querySelector('p#gadget_style_url'), {
          text: gadget.state.gadget_style_url
        });
      }
      if (modification_dict.hasOwnProperty('render_count')) {
        domsugar(gadget.element.querySelector('p#render_count'), {
          text: 'render count: ' + gadget.state.render_count
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