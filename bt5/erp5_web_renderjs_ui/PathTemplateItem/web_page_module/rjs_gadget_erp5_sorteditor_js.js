/*jslint indent: 2, maxerr: 3, nomen: true */
/*global window, rJS, domsugar*/
(function (window, rJS, domsugar) {
  "use strict";

  function createSortItemTemplate(sort_value_list, sort_column_list, ascending_text, descending_text) {
    var dom_column_option_list = [],
      option_dict,
      is_selected = false,
      i;

    for (i = 0; i < sort_column_list.length; i += 1) {
      is_selected = is_selected || (sort_value_list[0] === sort_column_list[i][0]);
      option_dict = {
        value: sort_column_list[i][0],
        // Used to be translated
        text: sort_column_list[i][1]
      };
      if (sort_value_list[0] === sort_column_list[i][0]) {
        option_dict.selected = "selected";
      }
      dom_column_option_list.push(domsugar('option', option_dict));
    }

    if (!is_selected && (sort_value_list.length !== 0)) {
      dom_column_option_list.push(domsugar('option', {
        text: sort_value_list[0],
        value: sort_value_list[0],
        selected: true
      }));
    }

    return domsugar('div', [
      domsugar('button', {type: 'submit', class: 'ui-icon ui-icon-minus'}),
      domsugar('div', {class: 'sort_item ui-controlgroup-controls'}, [
        domsugar('select', dom_column_option_list),
        domsugar('select', [
          domsugar('option', {
            value: 'ascending',
            text: ascending_text,
            selected: (sort_value_list[1] === 'ascending')
          }),
          domsugar('option', {
            value: 'descending',
            text: descending_text,
            selected: (sort_value_list[1] === 'descending')
          })
        ])
      ])
    ]);
  }

  /* Valid sort item is a tuple of (column-name, ordering) */
  function isValidSortItem(sort_item) {
    return sort_item.length === 2 &&
           (sort_item[1] === 'ascending' || sort_item[1] === 'descending');
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
        'Sort Editor',
        'Close',
        'Add Criteria',
        'Reset',
        'ascending',
        'descending'
      ])
        .push(function (translation_list) {
          var sort_dom_list = gadget.state.sort_list
            .filter(isValidSortItem)
            .map(function (sort_item) {
              return createSortItemTemplate(
                sort_item,
                gadget.state.sort_column_list,
                translation_list[5],
                translation_list[6]
              );
            });

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
                domsugar('div', {class: 'sort_item_container'},
                         sort_dom_list),
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
        sort_column_list: options.sort_column_list || [],
        key: options.key,
        sort_list: options.sort_list
      });
    })

    .onEvent('click', function click(evt) {
      var gadget = this;

      if (evt.target.classList.contains('trash')) {
        evt.preventDefault();
        domsugar(gadget.element.querySelector(".sort_item_container"), []);
      }

      if (evt.target.classList.contains('close')) {
        evt.preventDefault();
        return this.trigger();
      }

      if (evt.target.classList.contains('plus')) {
        evt.preventDefault();
        return gadget.getTranslationList([
          'ascending',
          'descending'
        ])
          .push(function (translation_list) {
            return gadget.element.querySelector(".sort_item_container")
                                 .appendChild(
                createSortItemTemplate(
                  [],
                  gadget.state.sort_column_list,
                  translation_list[0],
                  translation_list[1]
                )
              );

          });
      }

      if (evt.target.classList.contains('ui-icon-minus')) {
        evt.preventDefault();
        evt.target.parentElement.parentElement.removeChild(evt.target.parentElement);
      }

    }, false, false)

    .onEvent('submit', function submit() {
      var gadget = this,
        sort_list = gadget.element.querySelectorAll(".sort_item"),
        sort_query = [],
        select_list,
        sort_item,
        options = {},
        i;

      for (i = 0; i < sort_list.length; i += 1) {
        sort_item = sort_list[i];
        select_list = sort_item.querySelectorAll("select");
        sort_query[i] = [select_list[0][select_list[0].selectedIndex].value,
          select_list[1][select_list[1].selectedIndex].value];
      }
      if (i === 0) {
        options[gadget.state.key] = undefined;
      } else {
        options[gadget.state.key] = sort_query;
      }
      return gadget.redirect({
        command: 'store_and_change',
        options: options
      }, true);
    });

}(window, rJS, domsugar));