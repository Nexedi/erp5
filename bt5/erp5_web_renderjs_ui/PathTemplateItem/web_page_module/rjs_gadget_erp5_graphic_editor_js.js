/*jslint indent: 2, maxerr: 3, maxlen: 100, nomen: true */
/*global window, rJS, domsugar, console, RSVP*/
(function (window, rJS, domsugar, RSVP) {
  "use strict";

  rJS(window)
    //////////////////////////////////////////////
    // acquired method
    //////////////////////////////////////////////
    .declareAcquiredMethod("getTranslationList", "getTranslationList")
    .declareAcquiredMethod("getUrlForList", "getUrlForList")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("trigger", "trigger")

    //////////////////////////////////////////////
    // initialize the gadget content
    //////////////////////////////////////////////
    .declareMethod('render', function render(options) {
      console.log(options);
      return this.changeState({
        "jio_key": options.jio_key,
        "graphic_option_list": options.graphic_option_list
      });
    })

    .onStateChange(function onStateChange(modification_dict) {
      var i,
        option_list = modification_dict.graphic_option_list,
        url_list = [],
        gadget = this;
      console.log(modification_dict);
      console.log(gadget.state);
      for (i = 0; i < option_list.length; i += 1) {
        url_list.push({
          "command": "display_with_history",
          "options": {
            "jio_key": gadget.state.jio_key,
            "graphic_type": option_list[i][0]
          }
        });
      }

      return new RSVP.Queue(
        RSVP.all([
          gadget.getTranslationList([
            'Close',
            'Change Graphic'
          ]),
          gadget.getUrlForList(url_list)
        ])
      )
        .push(function (result_list) {
          var translation_list = result_list[0],
            li_list = [];
          for (i = 0; i < result_list[1].length; i += 1) {
            li_list.push(domsugar("li", [
              domsugar("a", {
                "href": result_list[1][i],
                "text": option_list[i][1]
              })
            ]));
          }
          domsugar(gadget.element.querySelector(".container"), [
            domsugar('div', [
              domsugar('div', {'data-role': 'header', 'class': 'ui-header'}, [
                domsugar('div', {"class": 'ui-btn-left'}, [
                  domsugar('div', {"class": 'ui-controlgroup-controls'}, [
                    domsugar('button', {
                      "type": 'submit',
                      "class": 'close ui-btn-icon-left ui-icon-times',
                      "text": translation_list[0]
                    })
                  ])
                ]),
                domsugar('h1', {"text": translation_list[1]}),
                domsugar('div', {"class": 'ui-btn-left'}, [
                  domsugar('div', {"class": 'ui-controlgroup-controls'}, [
                    domsugar('button')
                  ])
                ])
              ]),
              domsugar("ul", {
                "class": "graphic-listview"
              }, li_list)
            ])
          ]);
        });
    })
    .onEvent('click', function click(evt) {
      if (evt.target.classList.contains('close')) {
        evt.preventDefault();
        return this.trigger();
      }
    }, false, false);

}(window, rJS, domsugar, RSVP));