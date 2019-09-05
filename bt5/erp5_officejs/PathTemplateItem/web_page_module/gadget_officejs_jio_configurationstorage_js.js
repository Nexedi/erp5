/*jslint indent:2, maxlen: 80, nomen: true */
/*global jIO, RSVP, window, URL, atob */
(function (window, jIO, RSVP, URL, atob) {
  "use strict";

  function decodeDocumentId(id, hateoas_appcache) {
    var hateoas_section,
      hateoas_section_and_view;
    hateoas_section = "./" + hateoas_appcache + "/";
    hateoas_section_and_view = hateoas_section + "definition_view/";
    id = id.replace(hateoas_section_and_view, "");
    id = atob(id);
    return id;
  }

  function processHateoasDict(raw_dict) {
    var raw_field_list, type, parent, field_key, field_id, return_dict = {};
    return_dict.raw_dict = raw_dict;
    /*jslint nomen: true*/
    if (raw_dict.hasOwnProperty("_embedded") &&
        raw_dict._embedded.hasOwnProperty("_view")) {
      raw_field_list = raw_dict._embedded._view;
      type = raw_dict._links.type.name;
      parent = raw_dict._links.parent.name;
      return_dict.parent_relative_url = "portal_types/" + parent;
      return_dict.portal_type = type;
      for (field_key in raw_field_list) {
        if (raw_field_list.hasOwnProperty(field_key)) {
          field_id = "";
          if (raw_field_list[field_key]["default"] !== undefined &&
              raw_field_list[field_key]["default"] !== "") {
            if (field_key.startsWith("my_")) {
              field_id = field_key.replace("my_", "");
            } else if (field_key.startsWith("your_")) {
              field_id = field_key.replace("your_", "");
            } else {
              field_id = field_key;
            }
            return_dict[field_id] = raw_field_list[field_key]["default"];
          }
        }
      }
    } else {
      // ignore non configuration elements
      return raw_dict;
    }
    return return_dict;
  }

  function ConfigurationStorage(spec) {
    if (spec.sub_storage.type !== "appcache") {
      throw new Error("appcache substorage is mandatory for configuration " +
                      "storage");
    }
    this._sub_storage = jIO.createJIO(spec.sub_storage);
    this._hateoas_appcache = spec.hateoas_appcache;
    this._manifest = spec.manifest;
    this._origin_url = spec.origin_url !== undefined ?
        spec.origin_url : window.location.href;
    this._documents = {};
    this._version = spec.version || "";
    this._prefix = spec.prefix || "./";
    this._version = this._prefix + this._version;
  }

  ConfigurationStorage.prototype.get = function (id) {
    if (this._documents.hasOwnProperty(id)) {
      return this._documents[id];
    }
    return this._sub_storage.get.apply(this._sub_storage, arguments);
  };

  ConfigurationStorage.prototype.hasCapacity = function () {
    return true;
  };

  ConfigurationStorage.prototype.getAttachment = function () {
    return this._sub_storage.getAttachment.apply(this._sub_storage, arguments);
  };

  ConfigurationStorage.prototype.allAttachments = function () {
    return this._sub_storage.allAttachments.apply(this._sub_storage, arguments);
  };

  ConfigurationStorage.prototype.buildQuery = function () {
    var result = [],
      promise_list,
      id;
    for (id in this._documents) {
      if (this._documents.hasOwnProperty(id)) {
        result.push({
          'id': id,
          'value': this._documents[id],
          'doc': this._documents[id]
        });
      }
    }
    promise_list = [result];
    promise_list.push(this._sub_storage.buildQuery.apply(this._sub_storage,
                                                         arguments));
    return RSVP.any(promise_list);
  };

  ConfigurationStorage.prototype.repair = function () {
    var storage = this,
      promise_list = [],
      configuration_ids_list = [],
      configuration_id_index = 0,
      url = "",
      attachment_id,
      decoded_id;
    return new RSVP.Queue()
      .push(function () {
        return storage._sub_storage.repair.apply(storage._sub_storage,
                                                 arguments);
      })
      .push(function () {
        url = new URL(storage._manifest, new URL(storage._version,
                                                 storage._origin_url));
        return jIO.util.ajax({
          type: "GET",
          url: url
        });
      })
      .push(function (response) {
        var text = response.target.responseText,
          relative_url_list = text.split('\n'),
          take = false,
          i;
        for (i = 0; i < relative_url_list.length; i += 1) {
          if (relative_url_list[i].indexOf("NETWORK:") >= 0) {
            take = false;
          } else if (relative_url_list[i] !== "" &&
              relative_url_list[i].charAt(0) !== '#' &&
              relative_url_list[i].charAt(0) !== ' ' &&
              take) {
            attachment_id = storage._version + relative_url_list[i];
            decoded_id = decodeDocumentId(attachment_id,
                                          storage._hateoas_appcache);
            promise_list.push(storage._sub_storage.getAttachment(
              storage._origin_url, attachment_id, {"format": "json"}));
            configuration_ids_list[configuration_id_index] = decoded_id;
            configuration_id_index += 1;
          }
          if (relative_url_list[i].indexOf("CACHE:") >= 0) {
            take = true;
          }
        }
        return RSVP.all(promise_list);
      })
      .push(function (content_list) {
        var i, id;
        for (i = 0; i < content_list.length; i += 1) {
          id = configuration_ids_list[i];
          storage._documents[id] = processHateoasDict(content_list[i]);
          //storage._documents[id] = {"new": "content"};
        }
        //storage._documents.couscous = {};
      });
  };

  jIO.addStorage('configuration', ConfigurationStorage);
}(window, jIO, RSVP, URL, atob));
