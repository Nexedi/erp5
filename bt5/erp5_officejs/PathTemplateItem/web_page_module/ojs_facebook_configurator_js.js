/*global window, rJS, RSVP, URI, location,
    loopEventListener, btoa */
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, rJS, RSVP, console) {
  "use strict";

  function setFacebookConfiguration(gadget, access_token, user_id) {
    return gadget.getSetting("portal_type")
      .push(function (portal_type) {
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
                  //database: "t13-officejs-facebook"
                  database: String(user_id) + "t5-officejs-facebook"
                }
              }
          },
          signature_sub_storage: {
            type: "query",
              sub_storage: {
                type: "uuid",
                sub_storage: {
                  type: "indexeddb",
                  database: String(user_id) + "signature-officejs-facebook"
                }
              }
          },
          remote_sub_storage: {
            type: "query",
            sub_storage: {
              type: "facebook",
              access_token: access_token,
              user_id: user_id,
              default_field_list: ['id', 'message', 'created_time', 'link', 'story']
            }
          }
        }
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
      logged: false,
    })
  .declareAcquiredMethod("updateHeader", "updateHeader")
  .declareAcquiredMethod("redirect", "redirect")
  .declareAcquiredMethod("getSetting", "getSetting")
  .declareAcquiredMethod("setSetting", "setSetting")
  .declareMethod("render", function (options) {
      var gadget = this;
      return gadget.updateHeader({page_title: "Facebook Login"})
  })
  .declareService(function () {
    var gadget = this;
    FB.init({
        appId      : '1917551475189095',
        cookie     : true,
        xfbml      : true,
        version    : 'v2.8'
      });
    FB.getLoginStatus(function(response) {
      if (response.status == 'connected') {
        document.getElementById('status').innerHTML = ' Logged in';
        //gadget.changeState({logged: true});
      }
      else {
        document.getElementById('status').innerHTML = ' Logged out';
      }
      })
  })
    .onStateChange(function (modification_dict) {
      var gadget = this;
      var status;
      if (modification_dict.hasOwnProperty('logged')) {
        if(modification_dict.logged) {
          document.getElementById('status').innerHTML = ' Logged in';
          return setFacebookConfiguration(gadget, FB.getAccessToken(), FB.getUserID());
        }
        else {
          document.getElementById('status').innerHTML = ' Logged out';
        }
      }
    })

    .onEvent("click", function (event) {
      var gadget = this;
      if (event.target.id == 'login') {
        FB.getLoginStatus(function(response) {
          if (response.status == 'connected') {
            gadget.changeState({logged: true});
          }
          else {
            FB.login(function(response) {
              if (response.authResponse) {
                gadget.changeState({logged: true});
              }
            }, {scope: 'user_posts'});
          }
        });
      }
      else if (event.target.id == 'logout') {
        FB.logout(function(response) {
          document.getElementById('status').innerHTML = ' Logged out';
          gadget.changeState({logged: false});
    });
      }
    })
}(window, rJS, RSVP, console));