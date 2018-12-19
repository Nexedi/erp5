/*jslint indent:2, maxlen: 80, nomen: true */
/*global jIO, RSVP, UriTemplate, SimpleQuery, ComplexQuery, QueryFactory,
  Query, FormData*/
(function (jIO, RSVP, UriTemplate, SimpleQuery, ComplexQuery, QueryFactory,
  Query, FormData) {
  "use strict";

  function getSubIdEqualSubProperty(storage, value, key) {
    var query;
    if (storage._no_sub_query_id) {
      throw new jIO.util.jIOError('no sub query id active', 404);
    }
    query = new SimpleQuery({
      key: key,
      value: value,
      type: "simple"
    });
    if (storage._query.query !== undefined) {
      query = new ComplexQuery({
        operator: "AND",
        query_list: [query, storage._query.query],
        type: "complex"
      });
    }
    query = Query.objectToSearchText(query);
    return storage._sub_storage.allDocs({
      "query": query,
      "sort_on": storage._query.sort_on,
      "select_list": storage._query.select_list,
      "limit": storage._query.limit
    })
      .push(function (data) {
        if (data.data.rows.length === 0) {
          throw new jIO.util.jIOError(
            "Can not find id",
            404
          );
        }
        if (data.data.rows.length > 1) {
          throw new TypeError("id must be unique field: " + key
            + ", result:" + data.data.rows.toString());
        }
        return data.data.rows[0].id;
      });
  }

  /*jslint unparam: true*/
  var mapping_function = {
    "equalSubProperty": {
      "mapToSubProperty": function (property, sub_doc, doc, args, id) {
        sub_doc[args] = doc[property];
        return args;
      },
      "mapToMainProperty": function (property, sub_doc, doc, args, sub_id) {
        if (sub_doc.hasOwnProperty(args)) {
          doc[property] = sub_doc[args];
        }
        return args;
      },
      "mapToSubId": function (storage, doc, id, args) {
        if (doc !== undefined) {
          if (storage._property_for_sub_id &&
              doc.hasOwnProperty(storage._property_for_sub_id)) {
            return doc[storage._property_for_sub_id];
          }
        }
        return getSubIdEqualSubProperty(storage, id, storage._map_id[1]);
      },
      "mapToId": function (storage, sub_doc, sub_id, args) {
        return sub_doc[args];
      }
    },
    "equalValue": {
      "mapToSubProperty": function (property, sub_doc, doc, args) {
        sub_doc[property] = args;
        return property;
      },
      "mapToMainProperty": function (property) {
        return property;
      }
    },
    "ignore": {
      "mapToSubProperty": function () {
        return false;
      },
      "mapToMainProperty": function (property) {
        return property;
      }
    },
    "equalSubId": {
      "mapToSubProperty": function (property, sub_doc, doc) {
        sub_doc[property] = doc[property];
        return property;
      },
      "mapToMainProperty": function (property, sub_doc, doc, args, sub_id) {
        if (sub_id === undefined && sub_doc.hasOwnProperty(property)) {
          doc[property] = sub_doc[property];
        } else {
          doc[property] = sub_id;
        }
        return property;
      },
      "mapToSubId": function (storage, doc, id, args) {
        return id;
      },
      "mapToId": function (storage, sub_doc, sub_id) {
        return sub_id;
      }
    },
    "keep": {
      "mapToSubProperty": function (property, sub_doc, doc) {
        sub_doc[property] = doc[property];
        return property;
      },
      "mapToMainProperty": function (property, sub_doc, doc) {
        doc[property] = sub_doc[property];
        return property;
      }
    },
    "switchPropertyValue": {
      "mapToSubProperty": function (property, sub_doc, doc, args) {
        sub_doc[args[0]] = args[1][doc[property]];
        return args[0];
      },
      "mapToMainProperty": function (property, sub_doc, doc, args) {
        var subvalue, value = sub_doc[args[0]];
        for (subvalue in args[1]) {
          if (args[1].hasOwnProperty(subvalue)) {
            if (value === args[1][subvalue]) {
              doc[property] = subvalue;
              return property;
            }
          }
        }
      }
    }
  };
  /*jslint unparam: false*/

  function initializeQueryAndDefaultMapping(storage) {
    var property, query_list = [];
    for (property in storage._mapping_dict) {
      if (storage._mapping_dict.hasOwnProperty(property)) {
        if (storage._mapping_dict[property][0] === "equalValue") {
          if (storage._mapping_dict[property][1] === undefined) {
            throw new jIO.util.jIOError("equalValue has not parameter", 400);
          }
          storage._default_mapping[property] =
            storage._mapping_dict[property][1];
          query_list.push(new SimpleQuery({
            key: property,
            value: storage._mapping_dict[property][1],
            type: "simple"
          }));
        }
        if (storage._mapping_dict[property][0] === "equalSubId") {
          if (storage._property_for_sub_id !== undefined) {
            throw new jIO.util.jIOError(
              "equalSubId can be defined one time",
              400
            );
          }
          storage._property_for_sub_id = property;
        }
      }
    }
    if (storage._query.query !== undefined) {
      query_list.push(QueryFactory.create(storage._query.query));
    }
    if (query_list.length > 1) {
      storage._query.query = new ComplexQuery({
        type: "complex",
        query_list: query_list,
        operator: "AND"
      });
    } else if (query_list.length === 1) {
      storage._query.query = query_list[0];
    }
  }

  function MappingStorage(spec) {
    this._mapping_dict = spec.property || {};
    this._sub_storage = jIO.createJIO(spec.sub_storage);
    this._map_all_property = spec.map_all_property !== undefined ?
        spec.map_all_property : true;
    this._no_sub_query_id = spec.no_sub_query_id;
    this._attachment_mapping_dict = spec.attachment || {};
    this._query = spec.query || {};
    this._map_id = spec.id || ["equalSubId"];
    this._id_mapped = (spec.id !== undefined) ? spec.id[1] : false;
    this._attachment_list = spec.attachment_list || [];

    if (this._query.query !== undefined) {
      this._query.query = QueryFactory.create(this._query.query);
    }
    this._default_mapping = {};

    initializeQueryAndDefaultMapping(this);
  }

  function getAttachmentId(storage, sub_id, attachment_id, method) {
    var mapping_dict = storage._attachment_mapping_dict;
    if (mapping_dict !== undefined
        && mapping_dict[attachment_id] !== undefined
        && mapping_dict[attachment_id][method] !== undefined) {
      if (mapping_dict[attachment_id][method].uri_template !== undefined) {
        return UriTemplate.parse(
          mapping_dict[attachment_id][method].uri_template
        ).expand({id: sub_id});
      }
    }
    return attachment_id;
  }

  function getSubStorageId(storage, id, doc) {
    return new RSVP.Queue()
      .push(function () {
        var map_info = storage._map_id || ["equalSubId"];
        if (storage._property_for_sub_id && doc !== undefined &&
            doc.hasOwnProperty(storage._property_for_sub_id)) {
          return doc[storage._property_for_sub_id];
        }
        return mapping_function[map_info[0]].mapToSubId(
          storage,
          doc,
          id,
          map_info[1]
        );
      });
  }

  function mapToSubProperty(storage, property, sub_doc, doc, id) {
    var mapping_info = storage._mapping_dict[property] || ["keep"];
    return mapping_function[mapping_info[0]].mapToSubProperty(
      property,
      sub_doc,
      doc,
      mapping_info[1],
      id
    );
  }

  function mapToMainProperty(storage, property, sub_doc, doc, sub_id) {
    var mapping_info = storage._mapping_dict[property] || ["keep"];
    return mapping_function[mapping_info[0]].mapToMainProperty(
      property,
      sub_doc,
      doc,
      mapping_info[1],
      sub_id
    );
  }

  function mapToMainDocument(storage, sub_doc, sub_id) {
    var doc = {},
      property,
      property_list = [storage._id_mapped];
    for (property in storage._mapping_dict) {
      if (storage._mapping_dict.hasOwnProperty(property)) {
        property_list.push(mapToMainProperty(
          storage,
          property,
          sub_doc,
          doc,
          sub_id
        ));
      }
    }
    if (storage._map_all_property) {
      for (property in sub_doc) {
        if (sub_doc.hasOwnProperty(property)) {
          if (property_list.indexOf(property) < 0) {
            doc[property] = sub_doc[property];
          }
        }
      }
    }
    if (storage._map_for_sub_storage_id !== undefined) {
      doc[storage._map_for_sub_storage_id] = sub_id;
    }
    return doc;
  }

  function mapToSubstorageDocument(storage, doc, id) {
    var sub_doc = {}, property;

    for (property in doc) {
      if (doc.hasOwnProperty(property)) {
        mapToSubProperty(storage, property, sub_doc, doc, id);
      }
    }
    for (property in storage._default_mapping) {
      if (storage._default_mapping.hasOwnProperty(property)) {
        sub_doc[property] = storage._default_mapping[property];
      }
    }
    if (storage._map_id[0] === "equalSubProperty" && id !== undefined) {
      sub_doc[storage._map_id[1]] = id;
    }
    return sub_doc;
  }

  function handleAttachment(storage, argument_list, method) {
    return getSubStorageId(storage, argument_list[0])
      .push(function (sub_id) {
        argument_list[0] = sub_id;
        var old_id = argument_list[1];
        argument_list[1] = getAttachmentId(
          storage,
          argument_list[0],
          argument_list[1],
          method
        );
        if (storage._attachment_list.length > 0
            && storage._attachment_list.indexOf(old_id) < 0) {
          if (method === "get") {
            throw new jIO.util.jIOError("unhautorized attachment", 404);
          }
          return;
        }
        return storage._sub_storage[method + "Attachment"].apply(
          storage._sub_storage,
          argument_list
        );
      });
  }

  MappingStorage.prototype.get = function (id) {
    var storage = this;
    return getSubStorageId(this, id)
      .push(function (sub_id) {
        return storage._sub_storage.get(sub_id)
          .push(function (sub_doc) {
            return mapToMainDocument(storage, sub_doc, sub_id);
          });
      });
  };

  MappingStorage.prototype.post = function (doc) {
    var sub_doc = mapToSubstorageDocument(
      this,
      doc
    ),
      id = doc[this._property_for_sub_id];
    if (this._property_for_sub_id && id !== undefined) {
      return this._sub_storage.put(id, sub_doc);
    }
    if (!this._id_mapped || doc[this._id_mapped] !== undefined) {
      return this._sub_storage.post(sub_doc);
    }
    throw new jIO.util.jIOError(
      "post is not supported with id mapped",
      400
    );
  };

  MappingStorage.prototype.put = function (id, doc) {
    var storage = this,
      sub_doc = mapToSubstorageDocument(this, doc, id);
    return getSubStorageId(this, id, doc)
      .push(function (sub_id) {
        return storage._sub_storage.put(sub_id, sub_doc);
      })
      .push(undefined, function (error) {
        if (error instanceof jIO.util.jIOError && error.status_code === 404) {
          return storage._sub_storage.post(sub_doc);
        }
        throw error;
      })
      .push(function () {
        return id;
      });
  };

  MappingStorage.prototype.remove = function (id) {
    var storage = this;
    return getSubStorageId(this, id)
      .push(function (sub_id) {
        return storage._sub_storage.remove(sub_id);
      })
      .push(function () {
        return id;
      });
  };

  MappingStorage.prototype.putAttachment = function (id, attachment_id, blob) {
    var storage = this,
      mapping_dict = storage._attachment_mapping_dict;
    // THIS IS REALLY BAD, FIND AN OTHER WAY IN FUTURE
    if (mapping_dict !== undefined
        && mapping_dict[attachment_id] !== undefined
        && mapping_dict[attachment_id].put !== undefined
        && mapping_dict[attachment_id].put.erp5_put_template !== undefined) {
      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            getSubStorageId(storage, id),
            storage.get(id)
          ]);
        })
        .push(function (result) {
          var sub_id = result[0],
            doc = result[1],
            url = UriTemplate.parse(
              mapping_dict[attachment_id].put.erp5_put_template
            ).expand({id: sub_id}),
            data = new FormData();
          if (doc.filename) {
            data.append("field_my_file", blob, doc.filename);
          } else {
            data.append("field_my_file", blob);
          }
          data.append("form_id", "File_view");
          return jIO.util.ajax({
            "type": "POST",
            "url": url,
            "data": data,
            "xhrFields": {
              withCredentials: true
            }
          });
        });
    }
    return handleAttachment(this, arguments, "put", id)
      .push(function () {
        return attachment_id;
      });
  };

  MappingStorage.prototype.getAttachment = function () {
    return handleAttachment(this, arguments, "get");
  };

  MappingStorage.prototype.removeAttachment = function (id, attachment_id) {
    return handleAttachment(this, arguments, "remove", id)
      .push(function () {
        return attachment_id;
      });
  };

  MappingStorage.prototype.allAttachments = function (id) {
    var storage = this, sub_id;
    return getSubStorageId(storage, id)
      .push(function (sub_id_result) {
        sub_id = sub_id_result;
        return storage._sub_storage.allAttachments(sub_id);
      })
      .push(function (result) {
        var attachment_id,
          attachments = {},
          mapping_dict = {},
          i;
        for (attachment_id in storage._attachment_mapping_dict) {
          if (storage._attachment_mapping_dict.hasOwnProperty(attachment_id)) {
            mapping_dict[getAttachmentId(storage, sub_id, attachment_id, "get")]
              = attachment_id;
          }
        }
        for (attachment_id in result) {
          if (result.hasOwnProperty(attachment_id)) {
            if (!(storage._attachment_list.length > 0
                && storage._attachment_list.indexOf(attachment_id) < 0)) {
              if (mapping_dict.hasOwnProperty(attachment_id)) {
                attachments[mapping_dict[attachment_id]] = {};
              } else {
                attachments[attachment_id] = {};
              }
            }
          }
        }
        for (i = 0; i < storage._attachment_list.length; i += 1) {
          if (!attachments.hasOwnProperty(storage._attachment_list[i])) {
            attachments[storage._attachment_list[i]] = {};
          }
        }
        return attachments;
      });
  };

  MappingStorage.prototype.hasCapacity = function (name) {
    return this._sub_storage.hasCapacity(name);
  };

  MappingStorage.prototype.repair = function () {
    return this._sub_storage.repair.apply(this._sub_storage, arguments);
  };

  MappingStorage.prototype.bulk = function (id_list) {
    var storage = this;

    function mapId(parameter) {
      return getSubStorageId(storage, parameter.parameter_list[0])
        .push(function (id) {
          return {"method": parameter.method, "parameter_list": [id]};
        });
    }

    return new RSVP.Queue()
      .push(function () {
        var promise_list = id_list.map(mapId);
        return RSVP.all(promise_list);
      })
      .push(function (id_list_mapped) {
        return storage._sub_storage.bulk(id_list_mapped);
      })
      .push(function (result) {
        var mapped_result = [], i;
        for (i = 0; i < result.length; i += 1) {
          mapped_result.push(mapToMainDocument(
            storage,
            result[i]
          ));
        }
        return mapped_result;
      });
  };

  MappingStorage.prototype.buildQuery = function (option) {
    var storage = this,
      i,
      query,
      property,
      select_list = [],
      sort_on = [];

    function mapQuery(one_query) {
      var j, query_list = [], key, sub_query;
      if (one_query.type === "complex") {
        for (j = 0; j < one_query.query_list.length; j += 1) {
          sub_query = mapQuery(one_query.query_list[j]);
          if (sub_query) {
            query_list.push(sub_query);
          }
        }
        one_query.query_list = query_list;
        return one_query;
      }
      key = mapToMainProperty(storage, one_query.key, {}, {});
      if (key !== undefined) {
        one_query.key = key;
        return one_query;
      }
      return false;
    }

    if (option.sort_on !== undefined) {
      for (i = 0; i < option.sort_on.length; i += 1) {
        property = mapToMainProperty(this, option.sort_on[i][0], {}, {});
        if (property && sort_on.indexOf(property) < 0) {
          sort_on.push([property, option.sort_on[i][1]]);
        }
      }
    }
    if (this._query.sort_on !== undefined) {
      for (i = 0; i < this._query.sort_on.length; i += 1) {
        property = mapToMainProperty(this, this._query.sort_on[i], {}, {});
        if (sort_on.indexOf(property) < 0) {
          sort_on.push([property, option.sort_on[i][1]]);
        }
      }
    }
    if (option.select_list !== undefined) {
      for (i = 0; i < option.select_list.length; i += 1) {
        property = mapToMainProperty(this, option.select_list[i], {}, {});
        if (property && select_list.indexOf(property) < 0) {
          select_list.push(property);
        }
      }
    }
    if (this._query.select_list !== undefined) {
      for (i = 0; i < this._query.select_list; i += 1) {
        property = this._query.select_list[i];
        if (select_list.indexOf(property) < 0) {
          select_list.push(property);
        }
      }
    }
    if (this._id_mapped) {
      // modify here for future way to map id
      select_list.push(this._id_mapped);
    }
    if (option.query !== undefined) {
      query = mapQuery(QueryFactory.create(option.query));
    }

    if (this._query.query !== undefined) {
      if (query === undefined) {
        query = this._query.query;
      }
      query = new ComplexQuery({
        operator: "AND",
        query_list: [query, this._query.query],
        type: "complex"
      });
    }

    if (query !== undefined) {
      query = Query.objectToSearchText(query);
    }
    return this._sub_storage.allDocs(
      {
        query: query,
        select_list: select_list,
        sort_on: sort_on,
        limit: option.limit
      }
    )
      .push(function (result) {
        var sub_doc, map_info = storage._map_id || ["equalSubId"];
        for (i = 0; i < result.data.total_rows; i += 1) {
          sub_doc = result.data.rows[i].value;
          result.data.rows[i].id =
            mapping_function[map_info[0]].mapToId(
              storage,
              sub_doc,
              result.data.rows[i].id,
              map_info[1]
            );
          result.data.rows[i].value =
            mapToMainDocument(
              storage,
              sub_doc
            );
        }
        return result.data.rows;
      });
  };

  jIO.addStorage('mapping', MappingStorage);
}(jIO, RSVP, UriTemplate, SimpleQuery, ComplexQuery, QueryFactory, Query,
  FormData));
