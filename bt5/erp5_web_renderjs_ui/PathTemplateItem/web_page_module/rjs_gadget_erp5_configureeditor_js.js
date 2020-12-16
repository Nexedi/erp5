/*jslint indent: 2, maxerr: 3, nomen: true */
/*global window, rJS, domsugar*/
(function (window, rJS, domsugar) {
  "use strict";

  function createColumnItemTemplate(column_value, displayable_column_list) {
    var column_value_list = column_value || [],
      dom_option_list = [],
      option_dict,
      i;

    for (i = 0; i < displayable_column_list.length; i += 1) {
      option_dict = {
        value: displayable_column_list[i][0],
        // Used to be translated
        text: displayable_column_list[i][1]
      };
      if (column_value_list[0] === option_dict.value) {
        option_dict.selected = "selected";
      }
      dom_option_list.push(domsugar('option', option_dict));
    }

    return domsugar('div', [
      domsugar('button', {class: 'ui-icon ui-icon-minus'}),
      domsugar('div', {class: 'column_item ui-controlgroup-controls'}, [
        domsugar('select', dom_option_list)
      ])
    ]);
  }

  rJS(window)
    //////////////////////////////////////////////
    // acquired method
    //////////////////////////////////////////////
    .declareAcquiredMethod("getTranslationList", "getTranslationList")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("trigger", "trigger")

    .onStateChange(function onStateChange() {
      var gadget = this;

      return gadget.getTranslationList([
        'Submit',
        'Configure Editor',
        'Close',
        'Add Criteria',
        'Reset'
      ])
        .push(function (translation_list) {
          var column_dom_list =
              gadget.state.column_list.map(
                function (column_item) {
                  return createColumnItemTemplate(
                    column_item,
                    gadget.state.displayable_column_list
                  );
                }
              );

          domsugar(gadget.element.querySelector(".container"), [
            domsugar('div', [
              domsugar('div', {'data-role': 'header', 'class': 'ui-header'}, [
                domsugar('div', {class: 'ui-btn-right'}, [
                  domsugar('div', {class: 'ui-controlgroup-controls'}, [
                    domsugar('button', {
                      type: 'submit',
                      class: 'submit ui-btn-icon-left ui-icon-check',
                      text: translation_list[0]
                    })
                  ])
                ]),
                domsugar('h1', {text: translation_list[1]}),
                domsugar('div', {class: 'ui-btn-left'}, [
                  domsugar('div', {class: 'ui-controlgroup-controls'}, [
                    domsugar('button', {
                      type: 'submit',
                      class: 'close ui-btn-icon-left ui-icon-times',
                      text: translation_list[2]
                    })
                  ])
                ])
              ]),
              domsugar('section', [
                domsugar('div', {class: 'column_item_container'},
                         column_dom_list),
                domsugar('button', {
                  class: 'plus ui-icon-plus ui-btn-icon-left',
                  text: translation_list[3]
                }),
                domsugar('button', {
                  class: 'trash ui-icon-trash-o ui-btn-icon-left',
                  text: translation_list[4]
                })

              ])
            ])
          ]);

        });
    })

    .declareMethod('render', function render(options) {
      return this.changeState({
        column_list: options.column_list,
        displayable_column_list: options.displayable_column_list,
        key: options.key
      });
    })

    .onEvent('click', function click(evt) {
      var gadget = this;

      if (evt.target.classList.contains('trash')) {
        evt.preventDefault();
        domsugar(gadget.element.querySelector(".column_item_container"));
      }

      if (evt.target.classList.contains('close')) {
        evt.preventDefault();
        return this.trigger();
      }

      if (evt.target.classList.contains('plus')) {
        evt.preventDefault();
        return gadget.element.querySelector(".column_item_container")
                             .appendChild(
            createColumnItemTemplate(undefined,
                                     gadget.state.displayable_column_list)
          );
      }

      if (evt.target.classList.contains('ui-icon-minus')) {
        evt.preventDefault();
        evt.target.parentElement.parentElement.removeChild(evt.target.parentElement);
      }

    }, false, false)

    .onEvent('submit', function submit(evt) {
      var gadget = this,
        options = {},
        form = evt.target,
        i,
        field,
        column_list = [];
      for (i = 0; i < form.elements.length; i += 1) {
        field = form.elements[i];
        if (field.nodeName.toUpperCase() === 'SELECT') {
          column_list.push(field.value);
        }
      }
      if (column_list.length === 0) {
        options[gadget.state.key] = undefined;
      } else {
        // Remove duplicated elements (same column should not be displayed twice)
        column_list = column_list.filter(function (el, i, a) {
          return i === a.indexOf(el);
        });

        options[gadget.state.key] = column_list;
      }

      return gadget.redirect({
        command: 'store_and_change',
        options: options
      }, true);
    });

}(window, rJS, domsugar));