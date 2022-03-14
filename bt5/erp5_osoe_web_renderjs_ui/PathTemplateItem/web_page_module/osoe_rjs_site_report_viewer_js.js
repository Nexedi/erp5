/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80 */
/*global domsugar, window, rJS, RSVP */
(function (domsugar, window, rJS, RSVP) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getTranslationDict", "getTranslationDict")
    .declareAcquiredMethod("getUrlForDict", "getUrlForDict")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")

    .declareMethod('triggerSubmit', function () {
      return;
    })

    .allowPublicAcquisition('updateHeader', function () {
      return;
    })
    .allowPublicAcquisition('updatePanel', function () {
      return;
    })

    ////////////////////////////////////////////////////////////////////
    // Go
    ////////////////////////////////////////////////////////////////////
    .declareMethod('render', function (options) {
      var gadget = this,
        erp5_report_list = options.erp5_report_list,
        i,
        j,
        k,
        business_application_element_list = [],
        module_element_list,
        url_for_dict = {};

      for (i = 0; i < erp5_report_list.length; i += 1) {
        for (j = 0; j < erp5_report_list[i][1].length; j += 1) {
          for (k = 0; k < erp5_report_list[i][1][j][2].length; k += 1) {
            url_for_dict[erp5_report_list[i][1][j][1] +
                         erp5_report_list[i][1][j][2][k][1]] = {
              command: 'display_erp5_dialog_with_history',
              options: {
                jio_key: erp5_report_list[i][1][j][1],
                page: erp5_report_list[i][1][j][2][k][1]
              }
            };
          }
        }
      }

      return new RSVP.Queue(gadget.getUrlForDict(url_for_dict))
        .push(function (url_dict) {

          for (i = 0; i < erp5_report_list.length; i += 1) {
            module_element_list = [];

            for (j = 0; j < erp5_report_list[i][1].length; j += 1) {
              module_element_list.push(
                domsugar('li', [domsugar('h3', {
                  text: erp5_report_list[i][1][j][0]
                })])
              );

              for (k = 0; k < erp5_report_list[i][1][j][2].length; k += 1) {
                module_element_list.push(
                  domsugar('li', [domsugar('a', {
                    href: url_dict[erp5_report_list[i][1][j][1] +
                                   erp5_report_list[i][1][j][2][k][1]],
                    text: erp5_report_list[i][1][j][2][k][0]
                  })])
                );
              }
            }

            business_application_element_list.push(domsugar('li', [
              domsugar('h2', {
                text: erp5_report_list[i][0]
              }),
              domsugar('ul', module_element_list)
            ]));
          }

          domsugar(gadget.element, [
            domsugar('ul', {'class': 'ui-list-grid'},
                     business_application_element_list)
          ]);
        });

    });

}(domsugar, window, rJS, RSVP));