/*jslint nomen: true*/
(function (jIO) {
  "use strict";

  /**
   * The jIO DateUpdaterStorage extension
   *
   * @class DateUpdaterStorage
   * @constructor
   */

  function updateDocument(doc, property_list) {
    var i, len = property_list.length;
    for (i = 0; i < len; i += 1) {
      doc[property_list[i]] = new Date().toUTCString().replace('GMT', '+0000');
    }
    return doc;
  }

  function DateUpdaterStorage(spec) {
    this._sub_storage = jIO.createJIO(spec.sub_storage);
    this._property_list = spec.property_list || [];
  }

  DateUpdaterStorage.prototype.get = function () {
    return this._sub_storage.get.apply(this._sub_storage, arguments);
  };
  DateUpdaterStorage.prototype.allAttachments = function () {
    return this._sub_storage.allAttachments.apply(this._sub_storage, arguments);
  };
  DateUpdaterStorage.prototype.post = function (doc) {
    doc = updateDocument(doc, this._property_list);
    return this._sub_storage.post(doc);
  };
  DateUpdaterStorage.prototype.put = function (id, doc) {
    doc = updateDocument(doc, this._property_list);
    return this._sub_storage.put(id, doc);
  };
  DateUpdaterStorage.prototype.remove = function () {
    return this._sub_storage.remove.apply(this._sub_storage, arguments);
  };
  DateUpdaterStorage.prototype.getAttachment = function () {
    return this._sub_storage.getAttachment.apply(this._sub_storage, arguments);
  };
  DateUpdaterStorage.prototype.putAttachment = function (id) {
    var storage = this, argument_list = arguments;
    return storage.get(id)
      .push(function (doc) {
        return storage.put(id, doc);
      })
      .push(function () {
        return storage._sub_storage.putAttachment.apply(
          storage._sub_storage,
          argument_list
        );
      });
  };
  DateUpdaterStorage.prototype.removeAttachment = function (id) {
    var storage = this, argument_list = arguments;
    return storage.get(id)
      .push(function (doc) {
        return storage.put(id, doc);
      })
      .push(function () {
        return storage._sub_storage.removeAttachment.apply(
          storage._sub_storage,
          argument_list
        );
      });
  };
  DateUpdaterStorage.prototype.repair = function () {
    return this._sub_storage.repair.apply(this._sub_storage, arguments);
  };
  DateUpdaterStorage.prototype.hasCapacity = function (name) {
    return this._sub_storage.hasCapacity(name);
  };
  DateUpdaterStorage.prototype.buildQuery = function () {
    return this._sub_storage.buildQuery.apply(this._sub_storage,
                                              arguments);
  };

  jIO.addStorage('dateupdater', DateUpdaterStorage);

}(jIO));

