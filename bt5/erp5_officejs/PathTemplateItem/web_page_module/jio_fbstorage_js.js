/*jslint nomen: true */
/*global RSVP, UriTemplate, console*/
(function (jIO, RSVP, UriTemplate) {
  "use strict";

  var GET_POST_URL = "https://graph.facebook.com/v2.9/{+post_id}" +
      "?fields={+fields}&access_token={+access_token}",
    get_post_template = UriTemplate.parse(GET_POST_URL),
    GET_FEED_URL = "https://graph.facebook.com/v2.9/{+user_id}/feed" +
        "?fields={+fields}&limit={+limit}&since={+since}&access_token=" +
        "{+access_token}",
    get_feed_template = UriTemplate.parse(GET_FEED_URL);

  function FBStorage(spec) {
    if (typeof spec.access_token !== 'string' || !spec.access_token) {
      throw new TypeError("Access Token must be a string " +
                          "which contains more than one character.");
    }
    if (typeof spec.user_id !== 'string' || !spec.user_id) {
      throw new TypeError("User ID must be a string " +
                          "which contains more than one character.");
    }
    this._access_token = spec.access_token;
    this._user_id = spec.user_id;
    this._default_field_list = spec.default_field_list;
    delete this._default_field_list.__id;
    this._default_limit = spec.default_limit || 500;
  }

  FBStorage.prototype.get = function (id) {
    var that = this;
    return new RSVP.Queue()
      .push(function () {
        console.log('Ajax fetch for get');
        console.log(that._default_field_list);
        return jIO.util.ajax({
          type: "GET",
          url: get_post_template.expand({post_id: id,
            fields: that._default_field_list, access_token: that._access_token})
        });
      })
      .push(function (result) {
        return JSON.parse(result.target.responseText);
      },
      function (err) {
        console.log('Ajax fetch for get failed', err);
      });
  };

  function paginateResult(url, result, select_list) {
    return new RSVP.Queue()
      .push(function () {
        console.log('Ajax fetch for paginateResults', url);
        return jIO.util.ajax({
          type: "GET",
          url: url
        });
      })
      .push(function (response) {
        return JSON.parse(response.target.responseText);
      },
        function (err) {
          console.log('Ajax fetch for paginateResults failed', err);
          throw new jIO.util.jIOError("Getting feed failed " + err.toString(),
            400);
        })
      .push(function (response) {
        if (response.data.length === 0) {
          console.log('response.data.length==0', result);
          return result;
        }
        var i, j, obj = {};
        for (i = 0; i < response.data.length; i += 1) {
          obj.id = response.data[i].id;
          obj.value = {};
          for (j = 0; j < select_list.length; j += 1) {
            obj.value[select_list[j]] = response.data[i][select_list[j]];
          }
          result.push(obj);
          obj = {};
        }
        return paginateResult(response.paging.next, result, select_list);
      });
  }

  FBStorage.prototype.buildQuery = function (query) {
    console.log('QueryRecieved', query);
    var that = this, template_argument = {user_id: this._user_id, limit: 100,
      access_token: this._access_token}, fields = [],
      limit = this._default_limit;
    if (query.include_docs) {
      fields = fields.concat(that._default_field_list);
    }
    if (query.select_list) {
      fields = fields.concat(query.select_list);
    }
    if (query.limit) {
      limit = query.limit[1];
    }
    template_argument.fields = fields;
    template_argument.limit = limit;
    return paginateResult(get_feed_template.expand(template_argument), [],
      fields)
      .push(function (result) {
        if (!query.limit) {
          return result;
        }
        return result.slice(query.limit[0], query.limit[1]);
      });
  };

  FBStorage.prototype.hasCapacity = function (name) {
    var this_storage_capacity_list = ["list", "select", "include", "limit"];
    if (this_storage_capacity_list.indexOf(name) !== -1) {
      return true;
    }
  };

  jIO.addStorage('facebook', FBStorage);

}(jIO, RSVP, UriTemplate));