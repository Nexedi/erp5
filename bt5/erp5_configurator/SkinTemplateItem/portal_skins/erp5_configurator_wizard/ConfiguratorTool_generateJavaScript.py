REQUEST = context.REQUEST
active_process_id = REQUEST.get('active_process_id', None)

js_string = """
    // Initialisation
    window.onload = init;

    function getNewXMLHTTP() {
      try {
	    return new XMLHttpRequest();
      } catch(e) {	
  	    try {
  	      var aObj = new ActiveXObject("Msxml2.XMLHTTP");
	    } catch (e) {
	      try {
		    var aObj = new ActiveXObject("Microsoft.XMLHTTP");
	      } catch(e) {
		    return false;
	      }
        }
      }
      return aObj;
    }

    function checkClientInstallation() {
       time_out = window.setTimeout( "checkClientInstallation()", 10000 );
       var xhr_object = null;
       xhr_object = getNewXMLHTTP();
       xhr_object.onreadystatechange = function()
       {
         var status = document.getElementById('client_installation_status');
         if(xhr_object.readyState == 4)
         {
           if(xhr_object.status == 200)
           {
             status.innerHTML = xhr_object.responseText;
           }
           else
             status.innerHTML = "Error code " + xhr_object.status;
         };
       }
       xhr_object.open( "GET",
                        "portal_configurator/getInstallationStatusReport?active_process_id=%s",
                        true);
       //xhr_object.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
       xhr_object.setRequestHeader("Content-Type", "text/html");
       xhr_object.setRequestHeader("Cache-Control", "no-cache" )
       xhr_object.setRequestHeader("If-Modified-Since", "Sat, 1 Jan 2000 00:00:00 GMT" )
       xhr_object.send(null);
    }

    function init() {
      checkClientInstallation();
    }

""" %(active_process_id)

return js_string
