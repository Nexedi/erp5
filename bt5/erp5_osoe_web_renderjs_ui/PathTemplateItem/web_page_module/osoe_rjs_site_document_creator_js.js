/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80 */
/*global domsugar, window, rJS */
(function (domsugar, window, rJS) {
  "use strict";

  rJS(window)
    .declareAcquiredMethod("notifySubmit", "notifySubmit")
    .declareMethod('render', function (options) {
      return this.changeState({
        key: options.key,
        erp5_add_list: JSON.stringify(options.erp5_add_list)
      });
    })
    .onStateChange(function () {
      var gadget = this,
        erp5_add_list = JSON.parse(gadget.state.erp5_add_list),
        i,
        j,
        k,
        business_application_element_list = [],
        module_element_list;


      for (i = 0; i < erp5_add_list.length; i += 1) {
        module_element_list = [];

        for (j = 0; j < erp5_add_list[i][1].length; j += 1) {
          for (k = 0; k < erp5_add_list[i][1][j][2].length; k += 1) {
            module_element_list.push(
              domsugar('li', [domsugar('button', {
                type: 'submit',
                'data-value': erp5_add_list[i][1][j][1] + ' ' +
                              erp5_add_list[i][1][j][2][k][1],
                text: erp5_add_list[i][1][j][2][k][0]
              })])
            );
          }
        }

        business_application_element_list.push(domsugar('li', [
          domsugar('h2', {
            text: erp5_add_list[i][0]
          }),
          domsugar('ul', module_element_list)
        ]));
      }

      domsugar(gadget.element, [
        domsugar('ul', {'class': 'ui-list-grid'},
                 business_application_element_list)
      ]);

    })

    .declareMethod('getContent', function () {
      var result = {};
      if (this.state.value !== undefined) {
        result[this.state.key] = this.state.value;
      }
      return result;
    }, {mutex: 'changestate'})

    .declareMethod('checkValidity', function () {
      return (this.state.value !== undefined);
    }, {mutex: 'changestate'})

    .onEvent('click', function (evt) {
      if (evt.target.tagName === 'BUTTON') {
        this.state.value = evt.target.getAttribute('data-value');
      }
      return this.notifySubmit();
    }, false);

}(domsugar, window, rJS));