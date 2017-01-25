/*global window, RSVP, FileReader */
/*jslint indent: 2, maxerr: 3, unparam: true */
(function (window, RSVP) {
  "use strict";

  window.getWorkflowState = function (options)  {
    var sync_state,
      readonly = false;
    if(options.jio_key.indexOf("_module/") > 0){
      sync_state = "Synced";
      readonly = true;
    }else if(options.doc.sync_flag){
      sync_state = "Not Synced";
      if (options.doc.state) {
        readonly = true;
      }
    }else{
      sync_state = "Not Ready To Sync";
    }
    return {sync_state: sync_state, readonly: readonly};
  };
  
  window.geoLocationPromise = function() {
    return new Promise(function (resolve, reject) {
      var err;
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function (result) {
          resolve(result);
        }, function (error) {
          switch(error.code) {
            case error.PERMISSION_DENIED:
              err = new Error("User denied the request for Geolocation");
              break;
            case error.POSITION_UNAVAILABLE:
              err =  new Error("Location information is unavailable");
              break;
            case error.TIMEOUT:
              err = new Error("The request to get user location timed out");
              break;
            default:
              err = new Error("An unknown error occurred");
              break;
          }
          reject(err);
        },
        {maximumAge:60000, timeout:20000});
      } else {
        reject(new Error("Geolocation is not supported by this browser"));
    }
    });
  };
  window.getSequentialID = function (gadget, record_type_prefix){
    var last_sequential_id,
      prefix,
      date = new Date(),
      date_text = date.getFullYear()+('0'+(date.getMonth()+1)).slice(-2)+('0'+date.getDate()).slice(-2);
    return new RSVP.Queue()
      .push(function () {
        if (gadget.options.doc.source_reference) {
          return gadget.options.doc.source_reference;
        } else {
          return new RSVP.Queue()
            .push(function () {
              return new RSVP.all([
                gadget.getSetting('last_sequential_id'),
                gadget.getSetting('sequential_id_prefix')
              ]);
            })
           .push(function (result_list) {
             if (result_list[0]) {
              last_sequential_id = Number(result_list[0]);
             } else {
              last_sequential_id = 0;
             }
            last_sequential_id += 1;
            if (result_list[1]) {
              prefix = result_list[1];
            } else {
             prefix = getRandomPrefixForID();
            }
            return gadget.setSetting('sequential_id_prefix', prefix);
           })
           .push(function () {
             return gadget.setSetting('last_sequential_id', last_sequential_id);
           })
          .push(function () {
           return record_type_prefix + '-' + date_text + '-' + prefix + ('0000'+last_sequential_id).slice(-5);
          });
        }
      });
  };
  
  window.getRandomPrefixForID = function(){
    function random(){
      return 65 + Math.floor( Math.random() * 26 );
    }
    return String.fromCharCode(random())+String.fromCharCode(random())+String.fromCharCode(random());
  };
}(window, RSVP));