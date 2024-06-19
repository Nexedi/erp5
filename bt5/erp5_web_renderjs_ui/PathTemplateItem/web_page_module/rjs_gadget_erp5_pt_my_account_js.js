/*global window, rJS, domsugar, RSVP */
/*jslint indent: 2, maxerr: 3, nomen: true, maxlen: 80 */
(function (window, rJS, domsugar, RSVP) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // handle acquisition
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("getUrlForDict", "getUrlForDict")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("getTranslationDict", "getTranslationDict")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function () {
      var gadget = this,
        me_relative_url;

      return gadget.getSetting('me')
        .push(function (result) {
          me_relative_url = result;

          return RSVP.hash({
            translation: gadget.getTranslationDict([
              'Active Preference',
              'Preferences',
              'Language',
              'Profile',
              'Logout',
              'My Account'
            ]),
            me: new RSVP.Queue()
              .push(function () {
                if (me_relative_url !== undefined) {
                  return gadget.jio_allDocs({
                    query: 'relative_url:"' + me_relative_url + '"',
                    select_list: ['title'],
                    limit: [0, 1]
                  });
                }
              })
              .push(function (result) {
                var user;
                // Calculate user name
                if (result === undefined) {
                  user = null;
                } else {
                  user = result.data.rows[0].value.title;
                }
                return user;
              }),
            url_dict: gadget.getUrlForDict({
              // Back url
              back: {command: 'history_previous'},
              my_preference: {command: 'push_history',
                              options: {page: "preference"}},
              portal_preference: {command: 'push_history',
                                  options: {jio_key: "portal_preferences"}},
              person: {command: 'push_history',
                        options: {jio_key: me_relative_url}},
              // Change language
              change_language: {command: 'push_history',
                                options: {page: 'language'}},
              logout: {command: 'push_history', options: {page: 'logout'}}
            })
          });
        })
        .push(function (result_dict) {
          domsugar(gadget.element.querySelector('.document_list'), [
            domsugar('ul', {'class': 'document-listview'}, [
              domsugar('li', [
                domsugar('a', {href: result_dict.url_dict.my_preference,
                               text: result_dict.translation['Active Preference']})
              ]),
              domsugar('li', [
                domsugar('a', {href: result_dict.url_dict.portal_preference,
                               text: result_dict.translation.Preferences})
              ]),
              (me_relative_url === undefined) ? '' :
                  domsugar('li', [
                    domsugar('a', {href: result_dict.url_dict.person,
                                   text: result_dict.translation.Profile})
                  ]),
              domsugar('li', [
                domsugar('a', {href: result_dict.url_dict.change_language,
                               text: result_dict.translation.Language})
              ]),
              domsugar('li', [
                domsugar('a', {href: result_dict.url_dict.logout,
                               text: result_dict.translation.Logout})
              ])
            ])
          ]);

          return gadget.updateHeader({
            page_title: result_dict.translation['My Account'] +
                ((result_dict.me === null) ? '' : (': ' + result_dict.me)),
            page_icon: 'sliders',
            front_url: result_dict.url_dict.back
          });

        });
    })

    .declareMethod("triggerSubmit", function () {
      return;
    });
}(window, rJS, domsugar, RSVP));