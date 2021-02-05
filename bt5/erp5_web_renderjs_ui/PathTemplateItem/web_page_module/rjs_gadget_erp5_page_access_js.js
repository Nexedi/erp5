/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80, continue:true */
/*global a */
(function () {
  "use strict";
  // XXX history_previous: prevent getting to erp5 ui by checking the
  // historing or forcing the page value
  // XXX create topic by followup (allDocs group by follow up)

  var URL_DISPLAY_PARAMETER = 'view',
    DISPLAY_ADD = 'display_add',
    DISPLAY_REPORT = 'display_report',
    DISPLAY_CONTRIBUTE = 'display_contribute';

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getTranslationDict", "getTranslationDict")
    .declareAcquiredMethod("getUrlForDict", "getUrlForDict")

    .declareMethod('triggerSubmit', function () {
      return;
    })

    ////////////////////////////////////////////////////////////////////
    // Go
    ////////////////////////////////////////////////////////////////////
    .declareMethod('render', function (options) {
      return this.changeState({
        display_step: options[URL_DISPLAY_PARAMETER] || DISPLAY_ADD,
        // Force display in any case to refresh the menus
        render_timestamp: new Date().getTime()
      });
    })
    .onStateChange(function (modification_dict) {
      var gadget = this,
        _;
      return gadget.getTranslationDict(['Home'])
        .push(function (translation_dict) {
          _ = translation_dict;
          return gadget.getUrlForDict({
            front_url: {
              command: 'history_previous'
            },
            upload_url: {
              command: 'display_erp5_action_with_history',
              options: {
                jio_key: 'document_module',
                page: 'contribute_file'
              }
            },
            add_url: {
              command: 'change',
              options: {
                view: undefined
              }
            },
            export_url: {
              command: 'change',
              options: {
                view: 'export'
              }
            }
          });
        })
        .push(function (url_dict) {
          url_dict.page_title = _.Home;
          url_dict.page_icon = 'home';
          return gadget.updateHeader(url_dict);
        })

        .push(function () {
          if (gadget.state.display_step === DISPLAY_ADD) {
            throw new Error('not implemented ' + DISPLAY_ADD);
            return renderDiscussionThreadList(
              gadget,
              modification_dict.hasOwnProperty('display_step')
            );
          } else {
            throw new Error(
              'Unhandled display step: ' + gadget.state.display_step
            );
          }
        });
    });

}());