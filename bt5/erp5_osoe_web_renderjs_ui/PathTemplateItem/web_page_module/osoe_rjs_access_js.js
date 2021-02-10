/*jslint indent: 2, maxerr: 3, maxlen: 80 */
/*global window, rJS, RSVP */
(function (window, rJS, RSVP) {
  "use strict";

  rJS(window)
    .declareAcquiredMethod("getTranslationDict", "getTranslationDict")
    .declareMethod('render', function (options) {
      return new RSVP.Queue(RSVP.hash({
        access_gadget: this.getDeclaredGadget('access'),
        translation_dict: this.getTranslationDict([
          'Site Reports',
          'Contribute File',
          'New'
        ])
      }))
        .push(function (result_dict) {
          return result_dict.access_gadget.render(options, [{
            title: result_dict.translation_dict['Site Reports'],
            jio_key: 'portal_types',
            erp5_action: 'list_all_report'
          }, {
            title: result_dict.translation_dict.New,
            jio_key: 'portal_types',
            erp5_action: 'list_all_portal_type_to_create'
          }, {
            title: result_dict.translation_dict['Contribute File'],
            jio_key: 'document_module',
            erp5_action: 'contribute_file'
          }]);
        });
    });

}(window, rJS, RSVP));