/*global RSVP, Handlebars, URI, console */
/*jslint nomen: true, indent: 2, maxerr: 3 */

(function (RSVP, Handlebars, URI) {
  "use strict";
  
  return new RSVP.Queue()
    .push(function () {
      
      Handlebars.registerHelper('has_img', function (object) {
        
        // copied shamelessly from http://stackoverflow.com/a/34695026
        function is_url(str) {
          var a  = document.createElement('a');
          a.href = str;
          //return (a.host && a.host != window.location.host);
          return true;
        }
        
        return (is_url(object.image) || is_url(object.logo));
      });
      
      HandleBars.registerHelper('', function () {
        
      });
      
      HandleBars.registerHelper('', function () {
        
      });
      
      HandleBars.registerHelper('', function () {
        
      });
    });
}(RSVP, Handlebars, URI));