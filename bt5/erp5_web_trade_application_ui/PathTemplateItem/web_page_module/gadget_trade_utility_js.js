/*jslint indent: 2, nomen: true, maxlen: 80*/

function getRandomPrefixForID() {
  "use strict";
  function random() {
    return 65 + Math.floor(Math.random() * 26);
  }
  return String.fromCharCode(random())
    + String.fromCharCode(random())
    + String.fromCharCode(random());
}

function getSequentialID(gadget, record_type_prefix) {
  "use strict";
  var prefix, last_sequential_id;
  return gadget.getSetting("last_sequential_id")
    .push(function (result) {
      if (result === undefined) {
        last_sequential_id = 0;
      } else {
        last_sequential_id = Number(result);
      }
      last_sequential_id += 1;
      return gadget.setSetting("last_sequential_id", last_sequential_id);
    })
    .push(function () {
      return gadget.getSetting("sequential_id_prefix");
    })
    .push(function (result) {
      if (result === undefined) {
        prefix = getRandomPrefixForID();
        return gadget.setSetting("sequential_id_prefix", prefix);
      }
      prefix = result;
    })
    .push(function () {
      var date = new Date(),
        date_text = date.getFullYear()
          + ('0' + (date.getMonth() + 1)).slice(-2)
          + ('0' + date.getDate()).slice(-2);
      return record_type_prefix + '-' + date_text
        + '-' + prefix + ('0000' + last_sequential_id).slice(-5);
    });
}