/*jslint nomen: true*/
(function (jIO) {
  "use strict";

  /**
   * The jIO SafeRepairStorage extension
   *
   * @class SafeRepairStorage
   * @constructor
   */


  function SafeRepairStorage(spec) {
    this._sub_storage = jIO.createJIO(spec.sub_storage);
    this._id_dict = {};
  }

  SafeRepairStorage.prototype.get = function () {
    return this._sub_storage.get.apply(this._sub_storage, arguments);
  };
  SafeRepairStorage.prototype.allAttachments = function () {
    return this._sub_storage.allAttachments.apply(this._sub_storage, arguments);
  };
  SafeRepairStorage.prototype.post = function () {
    return this._sub_storage.post.apply(this._sub_storage, arguments);
  };
  SafeRepairStorage.prototype.put = function (id, doc) {
    var storage = this;
    return this._sub_storage.put.apply(this._sub_storage, arguments)
      .push(undefined, function (error) {
        if (error instanceof jIO.util.jIOError &&
            error.status_code === 403) {
          if (storage._id_dict[id]) {
            return storage._sub_storage.put(storage._id_dict[id], doc);
          }
          return storage._sub_storage.post(doc)
            .push(function (sub_id) {
              storage._id_dict[id] = sub_id;
              return sub_id;
            });
        }
      });
  };
  SafeRepairStorage.prototype.remove = function () {
    return;
  };
  SafeRepairStorage.prototype.getAttachment = function () {
    return this._sub_storage.getAttachment.apply(this._sub_storage, arguments);
  };
  SafeRepairStorage.prototype.putAttachment = function (id, attachment_id,
      attachment) {
    var storage = this;
    return this._sub_storage.putAttachment.apply(this._sub_storage, arguments)
      .push(undefined, function (error) {
        if (error instanceof jIO.util.jIOError &&
            error.status_code === 403) {
          return new RSVP.Queue()
            .push(function () {
              if (storage._id_dict[id]) {
                return storage._id_dict[id];
              }
              return storage._sub_storage.get(id)
                .push(function (doc) {
                  return storage._sub_storage.post(doc);
                });
            })
            .push(function (sub_id) {
              storage._id_dict[id] = sub_id;
              return storage._sub_storage.putAttachment(sub_id, attachment_id,
                  attachment);
            });
        }
      });
  };
  SafeRepairStorage.prototype.removeAttachment = function () {
    return;
  };
  SafeRepairStorage.prototype.repair = function () {
    return this._sub_storage.repair.apply(this._sub_storage, arguments);
  };
  SafeRepairStorage.prototype.hasCapacity = function (name) {
    return this._sub_storage.hasCapacity(name);
  };
  SafeRepairStorage.prototype.buildQuery = function () {
    return this._sub_storage.buildQuery.apply(this._sub_storage,
                                              arguments);
  };

  jIO.addStorage('saferepair', SafeRepairStorage);

}(jIO));
/*
 * Copyright 2013, Nexedi SA
 *
 * This program is free software: you can Use, Study, Modify and Redistribute
 * it under the terms of the GNU General Public License version 3, or (at your
 * option) any later version, as published by the Free Software Foundation.
 *
 * You can also Link and Combine this program with other software covered by
 * the terms of any of the Free Software licenses or any of the Open Source
 * Initiative approved licenses and Convey the resulting work. Corresponding
 * source of such a combination shall include the source code for all other
 * software used.
 *
 * This program is distributed WITHOUT ANY WARRANTY; without even the implied
 * warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
 *
 * See COPYING file for full licensing terms.
 * See https://www.nexedi.com/licensing for rationale and options.
 */
