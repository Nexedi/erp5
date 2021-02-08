/*jslint indent: 2, maxerr: 3, maxlen: 80 */
/*global window, rJS, RSVP */
(function (window, rJS, RSVP) {
  "use strict";

  rJS(window)
    .declareAcquiredMethod("getTranslationDict", "getTranslationDict")
    .declareMethod('render', function (options) {
      return new RSVP.Queue(RSVP.hash({
        access_gadget: this.getDeclaredGadget('access'),
        translation_dict: this.getTranslationDict(['Contribute', 'New'])
      }))
        .push(function (result_dict) {
          return result_dict.access_gadget.render(options, [{
            title: result_dict.translation_dict.New,
            jio_key: 'portal_contributions',
            erp5_action: 'create_a_document'
          }, {
            title: result_dict.translation_dict.Contribute,
            jio_key: 'document_module',
            erp5_action: 'contribute_file'
          }]);
        });
    });

}(window, rJS, RSVP));