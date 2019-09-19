/*jslint indent:2, maxlen: 80, nomen: true */
/*global jIO, RSVP, window, URL, atob, btoa, Rusha */
(function (window, jIO, RSVP, URL, atob, btoa, Rusha) {
  "use strict";

  var rusha = new Rusha();

  function decodeDocumentId(id, hateoas_appcache) {
    var hateoas_section,
      hateoas_section_and_view;
    hateoas_section = "./" + hateoas_appcache + "/";
    hateoas_section_and_view = hateoas_section + "definition_view/";
    id = id.replace(hateoas_section_and_view, "");
    id = atob(id);
    return id;
  }

  function encodeDocumentId(id, hateoas_appcache) {
    var hateoas_section,
      hateoas_section_and_view;
    id = btoa(id);
    hateoas_section = "./" + hateoas_appcache + "/";
    hateoas_section_and_view = hateoas_section + "definition_view/";
    id = hateoas_section_and_view + id;
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
    this._version = spec.version || "";
    this._prefix = spec.prefix || "./";
    this._version = this._prefix + this._version;
    this._hash = "";
  }

  ConfigurationStorage.prototype.get = function (id) {
    var storage = this;
    id = encodeDocumentId(id, storage._hateoas_appcache);
    return storage._sub_storage.getAttachment(storage._origin_url,
                                              id,
                                              {"format": "json"})
      .push(function (content) {
        content = processHateoasDict(content);
        content.hash = storage._hash;
        return content;
      });
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
    var storage = this,
      result = [],
      decoded_id,
      attachment_id;
    return storage.allAttachments(storage._origin_url)
      .push(function (all_attachments) {
        for (attachment_id in all_attachments) {
          if (all_attachments.hasOwnProperty(attachment_id)) {
            if (attachment_id !== storage._version &&
                attachment_id !== storage._version + "/" &&
                attachment_id !== storage._version + storage._manifest) {
              decoded_id = decodeDocumentId(attachment_id,
                                            storage._hateoas_appcache);
              result.push({
                'id': decoded_id,
                'value': {hash: storage._hash},
                'doc': {hash: storage._hash}
              });
            }
          }
        }
        return result;
      });
  };

  ConfigurationStorage.prototype.repair = function (app_version) {
    var storage = this,
      url = new URL(storage._manifest, new URL(storage._version,
                                               storage._origin_url));
    return new RSVP.Queue()
      .push(function () {
        return jIO.util.ajax({
          type: "GET",
          url: url
        });
      })
      .push(function (response) {
        var text = response.target.responseText;
        //hash is attached to manifest text and app version
        //if the app version has changed, then a cleanup was done in the storage
        //documents must be updated to restore any potential missing document
        storage._hash = rusha.digestFromString(text + app_version);
        return storage._sub_storage.repair.apply(storage._sub_storage,
                                                 arguments);
      });
  };

  jIO.addStorage('configuration', ConfigurationStorage);
}(window, jIO, RSVP, URL, atob, btoa, Rusha));