/**
 * JIO Linshare Storage. Type = "linshare".
 * Linshare "database" storage.
 * http://download.linshare.org/components/linshare-core/2.2.2/
 * Can't set up id, implied can't put new document
 */
/*global Blob, jIO, RSVP, UriTemplate*/
/*jslint nomen: true*/

(function (jIO, RSVP, Blob, UriTemplate) {
  "use strict";

  function makeRequest(storage, options) {
    var ajax_param = {
      type: options.type,
      url: storage._url_template.expand({uuid: options.uuid || ""}),
      headers : {
        "Authorization": "Basic " + storage._credential_token,
        "Accept": "application/json"
      }
    };
    if (options.type === 'PUT') {
      ajax_param.dataType = options.dataType;
      ajax_param.headers['Content-Type'] = "application/json";
    }
    if (options.data) {
      ajax_param.data = options.data;
    }
    if (options.download) {
      ajax_param.url += '/download';
    }
    return new RSVP.Queue()
      .push(function () {
        return jIO.util.ajax(ajax_param);
      })
      .push(function (event) {
        if (options.type === "PUT") {
          return event.target.response.uuid;
        }
        if (options.download) {
          return event.target.response;
        }
        return JSON.parse(event.target.response);
      });
  }

  function checkAttachmentMap(storage, id, name) {
    checkDocumentMap(storage, id);
    if (!storage._id_map[id].attachment.hasOwnProperty(name)) {
      throw new jIO.util.jIOError(
        "Can't find attachment with name :" + name,
        404
      );
    }
  }

  function checkDocumentMap(storage, id) {
    if (!storage._id_map.hasOwnProperty(id)) {
      throw new jIO.util.jIOError(
        "Can't find document with id : " + id,
        404
      );
    }
  }

  /**
   * The JIO Linshare Storage extension
   *
   * @class LinshareStorage
   * @constructor
   */
  function LinshareStorage(spec) {
    this._url_template = UriTemplate.parse(spec.url_template);
    this._credential_token = spec.credential_token;
    this._id_map = {};
  }

  LinshareStorage.prototype.put = function (id, doc) {
    var storage = this,
      data = new FormData();
    data.append('file', new Blob());
    data.append('filename', doc.title);
    data.append('filesize', 0);
    data.append('description', 'jio/document');
    data.append('metadata', jIO.util.stringify({
      doc: doc,
      id: id
    }));

    return makeRequest(this, {
        data: data,
        type: "POST"
      })
      .push(function (result) {
        if (storage._id_map.hasOwnProperty(id)) {
          storage._id_map[id].uuid = result.uuid;
        } else {
          storage._id_map[id] = {'uuid': result.uuid, attachment: {}};
        }
        return id;
      });
  };

  LinshareStorage.prototype.remove = function (id) {
    var storage = this;
    if (storage._id_map.hasOwnProperty(id)) {
      return makeRequest(storage, {
        type: "DELETE",
        uuid: storage._id_map[id].uuid
      })
      .push(function () {
        var promise_list = [],
          name;
        for (name in storage._id_map[id].attachment) {
          if (storage._id_map[id].attachment.hasOwnProperty(name)) {
            promise_list.push(storage.removeAttachment(id, name));
          }
        }
        return RSVP.all(promise_list);
      })
      .push(function () {
        delete storage._id_map[id];
        return id;
      });
    }
  };

  LinshareStorage.prototype.get = function (id) {
    checkDocumentMap(this, id);
    return makeRequest(this, {
      type: "GET",
      uuid: this._id_map[id].uuid
    })
    .push(function (result) {
      return JSON.parse(result.metaData).doc;
    });
  };

  LinshareStorage.prototype.hasCapacity = function (name) {
    return name === "list";
  };

  LinshareStorage.prototype.buildQuery = function () {
    return makeRequest(this, {
      type: "GET"
    })
      .push(function (result) {
        var  rows = [],
          len = result.length,
          i;
        for (i = 0 ; i < len ; i += 1) {
          if (result[i].hasOwnProperty('type')) {
            if (result[i].description === 'jio/document') {
              rows.push({id: JSON.parse(result[i].metaData).id, value: {}});
            }
          }
        }
        return rows;
      });
  };

  // Attachments link by field "description" - Dict

  LinshareStorage.prototype.allAttachments = function (id) {
  };

  LinshareStorage.prototype.putAttachment = function (id, name, blob) {
    var storage = this,
      data = new FormData(),
      uuid;
    if (!storage._id_map.hasOwnProperty(id)) {
      throw new jIO.util.JIOError(
        "Can't find document with id :" + id,
        404
      );
    }
    data.append('file', blob);
    data.append('filename', blob.name);
    data.append('filesize', blob.size);
    data.append('metadata', jIO.util.stringify({
      'id': id,
      'name': name
    }));
    data.append('description', 'jio/attachment');
    return makeRequest(storage, {
      data: data,
      type: "POST"
    })
    .push(function (result) {
      storage._id_map[id].attachment[name] = result.uuid;
      return result.uuid;
    });
  };

  LinshareStorage.prototype.getAttachment = function (id, name) {
    checkAttachmentMap(this, id, name);
    return makeRequest(this, {
      type: "GET",
      uuid: this._id_map[id].attachment[name],
      download: true
    })
    .push(function (result) {
      return new Blob([result]);
    });
  };

  LinshareStorage.prototype.removeAttachment = function (id, name) {
    if (this._id_map.hasOwnProperty(id) &&
        this._id_map[id].attachment.hasOwnProperty(name)) {
      return makeRequest(this, {
        type: "DELETE",
        uuid: this._id_map[id].attachment[name]
      })
      .push(function () {
        delete this._id_map[id].attachment[name];
        return id;
      });
    }
  };


  LinshareStorage.prototype.repair = function () {
    var storage = this;
    return makeRequest(this, {
      type: "GET"
    })
      .push(function (result) {
        var  rows = [],
          len = result.length,
          i,
          metadata,
          row,
          id;
        for (i = 0 ; i < len ; i += 1) {
          row = result[i];
          if (row.hasOwnProperty('description')) {
            if (row.description === 'jio/document') {
              id = JSON.parse(row.metaData).id;
              if (storage._id_map.hasOwnProperty(id)) {
                storage._id_map[id].uuid = row.uuid;
              } else {
                storage._id_map[id] = {'uuid': row.uuid, attachment: {}};
              }
            } else if (row.description === 'jio/attachment') {
              metadata = JSON.parse(row.metaData);
              id = metadata.id;
              if (!storage._id_map.hasOwnProperty(id)) {
                storage._id_map[id] = {'uuid': undefined, attachment: {}};
              }
              storage._id_map[id].attachment[metadata.name] = row.uuid;
            }
          }
        }
      });
  };

  jIO.addStorage('linshare', LinshareStorage);

}(jIO, RSVP, Blob, UriTemplate));