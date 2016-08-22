/*jslint indent: 2*/
/*global self, caches, importScripts, fetch, Promise, Request, Response, jIO, console, Headers, URI, location*/
var global = self,
  window = self;
(function (self, fetch) {
  "use strict";

  self.DOMParser = {};
  self.sessionStorage = {};
  self.localStorage = {};
  self.openDatabase = {};
  importScripts('rsvp.js', 'jiodev.js');

  Response.prototype.metadata = function () {
    var headers = {};
    Array.from(this.headers.entries()).forEach(function (data) {
      headers[data[0]] = data[1];
    });
    return {
      //'ok': this.ok
      url: this.url,
      headers: headers
    };
  };

  Response.prototype.metadata_w_blob = function () {
    var metadata = this.metadata();
    return this.blob().then(function (blob) {
      return Promise.resolve({
        'blob': blob,
        'metadata': metadata
      });
    });
  };

  // 3 levels cache are used:

  // 1. cache for web developper saved all files
  // from web_page_module
  // allow offline developing and offline view result
  self.jio_dev_storage = jIO.createJIO({
    type: "query",
    sub_storage: {
      type: "uuid",
      sub_storage: {
        "type": "indexeddb",
        "database": "webdevtool"
      }
    }
  });

  // 2. readonly cache for end user
  self.jio_erp5_cache_storage = {
    type: "query",
    sub_storage: {
      type: "uuid",
      sub_storage: {
        type: "indexeddb",
        database: self.jio_cache.name + '_erp5'
      }
    }
  };
  // sync in service worker not work.
  // erp5storage not support fetch.
  if (self.jio_cache.erp5_query) {
    self.jio_erp5_cache_storage = jIO.createJIO({
      type: "replicate",
      // XXX This drop the signature lists...
      query: {
        query: '(portal_type: ("Web Style", "Web Page", "Web Script")) AND ' +
          self.jio_cache.erp5_query,
        limit: [0, 1234567890]
      },
      use_remote_post: true,
      conflict_handling: 2,
      check_local_modification: false,
      check_local_creation: false,
      check_local_deletion: false,
      check_remote_modification: true,
      check_remote_creation: true,
      check_remote_deletion: true,
      local_sub_storage: {
        type: "attachasproperty",
        map: {
          text_content: "text_content",
          data: "data"
        },
        sub_storage: self.jio_erp5_cache_storage
      },
      remote_sub_storage: {
        type: "erp5",
        url: (new URI("hateoas"))
          .absoluteTo(location.href)
          .toString(),
        default_view_reference: "jio_view"
      }
    });
  } else {
    self.jio_erp5_cache_storage = jIO.createJIO(self.jio_erp5_cache_storage);
  }
  // 3. save static list urls
  // site root files
  // external urls
  // binary files (images, fonts)
  self.jio_cache_storage = jIO.createJIO({
    type: "query",
    sub_storage: {
      type: "uuid",
      sub_storage: {
        "type": "indexeddb",
        "database": "officejs_cache" + '_static'
      }
    }
  });

  // TODO: if map_portal_type2content_type changed we can repair jio storage
  var map_portal_type2content_type = {
      'Web Script': 'application/javascript',
      'Web Page': 'text/html',
      //'Image': 'image/',
      'Web Style': 'text/css'
    },
    map_url2id_prefix = {},
    map_url2url = {},
    exclude_urls = [],
    map_content_type2portal_type = {},
    websections_url = [],
    query_portal_types = "",
    site_url = ((new URI(self.location.href)).filename('')).toString(),
    portal_type2attach_name = function (portal_type) {
      // TODO: generate from erp5
      var map_portal_type2attach_name = {
          'Image': 'data'
        },
        attach_name;

      attach_name = map_portal_type2attach_name[portal_type];
      if (attach_name !== undefined) {
        return attach_name;
      }
      return 'text_content';
    },
    is_excluded_url = function (url) {
      var prefix, i;
      for (i = 0; i < exclude_urls.length; i++) {
        prefix = exclude_urls[i];
        if (url === prefix) {
          return true;
        }
        if (url.startsWith(prefix + '/')) {
          return true;
        }
      }
      return false;
    },
    get_mapped_url = function (url) {
      var prefix,
        prefix_id,
        key;
      for (key in map_url2url) {
        if (map_url2url.hasOwnProperty(key)) {
          if (url === key) {
            return map_url2url[key];
          }
          if (url.startsWith(key)) {
            return url.replace(key, map_url2url[key]);
          }
        }
      }
    },
    get_relative_url = function (url) {
      var prefix,
        relative_url,
        i,
        prefix_id;
      for (i = 0; i < websections_url.length; i++) {
        prefix = websections_url[i];
        if (url.startsWith(prefix)) {
          prefix_id = map_url2id_prefix[prefix];
          if (prefix_id !== "") {
            prefix_id = prefix_id + "/";
          }
          relative_url = url.replace(prefix, prefix_id);
          if (relative_url) {
            return relative_url;
          } else {
            return url;
          }
        }
      }
      return url;
    },
    get_from_cache_storage = function (url, storage) {
      var jio_key = get_relative_url(url);
      if (!storage) {
        storage = self.jio_cache_storage;
      }
      return new Promise(function (resolve, reject) {
        storage.get(jio_key)
          .push(function (metadata) {
            return storage.getAttachment(jio_key, 'body')
              .push(function (body) {
                resolve(new Response(body, {'headers': metadata.headers}));
              });
          })
          .push(undefined, function (error) {
            reject(error);
          });
      });
    },
    get_specific_url = function (url) {
      var prefix,
        prefix_id,
        i;
      for (i = 0; i < websections_url.length; i++) {
        prefix = websections_url[i];
        if (url.startsWith(prefix)) {
          prefix_id = map_url2id_prefix[prefix];
          if (prefix_id !== "") {
            return url.replace(prefix, prefix_id + '/');
          }
          break;
        }
      }
    },
    find_and_get = function (query, storage) {
      if (!storage) {
        storage = self.jio_dev_storage;
      }
      return storage.allDocs(query)
        .push(function (result) {
          if (result.data.total_rows >= 1) {
            var id = result.data.rows[0].id;
            return storage.get(id)
              .push(function (doc) {
                doc.id = id;
                return doc;
              });
          } else {
            throw {status_code: 404};
          }
        });
    },
    get_from_storage = function (url, storage) {
      var url_string = get_specific_url(url),
        url_object = new URI(url),
        reference = url_object.filename();
      if (!storage) {
        storage = self.jio_dev_storage;
      }
      return new Promise(function (resolve, reject) {
        var find_queue;
        if (url_string !== undefined) {
          find_queue = find_and_get({
            query: query_portal_types + ' AND (url_string: ="' + url_string + '")'
          }, storage);
          if (!self.jio_cache.development_mode) {
            find_queue = find_queue
              .push(undefined, function (error) {
                if (error.status_code === 404) {
                  return find_and_get({
                    query: query_portal_types + ' AND (reference: ="' + reference + '")',
                    sort_on: [["url_string", "ascending"]]
                  }, storage);
                } else {
                  throw error;
                }
              });
          }
          //} else if (reference !== "") {
        } else if (reference === get_relative_url(url)) {
          // i use sort_on for emulate query:
          // '(url_string: "" ) AND (reference: "' + reference + '")'
          find_queue = find_and_get({
            query: query_portal_types + ' AND (reference: ="' + reference + '")',
            sort_on: [["url_string", "ascending"]]
          }, storage);
        } else {
          reject({status_code: 404});
          return;
        }
        find_queue
          .push(function (doc) {
            return storage.getAttachment(doc.id, portal_type2attach_name(doc.portal_type))
              .push(function (body) {
                var content_type;
                content_type = doc.content_type;
                if (content_type === undefined) {
                  content_type = map_portal_type2content_type[doc.portal_type];
                }
                resolve(new Response(body, {
                  'headers': {
                    'content-type': content_type
                  }
                }));
              });
          })
          .push(undefined, function (error) {
            reject(error);
          });
      });
    },
    content_type2portal_type = function (content_type) {
      //var portal_type;

      return map_content_type2portal_type[content_type];
      //for (prefix in map_content_type2portal_type) {
      //  if (content_type.startsWith(prefix)) {
      //    return map_content_type2portal_type[prefix];
      //  }
      //}
    },
    save_in_dev_storage = function (url, response) {
      // save in developer storage
      //if (url)
      var jio_key,
        url_string,
        reference,
        prefix,
        prefix_id,
        erp5_id;
      for (prefix in map_url2id_prefix) {
        if (map_url2id_prefix.hasOwnProperty(prefix)) {
          if (url.startsWith(prefix)) {
            prefix_id = map_url2id_prefix[prefix];
            reference = (new URI(url)).filename();
            if (prefix_id === "") {
              if (url.replace(prefix, '') !== reference) {
                continue;
              }
            }
            if (prefix_id !== "") {
              url_string = url.replace(prefix, prefix_id + '/');
              erp5_id = url_string.replace(/\//g, '_').replace(/\./g, '_');
            } else {
              url_string = "";
              erp5_id = reference.replace(/\./g, '_');
            }
            if (erp5_id) {
              jio_key = "web_page_module/" + erp5_id;
            }
            break;
          }
        }
      }
      if (jio_key) {
        return response.metadata_w_blob()
          .then(function (response) {
            return new Promise(function (resolve, reject) {
              var content_type = response.metadata.headers['content-type'],
                portal_type,
                metadata;
              content_type = content_type.split(';')[0].trim();
              portal_type = content_type2portal_type(content_type);
              metadata = {
                'id': erp5_id,
                'portal_type': portal_type,
                'reference': reference,
                'url_string': url_string,
                'parent_relative_url': 'web_page_module'
              };
              /*if (!portal_type) {
               if (content_type.startsWith('image/')) {
               metadata.content_type = content_type;
               portal_type = 'Image';
               }
               metadata.portal_type = portal_type;
               }*/
              if (!portal_type) {
                console.log('content_type ' + content_type + ' not supported: ' + url);
                return resolve();
              }
              self.jio_dev_storage.put(jio_key, metadata)
                .push(function () {
                  return self.jio_dev_storage.putAttachment(
                    jio_key,
                    portal_type2attach_name(portal_type),
                    response.blob
                  );
                })
                .push(function () {
                  console.log('jio_save: ' + jio_key);
                  resolve();
                })
                .push(undefined, function (error) {
                  console.log(error);
                  reject(error);
                });
            });
          });
      } else {
        return Promise.resolve();
      }
    };

  (function () {
    var portal_type;
    for (portal_type in map_portal_type2content_type) {
      if (map_portal_type2content_type.hasOwnProperty(portal_type)) {
        map_content_type2portal_type[map_portal_type2content_type[portal_type]] = portal_type;
      }
    }
  }());

  (function () {
    var portal_type;
    for (portal_type in map_portal_type2content_type) {
      if (map_portal_type2content_type.hasOwnProperty(portal_type)) {
        query_portal_types = query_portal_types + '"' + portal_type + '",';
      }
    }
    query_portal_types = '(portal_type: (' + query_portal_types + '))';
  }());

  // TODO: generate from special websections current website
  map_url2id_prefix[site_url + 'rjsunsafe/ooffice_fonts/'] = 'ooffice_fonts';
  map_url2id_prefix[site_url + 'rjsunsafe/ooffice/'] = 'ooffice';
  map_url2id_prefix[site_url + 'rjsunsafe/'] = '';
  map_url2id_prefix[site_url] = '';
  map_url2id_prefix['https:'] = '';

  exclude_urls.push(site_url + 'hateoas');
  exclude_urls.push(site_url + 'hateoasnoauth');

  map_url2url[site_url + 'rjsunsafe/ooffice/apps/'] = 'https://localhost/OfficeWebDeploy/apps/';
  map_url2url[site_url + 'rjsunsafe/ooffice/sdkjs/'] = 'https://localhost/OfficeWebDeploy/sdkjs/';
  map_url2url[site_url + 'rjsunsafe/ooffice/vendor/'] = 'https://localhost/OfficeWebDeploy/vendor/';

  (function () {
    var url;
    for (url in map_url2id_prefix) {
      if (map_url2id_prefix.hasOwnProperty(url)) {
        websections_url.push(url);
      }
    }
    websections_url.sort(function (a, b) {
      return a.length < b.length;
    });
  }());

  self.jio_cache_install = function (event) {
    // Perform install step:  loading each required file into cache
    // sync jio
    // TODO:
    //    delete from cache not existing in self.jio_cache.cached_urls files.
    var queue,
      result_fetch = Promise.resolve(), // queue for fetching files
      result_jio_save = Promise.resolve(); // queue for save files

    if (self.jio_erp5_cache_storage.type === "replicate") {
      queue = new Promise(function (resolve, reject) {
        self.jio_erp5_cache_storage.repair()
          .push(resolve, reject);
      });
    } else {
      queue = Promise.resolve();
    }
    queue.then(function () {
      new Promise(function (resolve, reject) {
        //return resolve();
        self.jio_cache.cached_urls.map(function (url, i) {
          var request = new Request(url),
            requests_len = self.jio_cache.cached_urls.length - 1,
            jio_key = url;
          if (jio_key === "./") {
            jio_key = request.url;
          }
          // files download one by one
          result_fetch = result_fetch
            .then(function () {
              return new Promise(function (resolve) {
                self.jio_cache_storage.get(jio_key)
                  .push(function (metadata) {
                    resolve(metadata);
                  })
                  .push(undefined, resolve);
              });
            })
            .then(function (metadata) {
              if (metadata.url !== undefined) {
                var modification_mark_exist = false;
                if (metadata.headers.ETag !== undefined) {
                  modification_mark_exist = true;
                  request.headers.append('If-None-Match', metadata.headers.Etag);
                } else if (metadata.headers['last-modified'] !== undefined) {
                  modification_mark_exist = true;
                  request.headers.append('If-Modified-Since', metadata.headers['last-modified']);
                }
                if (modification_mark_exist) {
                  return fetch(request)
                    .then(undefined, function () {
                      // We say 'file not changed' if downloading is not possible with additional header
                      return new Response(null, {status: 304});
                    });
                }
              }
              return fetch(request);
            })
            .then(function (response) {
              if (response.status === 304) {
                if (i === requests_len) {
                  // latest file saved
                  result_jio_save = result_jio_save.then(resolve);
                }
                return Promise.resolve();
              } else {
                return response.metadata_w_blob()
                  .then(function (response) {
                    // files save one by one
                    result_jio_save = result_jio_save.then(function () {
                      return new Promise(function (resolve) {
                        self.jio_cache_storage.put(jio_key, response.metadata)
                          .push(function () {
                            return self.jio_cache_storage.putAttachment(
                              jio_key,
                              "body",
                              response.blob
                            )
                              .push(function () {
                                console.log('jio_save: ' + jio_key);
                                resolve();
                              });
                          })
                          .push(undefined, function (error) {
                            console.log(error);
                            reject();
                          });
                      });
                    });


                    if (i === requests_len) {
                      // latest file saved
                      result_jio_save = result_jio_save.then(resolve);
                    }
                    return Promise.resolve();
                  });
              }
            });
        });
      })
        .then(function () {
          console.log('cache loaded');
          return self.skipWaiting();
        })
        .then(undefined, console.log);
    });

    event.waitUntil(queue);
  };

  self.jio_cache_fetch = function (event) {
    var url = event.request.url,
      mapped_url,
      relative_url = get_relative_url(url),
      specific_url = get_specific_url(url) || relative_url,
      not_found_in_dev_storage = false,
      queue;

    if (is_excluded_url(url)) {
      queue = fetch(event.request);
    } else {
      mapped_url = get_mapped_url(url);
      if (self.jio_cache.development_mode && mapped_url) {
        queue = fetch(mapped_url)
          .then(undefined, function (error) {
            if (error.status_code === 404) {
              console.log(url + ',' + specific_url + ' not found by ' + mapped_url + ' storage');
              return get_from_storage(url, self.jio_erp5_cache_storage);
            } else {
              throw error;
            }
          })
          .then(undefined, function (error) {
            if (error.status_code === 404) {
              console.log(url + ',' + specific_url + ' not found in erp5 cache storage');
              return get_from_cache_storage(url);
            } else {
              throw error;
            }
          })
          .then(function (response) {
            if (response.ok) {
              save_in_dev_storage(url, response.clone());
              //console.log('returned: ' + url);
              return response;
            } else {
              debugger;
            }
          })
          .then(undefined, function (error) {
            console.log(error);
          });
      } else {
        queue = Promise.resolve()
          .then(function () {
            if (self.jio_cache.development_mode) {
              // 1 level storage development
              return get_from_storage(url, self.jio_dev_storage);
            } else {
              throw {status_code: 404};
            }
          })
          .then(undefined, function (error) {
            if (error.status_code === 404) {
              if (self.jio_cache.development_mode) {
                console.log(url + ',' + specific_url + ' not found in dev storage');
                not_found_in_dev_storage = true;
              }
              // 2 level storage from erp5
              return get_from_storage(url, self.jio_erp5_cache_storage);
            } else {
              throw error;
            }
          })
          .then(undefined, function (error) {
            if (error.status_code === 404) {
              console.log(url + ',' + specific_url + ' not found in erp5 cache storage');
              // 3 level cache urls one for all aplications
              return get_from_cache_storage(url);
            } else {
              throw error;
            }
          })
          .then(undefined, function (error) {
            if (error.status_code === 404) {
              console.log(url + ',' + relative_url + ' not found in cache storage');
              // fetch
              return fetch(event.request);
            } else {
              throw error;
            }
          })
          .then(function (response) {
            if (response.ok) {
              if (not_found_in_dev_storage) {
                save_in_dev_storage(url, response.clone());
              }
              //console.log('returned: ' + url);
              return response;
            }
          })
          .then(undefined, function (error) {
            console.log(error);
          });
      }
    }
    event.respondWith(queue);
  };

  self.jio_cache_activate = function (event) {
    /* Just like with the install event, event.waitUntil blocks activate on a promise.
     Activation will fail unless the promise is fulfilled.
     */
    event.waitUntil(self.clients.claim());
  };

  self.addEventListener('install', self.jio_cache_install);
  self.addEventListener('fetch', self.jio_cache_fetch);
  self.addEventListener("activate", self.jio_cache_activate);

}(self, fetch));