/*global window, rJS, RSVP, btoa, XMLHttpRequest, Handlebars, jIO */
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, rJS, RSVP, btoa, XMLHttpRequest, Handlebars, jIO) {
  "use strict";

  var gadget_klass = rJS(window),
    templater = gadget_klass.__template_element,
    notify_msg_template = Handlebars.compile(
      templater.getElementById("template-message-error").innerHTML
    );

  function validateHttpUrl(value) {
    /*jslint regexp: true*/
    if (/\(?(?:(http|https):\/\/)(?:((?:[^\W\s]|\.|-|[:]{1})+)@{1})?((?:www.)?(?:[^\W\s]|\.|-)+[\.][^\W\s]{2,4}|localhost|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|\[[\dabcedf:]+\])(?::(\d*))?([\/]?[^\s\?]*[\/]{1})*(?:\/?([^\s\n\?\[\]\{\}\#]*(?:(?=\.)){1}|[^\s\n\?\[\]\{\}\.\#]*)?([\.]{1}[^\s\?\#]*)?)?(?:\?{1}([^\s\n\#\[\]]*))?([\#][^\s\n]*)?\)?/i.test(value)) {
      return true;
    }
    /*jslint regexp: false*/
    return false;
  }

  function changeMonitorPassword(gadget, base_url, title, basic_login,
      password) {
    var url = base_url,
      jio_gadget;

    url += (url.endsWith('/') ? '' : '/') + 'config/';
    gadget.props.gindex += 1;
    return gadget.declareGadget("gadget_officejs_monitoring_jio.html",
      {element: gadget.element,
        scope: 'jio_' + gadget.props.gindex + "_gadget",
        sandbox: "public"}
      )
      .push(function (new_gadget) {
        jio_gadget = new_gadget;
        return jio_gadget.createJio({
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
      })
      .push(function () {
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
        return new Error("Cannot get document 'config.json' at : " + url);
      })
      .push(function () {
        return {status: 'OK'};
      }, function (error) {
        //console.error(error);
        return {
          status: 'ERROR',
          code: error.status || error.target.status,
          url: base_url,
          title: title
        };
      });
  }

  function testUrl(url, credential_hash) {
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
  }

  function checkCredential(url, title, hash, new_hash) {
    // Verify if login and password are correct for this URL
    if (url === undefined) {
      return {status: 'OK'};
    }
    return testUrl(url, hash)
      .then(function (result) {
        return result;
      }, function (error) {
        var ko_msg = {
            status: 'KO',
            msg: error.msg + ' (' + url + ')',
            title: title
          };
        if (new_hash !== undefined) {
          // saved password is not valid
          // check if inputted password is valid
          return testUrl(url, new_hash)
            .then(function () {
              ko_msg.hash = new_hash;
              return ko_msg;
            }, function () {
              return ko_msg;
            });
        }
        return ko_msg;
      });
  }

  function saveOPML(gadget, doc, verify_password) {
    var opml_dict = {
        type: "opml",
        title: doc.title,
        portal_type: "opml",
        url: doc.url,
        basic_login: btoa(doc.username + ':' + doc.password),
        username: doc.username,
        password: doc.password,
        active: (doc.active === "on") ? true : false,
        has_monitor: true,
        state: doc.state || (doc.active === "on" ? "Started" : "Stopped")
      },
      update_password_list = [],
      allow_force = false;
    gadget.state.message.textContent = "";

    function validateOPML() {
      // read the opml online to get the content and title
      // it also help to make sure that the opml content is valid
      gadget.state.message.textContent = "Reading OPML content...";
      return gadget.state.jio_gadget.createJio({
        type: "query",
        sub_storage: {
          type: "parser",
          document_id: doc.url,
          attachment_id: 'enclosure',
          parser: 'opml',
          sub_storage: {
            type: "http",
            timeout: 25000 // timeout after 25 seconds
          }
        }
      })
        .push(function () {
          return gadget.state.jio_gadget.allDocs({
            select_list: ['title', 'opml_title', 'xmlUrl', 'url']
          });
        })
        .push(undefined, function (error) {
          var message_text,
              code = 0;
          if (error instanceof jIO.util.jIOError) {
            message_text = error.message;
            code = error.status_code;
          } else if (error instanceof TypeError || error.message) {
            message_text = error.message;
          } else {
            code = error.target.status;
            message_text = error.target.responseType === "text" ?
                error.target.statusText : "";
          }
          gadget.state.message
            .innerHTML = notify_msg_template({
              status: 'error',
              message: code + ": Failed to access OPML URL. " +
                message_text
            });
          return {data: {total_rows: 0}};
        })
        .push(function (opml_result) {
          var i,
            check_list = [true],
            new_login;
          if (opml_result.data.total_rows > 0) {
            opml_dict.title = opml_result.data.rows[0].value.title;
            if (doc.new_password) {
              new_login = btoa(doc.username + ':' + doc.new_password);
            }
            for (i = 1; i < opml_result.data.total_rows; i += 1) {
              if (opml_result.data.rows[i].value.url !== undefined) {
                check_list.push(checkCredential(
                  opml_result.data.rows[i].value.url,
                  opml_result.data.rows[i].value.title,
                  opml_dict.basic_login,
                  new_login
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
            error_msg = '',
            used_new_passwd_count = 0;
          // in case the current password in opml is wrong and new
          // password provided is OK, we set it as the current password in opml.
          for (i = 1; i < status_list.length; i += 1) {
            if (status_list[i].status !== 'OK') {
              if (status_list[i].hash !== undefined) {
                used_new_passwd_count += 1;
              }
              error_msg += 'Login/password invalid for instance: ' +
                status_list[i].title + '. ' +
                status_list[i].msg + '\n';
              allow_force = true;
            }
          }
          if (used_new_passwd_count > 0 &&
              used_new_passwd_count === (status_list.length - 1)) {
            // all backends password are OK, we only update our password
            opml_dict.password = doc.new_password;
            doc.new_password = '';
            opml_dict.basic_login = status_list[1].hash;
            return true;
          }
          if (error_msg !== '') {
            gadget.state.message
              .innerHTML = notify_msg_template({
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
            update_promise_list.push(changeMonitorPassword(
              gadget,
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
            .push(function (result_list) {
              var j,
                error_msg = "";
              for (j = 0; j < result_list.length; j += 1) {
                if (result_list[j].status === 'ERROR') {
                  error_msg += 'ERROR ' + result_list[j].code +
                    '. [' + result_list[j].title + '] Failed to ' +
                    'change password, please try again\n';
                }
              }
              if (error_msg !== "") {
                gadget.state.message
                  .innerHTML = notify_msg_template({
                    status: 'error',
                    message: error_msg
                  });
                return false;
              }
              opml_dict.basic_login =
                btoa(doc.username + ':' + doc.new_password);
              opml_dict.password = doc.new_password;
              return true;
            });
        });
    }

    return new RSVP.Queue()
      .push(function () {
        if (verify_password) {
          // if verification pass -> instance is started
          opml_dict.state = "Started";
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
              return {status: status, can_force: allow_force};
            });
        }
        return {status: status, can_force: allow_force};
      });
  }

  gadget_klass
    /////////////////////////////
    // state
    /////////////////////////////
    .setState({
      message: "",
      redirect: false
    })
    /////////////////////////////
    // ready
    /////////////////////////////
    .ready(function (gadget) {
      gadget.props = {gindex: 0};
      return gadget.changeState({
        message: gadget.element.querySelector('.ui-message-alert')
      })
        .push(function () {
          return gadget.getDeclaredGadget("jio_gadget")
            .push(function (jio_gadget) {
              return gadget.changeState({"jio_gadget": jio_gadget});
            });
        });
    })

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("jio_put", "jio_put")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("checkOPMLForm", function (form_doc) {
      var gadget = this;

      if (!validateHttpUrl(form_doc.url)) {
        gadget.state.message
          .innerHTML = notify_msg_template({
            status: 'error',
            message: "'" + form_doc.url + "' is not a valid OPML URL"
          });
        return false;
      }
      if (!form_doc.username || !form_doc.password) {
        gadget.state.message
          .innerHTML = notify_msg_template({
            status: 'error',
            message: 'Username and password are required!'
          });
        return false;
      }
      if (form_doc.new_password &&
          form_doc.new_password !== form_doc.confirm_new_password) {
        gadget.state.message
          .innerHTML = notify_msg_template({
            status: 'error',
            message: 'The new password and it confirmation are differents!'
          });
        return false;
      }
      return true;
    })

    .declareMethod("saveOPML", function (form_doc, verify_password) {
      return saveOPML(this, form_doc, verify_password);
    });

}(window, rJS, RSVP, btoa, XMLHttpRequest, Handlebars, jIO));
