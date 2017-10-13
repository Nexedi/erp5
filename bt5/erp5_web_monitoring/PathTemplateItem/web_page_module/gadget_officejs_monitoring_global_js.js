/*global window, RSVP, btoa */
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, RSVP, btoa) {
  "use strict";

  /* Function used to manage/add/update OPML */

  window.OPMLManage = (function(){
    var gadget,
      self = {};

    self.init = function (rjs_gadget, template_msg) {
      gadget = rjs_gadget;
      gadget.props = {gindex: 0};
      self.notify_msg_template = template_msg;
      return new RSVP.Queue()
        .push(function () {
          return gadget.changeState({
            message: gadget.element.querySelector('.ui-message-alert')
          });
        })
        .push(function () {
          return gadget.getDeclaredGadget("jio_gadget")
            .push(function (jio_gadget) {
              return gadget.changeState({"jio_gadget": jio_gadget});
            });
        });
    };

    self.validateHttpUrl = function (value) {
      /*jslint regexp: true*/
      if (/\(?(?:(http|https):\/\/)(?:((?:[^\W\s]|\.|-|[:]{1})+)@{1})?((?:www.)?(?:[^\W\s]|\.|-)+[\.][^\W\s]{2,4}|localhost|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|\[[\dabcedf:]+\])(?::(\d*))?([\/]?[^\s\?]*[\/]{1})*(?:\/?([^\s\n\?\[\]\{\}\#]*(?:(?=\.)){1}|[^\s\n\?\[\]\{\}\.\#]*)?([\.]{1}[^\s\?\#]*)?)?(?:\?{1}([^\s\n\#\[\]]*))?([\#][^\s\n]*)?\)?/i.test(value)) {
        return true;
      }
      /*jslint regexp: false*/
      return false;
    };

    self.changeMonitorPassword = function (base_url, title, basic_login,
        password) {
      var url = base_url,
        jio_gadget,
        jio_options;

      url += (url.endsWith('/') ? '' : '/') + 'config/';
      gadget.props.gindex += 1;
      return gadget.declareGadget("gadget_officejs_monitoring_jio.html",
          {
            element: gadget.element,
            scope: 'jio_' + gadget.props.gindex + "_gadget",
            sandbox: "public"
          }
        ).push(function(new_gadget) {
          jio_gadget = new_gadget;
          jio_gadget.createJio({
            type: "query",
            sub_storage: {
              type: "drivetojiomapping",
              sub_storage: {
                type: "dav",
                url: url,
                basic_login: basic_login
              }
            }
          });
          return jio_gadget.get('config');
        })
        .push(function (doc) {
          var i;
          if (doc) {
            for (i  = 0; i < doc.length; i += 1) {
              if (doc[i].key === 'monitor-password') {
                doc[i].value = password;
                return jio_gadget.put('config.tmp', doc);
              }
            }
          }
          return new Error("Cannot get document 'config.json' at : " % url);
        })
        .push(function () {
          return {status: 'OK'};
        }, function (error) {
          console.log(error);
          return {
            status: 'ERROR',
            code: error.status || error.target.status,
            url: base_url,
            title: title
          };
        });
    };

    self.checkCredential = function (url, title, hash) {
      var ouput;
      // Verify if login and password are correct for this URL
      if (url === undefined) {
        return {status: 'OK'};
      }
      return self.testUrl(url, hash)
        .then(function(result) {
          return result;
        }, function(error) {
          var ko_msg = {
              status: 'KO',
              msg: error.msg + ' (' + url + ')',
              title: title
            };
          return ko_msg;
        });
    };

    self.testUrl = function (url, credential_hash) {
      // test URL availability!!
      // check that password is valid for that URL
      return new RSVP.Queue()
        .push(function () {
          return new RSVP.Promise(function (resolve, reject) {
            var xhr = new XMLHttpRequest();

            xhr.onload = function (event) {
              var response = event.target;
              if (response.status === 200) {
                resolve({status: 'OK'});
              } else {
                reject({
                  status: 'ERROR',
                  msg: new Error("XHR: " + response.status + ": " + response.statusText)
                });
              }
            };

            xhr.onerror = function (e) {
              reject({
                status: 'ERROR',
                msg: e.target.status + ": " + e.target.statusText
              });
            };

            xhr.open("GET", url, true);
            if (credential_hash !== undefined) {
              xhr.setRequestHeader('Authorization', 'Basic ' + credential_hash);
            }
            xhr.send("");
          });
        });
    };

    self.saveOPML = function (doc, verify_password) {
      var opml_dict = {
          type: "opml",
          title: doc.title,
          portal_type: "opml",
          url: doc.url,
          basic_login: btoa(doc.username + ':' + doc.password),
          username: doc.username,
          password: doc.password,
          active: (doc.active === 1) ? true : false
        },
        update_password_list = [];
      gadget.state.message.textContent = "";

      function validateOPML() {
        // read the opml online to get the content and title
        // it also help to make sure that the opml content is valid
        gadget.state.message.textContent = "Reading OPML content...";
        gadget.state.jio_gadget.createJio({
          type: "query",
          sub_storage: {
            type: "parser",
            document_id: doc.url,
            attachment_id: 'enclosure',
            parser: 'opml',
            sub_storage: {
              type: "http"
            }
          }
        });
        return gadget.state.jio_gadget.allDocs({
          select_list: ['title', 'opml_title', 'xmlUrl', 'url']
        })
          .push(undefined, function (error) {
            gadget.state.message
              .innerHTML = self.notify_msg_template({
                status: 'error',
                message: error.name +
                  ": Failed to access OPML URL. " + error.message
              });
            return {data: {total_rows: 0}};
          })
          .push(function (opml_result) {
            var i,
              check_list = [true];
            if (opml_result.data.total_rows > 0) {
              opml_dict.title = opml_result.data.rows[0].value.title;
              for (i = 1; i < opml_result.data.total_rows; i += 1) {
                if (opml_result.data.rows[i].value.url !== undefined) {
                  check_list.push(self.checkCredential(
                    opml_result.data.rows[i].value.url,
                    opml_result.data.rows[i].value.title,
                    opml_dict.basic_login
                  ));
                  update_password_list.push({
                    base_url: opml_result.data.rows[i].value.url,
                    title: opml_result.data.rows[i].value.title
                  });
                }
              }
              gadget.state.message.textContent = "Validating password(s)...";
              return RSVP.all(check_list);
            }
            return [false];
          })
          .push(function (status_list) {
            var i,
              error_msg = '';
            for (i = 1; i < status_list.length; i += 1) {
              if (status_list[i].status !== 'OK') {
                error_msg += 'Login/password invalid for instance: ' +
                  status_list[i].title + '. ' +
                  status_list[i].msg + '\n';
              }
            }
            if (error_msg !== '') {
              gadget.state.message
                .innerHTML = self.notify_msg_template({
                  status: 'error',
                  message: error_msg
                });
              return false;
            }
            return status_list[0];
          })
          .push(function (previous_status) {
            var i,
              update_promise_list = [];
            if (doc.new_password === "") {
              return previous_status;
            }
            if (!previous_status) {
              return false;
            }
            gadget.state.message.textContent = "Updating password(s)...";
            for (i = 0; i < update_password_list.length; i += 1) {
              update_promise_list.push(self.changeMonitorPassword(
                update_password_list[i].base_url,
                update_password_list[i].title,
                opml_dict.basic_login,
                doc.new_password
              ));
            }
            return new RSVP.Queue()
              .push(function () {
                return RSVP.all(update_promise_list);
              })
              .push(function(result_list) {
                var i,
                  error_msg = "";
                for (i = 0; i < result_list.length; i += 1) {
                  if (result_list[i].status === 'ERROR') {
                    error_msg += 'ERROR ' + result_list[i].code +
                      '. [' + result_list[i].title + '] Failed to ' +
                      'change password, please try again\n';
                  }
                }
                if (error_msg !== "") {
                  gadget.state.message
                    .innerHTML = self.notify_msg_template({
                      status: 'error',
                      message: error_msg
                    });
                  return false;
                } else {
                  opml_dict.basic_login =
                    btoa(doc.username + ':' + doc.new_password);
                  opml_dict.password = doc.new_password;
                  return true;
                }
              });
          });
      }

      return new RSVP.Queue()
        .push(function () {
          if (verify_password) {
            return validateOPML();
          }
          return true;
        })
        .push(function (status) {
          if (status) {
            gadget.state.message.textContent = "Saving OPML...";
            return gadget.jio_put(opml_dict.url, opml_dict)
              .push(function () {
                gadget.state.message.textContent = "";
                return status;
              });
          }
          return status;
        });
    };

    return self;
  })();
}(window, RSVP, btoa));
