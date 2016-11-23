/*jslint browser:true */
function displayMessage() {
    "use strict";
    var wizard_message = document.getElementById("wizard_message");
    wizard_message.style.visibility = "visible";
    if (!(/MSIE/).test(navigator.userAgent)) {
        if (scrapeText(wizard_message) === "true") {
            wizard_message.innerHTML = "<a href='next'>Please click here to access ERP5 Express Configuration service.</a>";
        } else {
            wizard_message.innerHTML = "You can not access ERP5 Express Configuration service.";
        }
    } else {
        wizard_message.innerHTML = "<a href='http://www.mozilla.com/firefox/'>Please click here to download Firefox, because your browser may not work properly. It is free.</a>";
    }
}
addLoadEvent(displayMessage);