/*global window, rJS, RSVP, jIO, UriTemplate, document, console */
/*jslint indent: 2, maxerr: 3, nomen: true */
(function (window, rJS, RSVP, jIO, UriTemplate, document, console) {
  "use strict";

  function validateEmail(email) {
    var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
  }

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // handle acquisition
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("notifySubmitted", 'notifySubmitted')
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("updateHeader", "updateHeader")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    //.declareMethod("render", function (options) {
    //})

    .onEvent('submit', function (evt) {
      var gadget = this,
        first_name =  document.getElementById("first_name").value,
        last_name =  document.getElementById("last_name").value,
        email =  document.getElementById("email").value;

      function showMessage(msg) {
        document.getElementById("status-message").innerHTML = msg;
      }

      if ((validateEmail(email)) && (first_name) && (last_name)) {
          /* send to server */
        var url =  "ERP5Site_newCredentialRequest?batch_mode=1&reference=" + email + "&default_email_text=" + email + "&first_name=" + first_name + "&last_name=" + last_name;

        return RSVP.Queue()
         .push(function () {
            return jIO.util.ajax({"type": "POST",
                              "url": url,
                              "xhrFields": {withCredentials: true}});
          })
         .push(function (server_response) {
            var response =  server_response.target.response;
            var r = JSON.parse(response),
                msg = r.msg,
                code = r.code;
            if (code === 0) {
              return gadget.notifySubmitted({message: msg, status: 'success'});
            }
            else {
              return gadget.notifySubmitted({message: msg, status: 'error'});              
            }
          }, function (error) {
            return gadget.notifySubmitted({message: 'HTTP ERROR. Registration NOT done.', status: 'error'});
          })
          //if you want to redirect to a specific page after registration:
          /*.push(function () {
            return gadget.redirect({
              command: 'display',
              options: {
                page: "home"
              }
            });
          })*/;
      } else {
        return gadget.notifySubmitted({message: 'bad fields', status: 'error'});
      }
    });


}(window, rJS, RSVP, jIO, UriTemplate, document, console));