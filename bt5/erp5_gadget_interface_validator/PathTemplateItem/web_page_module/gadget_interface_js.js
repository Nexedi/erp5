/*jslint nomen: true, indent: 2, maxerr: 30, maxlen: 80 */
/*global DOMParser, document, XMLHttpRequest, rJS, renderJS, RSVP, window*/
/*
 * DOMParser HTML extension
 * 2012-09-04
 *
 * By Eli Grey, http://eligrey.com
 * Public domain.
 * NO WARRANTY EXPRESSED OR IMPLIED. USE AT YOUR OWN RISK.
 */
/*! @source https://gist.github.com/1129031 */
(function (DOMParser, document) {
  "use strict";
  var DOMParser_proto = DOMParser.prototype,
    real_parseFromString = DOMParser_proto.parseFromString;

  // Firefox/Opera/IE throw errors on unsupported types
  try {
    // WebKit returns null on unsupported types
    if ((new DOMParser()).parseFromString("", "text/html")) {
      // text/html parsing is natively supported
      return;
    }
  } catch (ignore) {}

  DOMParser_proto.parseFromString = function (markup, type) {
    var result, doc, doc_elt, first_elt;
    if (/^\s*text\/html\s*(?:;|$)/i.test(type)) {
      doc = document.implementation.createHTMLDocument("");
      doc_elt = doc.documentElement;

      doc_elt.innerHTML = markup;
      first_elt = doc_elt.firstElementChild;

      if (doc_elt.childElementCount === 1
          && first_elt.localName.toLowerCase() === "html") {
        doc.replaceChild(first_elt, doc_elt);
      }

      result = doc;
    } else {
      result = real_parseFromString.apply(this, arguments);
    }
    return result;
  };
}(DOMParser, document));

