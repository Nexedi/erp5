/*global window, rJS, UriTemplate */
/*jslint indent: 2, maxerr: 3, nomen: true */
(function (window, rJS, UriTemplate, document) {
  "use strict";


  rJS(window)
    /////////////////////////////////////////////////////////////////
    // handle acquisition
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("updateHeader", "updateHeader")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .onEvent('submit', function (evt) {
      var first_name =  document.getElementById("first_name").value,
        last_name =  document.getElementById("last_name").value,
        email =  document.getElementById("email").value;

      function showMessage(msg) {
        document.getElementById("status-message").innerHTML = msg;
      }

      function validateEmail(email) {
         var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
         return re.test(String(email).toLowerCase());
       }
    
      if ((validateEmail(email)) && (first_name) && (last_name)) {
          /* send to server */
         var url =  "ERP5Site_newCredentialRequest?batch_mode=1&reference=" + email + "&default_email_text=" + email + "&first_name=" + first_name + "&last_name=" + last_name;
         jIO.util.ajax({"type": "POST",
                            "url": url,
                            "xhrFields": {withCredentials: true}})
         // XXX: check server response code!
         showMessage("Request was created and will be reviewed shortly. It might take some time to be approved. You will be notified by email.");
      } else {
        showMessage("Invalid first or last name or invalid email address!");
      }

      return evt;
    });

}(window, rJS, UriTemplate, document));