/*global window, rJS, RSVP, URI, location,
    loopEventListener, btoa, FB */
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, rJS, RSVP, FB) {
  "use strict";

  function setFacebookConfiguration(gadget, access_token, user_id) {
    return new RSVP.Queue()
      .push(function () {
        var configuration = {};
        configuration = {
          type: "replicate",
          use_remote_post: false,
          conflict_handling: 2,
          check_local_modification: false,
          check_local_creation: false,
          check_local_deletion: false,
          check_remote_modification: true,
          check_remote_creation: true,
          check_remote_deletion: true,
          signature_hash_key: 'updated_time',
          parallel_operation_amount: 16,
          local_sub_storage: {
            type: "query",
            sub_storage: {
              type: "uuid",
              sub_storage: {
                type: "indexeddb",
                database: user_id + "t5-officejs-facebook"
              }
            }
          },
          signature_sub_storage: {
            type: "query",
            sub_storage: {
              type: "uuid",
              sub_storage: {
                type: "indexeddb",
                database: user_id + "signature-officejs-facebook"
              }
            }
          },
          remote_sub_storage: {
            type: "query",
            sub_storage: {
              type: "cachealldocs",
              default_field_list: ['id', 'message', 'created_time', 'link', 'story'],
              sub_storage: {
                type: "facebook",
                access_token: access_token,
                user_id: user_id,
                default_field_list: ['id', 'message', 'created_time', 'link', 'story']
              }
            }
          }
        };
        return gadget.setSetting('jio_storage_description', configuration);
      })
      .push(function () {
        return gadget.setSetting('jio_storage_name', "FACEBOOK");
      })
      .push(function () {
        return gadget.setSetting('sync_reload', true);
      })
      .push(function () {
        return gadget.redirect({
          command: "display",
          options: {page: 'ojs_sync', auto_repair: 'true'}
        });
      });
  }

  var gadget_klass = rJS(window);

  gadget_klass
    .setState({
      logged: false
    })
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("setSetting", "setSetting")
    .declareMethod("render", function () {
      var gadget = this;
      return gadget.updateHeader({page_title: "Facebook Login"});
    })
    .declareService(function () {
      var gadget = this;
      FB.init({
        appId      : '1917551475189095',
        cookie     : true,
        xfbml      : true,
        version    : 'v2.8'
      });
      FB.getLoginStatus(function (response) {
        if (response.status === 'connected') {
          gadget.element.querySelector("span").textContent = ' Logged in';
        } else {
          gadget.element.querySelector("span").textContent = ' Logged out';
        }
      });
    })
    .onStateChange(function (modification_dict) {
      var gadget = this;
      if (modification_dict.hasOwnProperty('logged')) {
        if (modification_dict.logged) {
          gadget.element.querySelector("span").textContent = ' Logged in';
          return setFacebookConfiguration(gadget, FB.getAccessToken(), FB.getUserID());
        }
        gadget.element.querySelector("span").textContent = ' Logged out';
      }
    })

    .onEvent("click", function (event) {
      var gadget = this;
      if (event.target.getAttribute('data-i18n') === 'Log In') {
        FB.getLoginStatus(function (response) {
          if (response.status === 'connected') {
            gadget.changeState({logged: true});
          } else {
            FB.login(function (response) {
              if (response.authResponse) {
                gadget.changeState({logged: true});
              }
            }, {scope: 'user_posts'});
          }
        });
      } else if (event.target.getAttribute('data-i18n') === 'Log Out') {
        FB.logout(function () {
          gadget.element.querySelector("span").textContent = ' Logged out';
          gadget.changeState({logged: false});
        });
      }
    });
}(window, rJS, RSVP, FB));