(function (window, rJS, RSVP, DOMParser, XMLHttpRequest, renderJS) {
  "use strict";
  function ajax(url) {
    var xhr;
    function resolver(resolve, reject) {
      function handler() {
        try {
          if (xhr.readyState === 0) {
            // UNSENT
            reject(xhr);
          } else if (xhr.readyState === 4) {
            // DONE
            if ((xhr.status < 200) || (xhr.status >= 300)) {
              reject(xhr);
            } else {
              resolve(xhr);
            }
          }
        } catch (e) {
          reject(e);
        }
      }

      xhr = new XMLHttpRequest();
      xhr.open("GET", url);
      xhr.onreadystatechange = handler;
      xhr.setRequestHeader('Accept', 'text/html');
      xhr.withCredentials = true;
      xhr.send();
    }

    function canceller() {
      if ((xhr !== undefined) && (xhr.readyState !== xhr.DONE)) {
        xhr.abort();
      }
    }
    return new RSVP.Promise(resolver, canceller);
  }

  function fetchAppcacheData(appcache_url) {
    return new RSVP.Queue()
      .push(function () {
        return ajax(appcache_url);
      })
      .push(function (xhr) {
        return xhr.responseText.split('\n');
      });
  }

  function filterGadgetList(filename_list) {
    var html_list = [],
      js_list = [],
      gadget_list = [],
      ext,
      file_name,
      last_index,
      i;
    for (i = 0; i < filename_list.length; i += 1) {
      last_index = filename_list[i].lastIndexOf('.');
      file_name = filename_list[i].substr(0, last_index);
      ext = filename_list[i].substr(last_index + 1);
      if (ext === "html") {
        html_list.push(file_name);
      } else if (ext === "js") {
        js_list.push(file_name);
      }
    }
    for (i = 0; i < html_list.length; i += 1) {
      if (js_list.indexOf(html_list[i]) > -1) {
        gadget_list.push(html_list[i] + ".html");
      }
    }
    return gadget_list;
  }

  function generateErrorMessage(error) {
    var error_message = '';
    error_message = error_message +
                    error.toString() +
                    (error.message !== undefined ? error.message : '') +
                    (error.status ? error.status.toString() + ' ' : '') +
                    (error.statusText !== undefined ? error.statusText : '');
    return error_message;
  }

  function getInterfaceListFromURL(gadget_url) {
    return new RSVP.Queue()
      .push(function () {
        return ajax(gadget_url);
      })
      .push(function (xhr) {
        var document_element = (new DOMParser()).parseFromString(
            xhr.responseText,
            'text/html'
          ),
          interface_list = [],
          element,
          i;
        if (document_element.nodeType === 9 && document_element.head !== null) {
          for (i = 0; i < document_element.head.children.length; i += 1) {
            element = document_element.head.children[i];
            if (element.href !== null &&
                element.rel === "http://www.renderjs.org/rel/interface") {
              interface_list.push(
                renderJS.getAbsoluteURL(element.getAttribute("href"),
                                        window.location.href)
              );
            }
          }
        }
        return interface_list;
      }, function (error) {
        var message = "Error with loading the gadget data.\n";
        error.message = message + generateErrorMessage(error);
        throw error;
      });
  }

  function verifyInterfaceDefinition(interface_url) {
    //to verify if interface definition follows the correct template.
    var error_message = "Interface definition is incorrect: " +
                        "One or more required tags are missing.";
    return new RSVP.Queue()
      .push(function () {
        return ajax(interface_url);
      })
      .push(function (xhr) {
        var doc = (new DOMParser()).parseFromString(xhr.responseText,
                                                    'text/html').body,
          dl_list = doc.getElementsByTagName('dl'),
          next_element = dl_list[0].firstElementChild,
          method_len = dl_list.length - 1,
          argument_len,
          next_child_element,
          i,
          j;
        if (dl_list[0].childElementCount !== 3 * method_len) {
          throw new Error(error_message);
        }
        for (i = 0; i < method_len; i += 1) {
          if ((next_element === null) ||
              (next_element.localName.toLowerCase() !== 'dt')) {
            throw new Error(error_message);
          }
          next_element = next_element.nextElementSibling;
          if (next_element.localName.toLowerCase() !== 'dd') {
            throw new Error(error_message);
          }
          next_element = next_element.nextElementSibling;
          if (next_element.localName.toLowerCase() !== 'dl') {
            throw new Error(error_message);
          }

          if (next_element.getElementsByTagName('dt').length !==
              next_element.getElementsByTagName('dd').length) {
            throw new Error(error_message);
          }
          argument_len = next_element.getElementsByTagName('dt').length;
          next_child_element = next_element.firstElementChild;
          for (j = 0; j < argument_len; j += 1) {
            if ((next_child_element === null) ||
                (next_child_element.localName.toLowerCase() !== 'dt')) {
              throw new Error(error_message);
            }
            next_child_element = next_child_element.nextElementSibling;
            if (next_child_element.localName.toLowerCase() !== 'dd') {
              throw new Error(error_message);
            }
            next_child_element = next_child_element.nextElementSibling;
          }
          next_element = next_element.nextElementSibling;
        }
      }, function (error) {
        var message = "Error with loading the interface data.\n";
        error.message = message + generateErrorMessage(error);
        throw error;
      });
  }

  function verifyInterfaceDeclaration(interface_url, declared_interface_list) {
    //to verify if gadget declares the interface.
    if (declared_interface_list.indexOf(interface_url) > -1) {
      return "Success";
    }
    throw new Error("Interface is not declared.");
  }

/*
  function verifyMethodSignature(interface_method, gadget_method) {
    //to verify if two methods have the same signature
    var max_arg_len = interface_method.argument_list.length,
      min_arg_len = 0,
      i,
      argument_list;
    if (max_arg_len) {
      argument_list = interface_method.argument_list;
      for (i = 0; i < argument_list.length; i += 1) {
        if (argument_list[i].required) {
          min_arg_len += 1;
        }
      }
    }
    return (gadget_method.arg_len >= min_arg_len &&
            gadget_method.arg_len <= max_arg_len);
  }

  function verifyAllMethodSignature(interface_method_list, gadget_method_list) {
    //to verify if all the declared methods match the signature
    // of the interface methods.
    var defer = RSVP.defer(),
      interface_method_dict = {},
      gadget_method_name_list = [],
      index,
      item,
      i,
      j,
      failed = false,
      failed_methods = [];
    for (i = 0; i < interface_method_list.length; i += 1) {
      interface_method_dict[interface_method_list[i].name] =
        interface_method_list[i];
    }
    for (j = 0; j < gadget_method_list.length; j += 1) {
      gadget_method_name_list.push(gadget_method_list[j].name);
    }
    try {
      for (item in interface_method_dict) {
        index = gadget_method_name_list.lastIndexOf(item);
        if (!verifyMethodSignature(interface_method_dict[item],
                                   gadget_method_list[index])) {
          failed = true;
          failed_methods.push(item);
        }
      }
      if (failed) {
        var error_message =
            "Following methods have missing/mismatched arguments: ",
          method;
        for (method in failed_methods) {
          error_message += ("\n" + failed_methods[method]);
        }
        throw new Error(error_message);
      }
      defer.resolve("Success");
    } catch (error) {
      defer.reject(error);
    }
    return defer.promise;
  }
*/

  function verifyAllMethodDeclared(interface_method_list, gadget_method_list) {
    //to verify if all the interface methods are declared by the gadget.
    var gadget_method_name_list = gadget_method_list,
      interface_method_name_list = [],
      i,
      j,
      failed = false,
      failed_methods = [],
      error_message;
    for (i = 0; i < interface_method_list.length; i += 1) {
      interface_method_name_list.push(interface_method_list[i].name);
    }
    for (j = 0; j < interface_method_name_list.length; j += 1) {
      if (gadget_method_name_list.indexOf(
          interface_method_name_list[j]
        ) < 0) {
        failed = true;
        failed_methods.push(interface_method_name_list[j]);
      }
    }
    if (failed) {
      error_message =
          "Following required methods are not declared in the gadget: ";
      for (i = 0; i < failed_methods.length; i += 1) {
        error_message += ("\n" + failed_methods[i]);
      }
      throw new Error(error_message);
    }
    return "Success";
  }

  function verifyAllMethod(interface_method_list, gadget_method_list) {
    //to verify all methods of gadget and interface.
    return new RSVP.Queue()
      .push(function () {
        return verifyAllMethodDeclared(interface_method_list,
                                       gadget_method_list[0]);
      });
/*    Commented till figure out the way to fetch the argument length of a
      defined function.
      .push(function() {
        return verifyAllMethodSignature(interface_method_list,
                                        gadget_method_list[1]);
      })
*/
  }

  rJS(window)

    .declareMethod("getVerifyGadget", function (gadget_url) {
      var interface_gadget = this;
      return interface_gadget.declareGadget(gadget_url, {
        scope: gadget_url
      })
        .push(function () {
          return interface_gadget.getDeclaredGadget(gadget_url);
        }, function (error) {
          var message = "Error with loading the gadget.\n";
          error.message = message + error.message;
          throw error;
        });
    })

    .declareMethod("getDeclaredGadgetInterfaceList", function (gadget_data) {
      if (gadget_data.constructor === String) {
        return getInterfaceListFromURL(gadget_data);
      }
      return gadget_data.getInterfaceList();
    })

    .declareMethod("getDeclaredGadgetMethodList", function (gadget) {
      var declared_method_dict = {},
        declared_method_list = [],
        item;
      for (item in gadget.constructor.prototype) {
        if (gadget.constructor.prototype.hasOwnProperty(item)) {
          if (!(/__/).test(item)) {
            declared_method_dict[item] = gadget[item];
          }
        }
      }
      for (item in declared_method_dict) {
        if (declared_method_dict.hasOwnProperty(item)) {
          declared_method_list.push(item);
        }
      }
      return RSVP.all([
        declared_method_list //,
        // gadget.getDeclaredMethodList()
      ]);
    })

    .declareMethod("getGadgetListFromAppcache", function (appcache_url) {
      return new RSVP.Queue()
        .push(function () {
          return fetchAppcacheData(appcache_url);
        })
        .push(function (filename_list) {
          return filterGadgetList(filename_list);
        });
    })

    .declareMethod("getAbsoluteURL", function (gadget, url) {
      return gadget.getPath()
        .push(function (base_url) {
          return rJS.getAbsoluteURL(url, base_url);
        });
    })

    .declareMethod("getInterfaceData", function (interface_url) {
      var interface_data = {
          name: "",
          description: "",
          method_list: []
        };
      return new RSVP.Queue()
        .push(function () {
          return ajax(interface_url);
        })
        .push(function (xhr) {
          var doc = (new DOMParser()).parseFromString(xhr.responseText,
                                                      'text/html').body,
            dl_list = doc.querySelectorAll('dl'),
            dt_list = doc.querySelectorAll('dt'),
            dd_list = doc.querySelectorAll('dd'),
            method_len = dl_list.length - 1,
            dt_count = 0,
            dl_count = 1,
            i,
            method,
            argument_len,
            j,
            argument_item;
          interface_data.name = doc.querySelector('h1').innerHTML;
          interface_data.description =
            doc.querySelector('h3').innerHTML;
          for (i = 0; i < method_len; i += 1) {
            method = {
              name: dt_list[dt_count].innerHTML,
              description: dd_list[dt_count].innerHTML,
              argument_list: []
            };
            argument_len = dl_list[dl_count].querySelectorAll('dt')
                                            .length;
            dt_count += 1;
            dl_count += 1;
            for (j = 0; j < argument_len; j += 1) {
              argument_item = {
                name: dt_list[dt_count].innerHTML,
                description: dd_list[dt_count].innerHTML,
                required: dt_list[dt_count]
                  .getAttribute("data-parameter-required") !== "optional",
                type: dt_list[dt_count].getAttribute("data-parameter-type")
              };
              dt_count += 1;
              method.argument_list.push(argument_item);
            }
            interface_data.method_list.push(method);
          }
          return interface_data;
        }, function (error) {
          var message = "Error with loading the interface data.\n";
          error.message = message + generateErrorMessage(error);
          throw error;
        });
    })

    .declareMethod("getDefinedInterfaceMethodList", function (interface_url) {
      return this.getInterfaceData(interface_url)
        .push(function (interface_data) {
          return interface_data.method_list;
        });
    })

    .declareMethod("getGadgetListImplementingInterface",
                   function (interface_data, gadget_source_data) {
        var interface_gadget = this,
          interface_list,
          gadget_list;
        return new RSVP.Queue()
          .push(function () {
            var required_interface_list = [];
            if (!interface_data) {
              throw new Error("Invalid input: No interface data is provided.");
            }
            if (interface_data.constructor === Array) {
              required_interface_list = interface_data;
            } else if (interface_data.constructor === String) {
              required_interface_list.push(interface_data);
            } else {
              throw new Error(
                "Invalid input: Invalid interface data is provided."
              );
            }
            return required_interface_list;
          })
          .push(function (i_list) {
            var source_gadget_list = [];
            interface_list = i_list;
            if (!gadget_source_data) {
              throw new Error(
                "Invalid input: No gadget source information is provided."
              );
            }
            if (gadget_source_data.constructor === Array) {
              source_gadget_list = gadget_source_data;
            } else if (gadget_source_data.constructor === String) {
              source_gadget_list = interface_gadget.getGadgetListFromAppcache(
                gadget_source_data
              );
            } else {
              throw new Error(
                "Invalid input: Invalid gadget source information is provided."
              );
            }
            return source_gadget_list;
          })
          .push(function (g_list) {
            var i,
              result_list = [];
            gadget_list = g_list;
            for (i = 0; i < gadget_list.length; i += 1) {
              result_list.push(
                interface_gadget.verifyGadgetInterfaceImplementation(
                  gadget_list[i],
                  interface_list
                )
              );
            }
            return RSVP.all(result_list);
          })
          .push(function (result_list) {
            var i,
              result_gadget_list = [];
            for (i = 0; i < result_list.length; i += 1) {
              if (result_list[i].result) {
                result_gadget_list.push(gadget_list[i]);
              }
            }
            return result_gadget_list;
          });
      })

    .declareMethod("verifyGadgetSingleInterfaceImplementation",
                   function (verify_gadget, interface_url) {
        var interface_gadget = this,
          absolute_interface_url,
          verify_result = {};
        return new RSVP.Queue()
          .push(function () {
            return RSVP.all([
              interface_gadget.getDeclaredGadgetInterfaceList(verify_gadget),
              interface_gadget.getAbsoluteURL(verify_gadget, interface_url)
            ]);
          })
          .push(function (interface_detail) {
            var declared_interface_list = interface_detail[0];
            absolute_interface_url = interface_detail[1];
            return verifyInterfaceDeclaration(absolute_interface_url,
                                              declared_interface_list);
          })
          .push(function () {
            return verifyInterfaceDefinition(absolute_interface_url);
          })
          .push(function () {
            return RSVP.all([
              interface_gadget.getDefinedInterfaceMethodList(
                absolute_interface_url
              ),
              interface_gadget.getDeclaredGadgetMethodList(verify_gadget)
            ]);
          })
          .push(function (method_list) {
            return verifyAllMethod(method_list[0], method_list[1]);
          })
          .push(function () {
            verify_result.result = true;
            return verify_result;
          }, function (error) {
            var interface_name = absolute_interface_url.substr(
              absolute_interface_url.lastIndexOf('/') + 1
            ),
              error_message;
            error_message = "Interface Name: " + interface_name + "\n" +
                            "Error Details : \n" + error.message + "\n";
            verify_result.result = false;
            verify_result.details = error_message;
            return verify_result;
          });
      })

    .declareMethod("verifyGadgetInterfaceImplementation",
                   function (gadget_data, interface_data) {
        var interface_gadget = this,
          verify_gadget,
          interface_list,
          verify_result = {};
        return new RSVP.Queue()
          .push(function () {
            var required_gadget;
            if (!gadget_data) {
              throw new Error("Invalid input: No gadget data is provided.");
            }
            if (gadget_data.constructor === String) {
              verify_result.gadget_url = gadget_data;
              required_gadget = interface_gadget.getVerifyGadget(gadget_data);
            } else {
              required_gadget = gadget_data;
            }
            return required_gadget;
          })
          .push(function (required_gadget) {
            var required_interface_list = [];
            verify_gadget = required_gadget;
            if (!interface_data) {
              required_interface_list =
                interface_gadget.getDeclaredGadgetInterfaceList(verify_gadget);
            } else if (interface_data.constructor === Array) {
              required_interface_list = interface_data;
            } else if (interface_data.constructor === String) {
              required_interface_list.push(interface_data);
            }
            return required_interface_list;
          })
          .push(function (required_interface_list) {
            var result_list = [],
              i;
            interface_list = required_interface_list;
            for (i = 0; i < interface_list.length; i += 1) {
              result_list.push(
                interface_gadget.verifyGadgetSingleInterfaceImplementation(
                  verify_gadget,
                  interface_list[i]
                )
              );
            }
            return RSVP.all(result_list);
          })
          .push(function (result_list) {
            var i,
              failed = false,
              error_message = '';
            for (i = 0; i < result_list.length; i += 1) {
              if (!result_list[i].result) {
                failed = true;
                error_message += (result_list[i].details + '\n');
              }
            }
            if (failed) {
              throw new Error(error_message);
            }
          })
          .push(function () {
            verify_result.result = true;
            return verify_result;
          }, function (error) {
            verify_result.result = false;
            verify_result.details = error.message;
            return verify_result;
          });
      });

}(window, rJS, RSVP, DOMParser, XMLHttpRequest, renderJS));