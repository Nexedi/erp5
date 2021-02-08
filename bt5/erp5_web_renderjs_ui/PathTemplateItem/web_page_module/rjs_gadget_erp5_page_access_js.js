/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80 */
/*global domsugar, window, rJS */
(function () {
  "use strict";
  // XXX history_previous: prevent getting to erp5 ui by checking the
  // historing or forcing the page value
  // XXX create topic by followup (allDocs group by follow up)

  var URL_DISPLAY_PARAMETER = 'view',
    // DISPLAY_ADD,
    DISPLAY_REPORT = 'display_report',
    DISPLAY_CONTRIBUTE = 'display_contribute',
    MAIN_SCOPE = 'sub_gadget';

  function searchERP5Action(gadget, jio_key, action_name) {
    return gadget.jio_getAttachment(jio_key, 'links')
      .push(function (document_view) {
        var action, action_data, i, j;
        for (i = 0; i < Object.keys(document_view._links).length; i = i + 1) {
          action = Object.keys(document_view._links)[i];
          if (document_view._links.hasOwnProperty(action)) {
            if (document_view._links[action].constructor !== Array) {
              document_view._links[action] = [document_view._links[action]];
            }
            for (j = 0;  j < document_view._links[action].length; j = j + 1) {
              action_data = document_view._links[action][j];
              if (action_data.name === action_name) {
                return action_data.href;
              }
            }
          }
        }
        throw new Error('Action not found: ' + action_name);
      });
  }

  function loadChildGadget(gadget, gadget_url, must_declare, callback) {
    var queue,
      child_gadget;
    if (must_declare) {
      queue = gadget.declareGadget(gadget_url, {scope: MAIN_SCOPE});
    } else {
      queue = gadget.getDeclaredGadget(MAIN_SCOPE);
    }
    return queue
      .push(function (result) {
        child_gadget = result;
        if (callback) {
          return callback(result);
        }
      })
      .push(function (result) {
        if (must_declare) {
          domsugar(gadget.element, [child_gadget.element]);
        }
        return result;
      });
  }

  function renderEmbeddedForm(gadget, jio_key, action_name) {
    return searchERP5Action(gadget, jio_key, action_name)
      .push(function (action_href) {
        return loadChildGadget(gadget, "gadget_erp5_page_form.html",
                               true,
                               function (form_gadget) {
            return form_gadget.render({
              jio_key: jio_key,
              view: action_href
            });
          });
      });
  }

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getTranslationDict", "getTranslationDict")
    .declareAcquiredMethod("getUrlForDict", "getUrlForDict")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")

    .declareMethod('triggerSubmit', function () {
      return;
    })

    .allowPublicAcquisition('updateHeader', function () {
      return;
    })

    ////////////////////////////////////////////////////////////////////
    // Go
    ////////////////////////////////////////////////////////////////////
    .declareMethod('render', function (options) {
      return this.changeState({
        display_step: options[URL_DISPLAY_PARAMETER] || undefined,
        // Force display in any case to refresh the menus
        render_timestamp: new Date().getTime()
      });
    })
    .onStateChange(function () {
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
              command: 'change',
              options: {
                view: DISPLAY_CONTRIBUTE
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
                view: DISPLAY_REPORT
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
          if (gadget.state.display_step === DISPLAY_CONTRIBUTE) {
            return renderEmbeddedForm(gadget,
                                      'document_module',
                                      'contribute_file');
          }
          if (gadget.state.display_step === undefined) {
            return renderEmbeddedForm(gadget,
                                      'portal_contributions',
                                      'create_a_document');
          }
          throw new Error(
            'Unhandled display step: ' + gadget.state.display_step
          );
        });
    });

}());