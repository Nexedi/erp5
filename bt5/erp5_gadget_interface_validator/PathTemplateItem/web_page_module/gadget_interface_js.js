/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80 */
/*global DOMParser, rJS, RSVP, window,
         jIO, console, document*/
(function (window, rJS, RSVP, DOMParser, jIO, console, document) {
  "use strict";

  //////////////////////////////////////////////
  // Interface reader
  //////////////////////////////////////////////
  function GadgetInterface() {
    if (!(this instanceof GadgetInterface)) {
      return new GadgetInterface();
    }
    this.title = '';
    this.description = '';
    this.method_list = [];
  }

  GadgetInterface.parse = function (txt) {
    var parser = (new DOMParser()).parseFromString(txt, 'text/html').body,
      reader = new GadgetInterface(),
      element,
      sub_element,
      method,
      argument;
    // Extract title
    element = parser.firstElementChild;
    if (element.tagName !== 'H1') {
      throw new Error("Can't find gadget interface title from " +
                      element.outerHTML);
    }
    reader.title = element.textContent;

    // Extract description
    element = element.nextElementSibling;
    if (element.tagName !== 'H3') {
      throw new Error("Can't find gadget interface description from " +
                      element.outerHTML);
    }
    reader.description = element.textContent;

    // Extract method list
    element = element.nextElementSibling;
    if (element.tagName !== 'DL') {
      throw new Error("Can't find gadget interface method list from " +
                      element.outerHTML);
    }
    if (element.nextElementSibling !== null) {
      // Ensure the HTML doesn't contain unexpected tags after methods
      // definition
      throw new Error("Unexpected element " + element.tagName +
                      " from " + element.outerHTML);
    }

    // Parse all methods
    element = element.firstElementChild;
    while (element !== null) {
      // Loop on all methods
      method = {};

      // Extract method title
      if (element.tagName !== 'DT') {
        throw new Error("Can't find gadget interface method name from " +
                        element.outerHTML);
      }
      method.name = element.textContent;

      // Extract method description
      element = element.nextElementSibling;
      if (element.tagName !== 'DD') {
        throw new Error("Can't find gadget interface method description " +
                        "from " + element.outerHTML);
      }
      method.description = element.textContent;

      // Extract method argument list
      element = element.nextElementSibling;
      if (element.tagName !== 'DL') {
        throw new Error("Can't find gadget interface method argument list " +
                        "from " + element.outerHTML);
      }

      // Parse all arguments
      method.argument_list = [];
      sub_element = element.firstElementChild;
      while (sub_element !== null) {
        // Loop on all arguments
        argument = {};

        // Extract argument name
        if (sub_element.tagName !== 'DT') {
          throw new Error("Can't find gadget interface argument name from " +
                          sub_element.outerHTML);
        }
        argument.name = sub_element.textContent;
        argument.required =
          sub_element.getAttribute("data-parameter-required") !== "optional";
        argument.type = sub_element.getAttribute("data-parameter-type");

        // Extract argument description
        sub_element = sub_element.nextElementSibling;
        if (sub_element.tagName !== 'DD') {
          throw new Error("Can't find gadget interface argument description " +
                          "from " + sub_element.outerHTML);
        }
        argument.description = sub_element.textContent;

        // Next argument
        method.argument_list.push(argument);
        sub_element = sub_element.nextElementSibling;
      }

      // Next method
      reader.method_list.push(method);
      element = element.nextElementSibling;
    }

    return reader;
  };

  GadgetInterface.fetch = function (interface_url) {
    var context = this;
    return new RSVP.Queue()
      .push(function () {
        return jIO.util.ajax({
          url: interface_url,
          dataType: 'text'
        });
      })
      .push(function (evt) {
        return context.parse(evt.target.responseText);
      });
  };

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

  function verifyAllMethodDeclared(interface_method_list, gadget_method_list,
                                   error_list) {
    //to verify if all the interface methods are declared by the gadget.
    var gadget_method_name_list = gadget_method_list,
      interface_method_name_list = [],
      i,
      j,
      missing_method_list = [],
      error_message;
    for (i = 0; i < interface_method_list.length; i += 1) {
      interface_method_name_list.push(interface_method_list[i].name);
    }
    // Check missing method declaration
    for (j = 0; j < interface_method_name_list.length; j += 1) {
      if (gadget_method_name_list.indexOf(
          interface_method_name_list[j]
        ) < 0) {
        missing_method_list.push(interface_method_name_list[j]);
      }
    }
    if (missing_method_list.length) {
      error_message =
          "Following required methods are not declared in the gadget: ";
      for (i = 0; i < missing_method_list.length; i += 1) {
        error_message += ("\n" + missing_method_list[i]);
      }
      error_list.push({
        details: error_message
      });
    }
  }

  var interface_loader_defer = RSVP.defer(),
    counter = 0;
  interface_loader_defer.resolve('Bootstrap');

  function getOrDeclareGadget(context, gadget_to_check_url) {
    return context.getDeclaredGadget(gadget_to_check_url)
      .push(undefined, function (error) {
        var element,
          loader_gadget,
          current_defer;
        if (error instanceof rJS.ScopeError) {
          element = document.createElement('div');
          context.element.querySelector('div').appendChild(element);
          return new RSVP.Queue()
            .push(function () {
              context.element.firstElementChild.textContent =
                'Waiting ' + counter;
              // Wait for previous defer, and create a new one.
              var previous_deferred = interface_loader_defer;
              current_defer = RSVP.defer();
              interface_loader_defer = current_defer;
              counter += 1;
              return previous_deferred.promise;
            })
            .push(function () {
              context.element.firstElementChild.textContent = 'Loading';
              // XXX Load in an iframe
              return context.declareGadget('gadget_interface_loader.html', {
                scope: gadget_to_check_url,
                element: element,
                sandbox: 'iframe'
              });
            })
            .push(function (result) {
              loader_gadget = result;
              return loader_gadget.declareGadgetToCheck(gadget_to_check_url);
            })
            .push(function () {
              // Iframe loaded, unblock the next iteration
              current_defer.resolve();
              return loader_gadget;
            }, function (error) {
              current_defer.resolve();
              throw error;
            });
        }
        throw error;
      });
  }

  function getDefinedInterfaceMethodList(interface_url, error_list) {
    return GadgetInterface.fetch(interface_url)
      .push(function (interface_data) {
        return interface_data.method_list;
      }, function (error) {
        var interface_name = interface_url.substr(
          interface_url.lastIndexOf('/') + 1
        );
        error_list.push({
          details: "Interface Name: " + interface_name + "\n" +
                   "Error Details : \n" + error.message + "\n"
        });
        // As interface can't be parsed, no method is found
        return [];
      });
  }

  rJS(window)
/*
    .declareMethod("getGadgetListImplementingInterface",
                   function (interface_data, appcache_url) {
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
            interface_list = i_list;
            return interface_gadget.getGadgetListFromAppcache(
              appcache_url
            );
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
*/

    .declareMethod("render", function (options) {
      return this.changeState(options);
    })

    .onStateChange(function () {
      var context = this,
        required_interface_list = [],
        gadget_method_list = [],
        error_list = [];

      return getOrDeclareGadget(context, context.state.gadget_to_check_url)

        .push(function (gadget_to_check) {
          // Get the list of interfaces/methods
          return RSVP.all([
            gadget_to_check.getGadgetToCheckInterfaceList(),
            gadget_to_check.getGadgetToCheckMethodList('method')
          ]);
        })
        .push(function (result_list) {
          required_interface_list = result_list[0];
          gadget_method_list = result_list[1];
        }, function (error) {
          error_list.push({
            details: "Error with gadget loading\n" + (error.message || '')
          });
        })

        .push(function () {
          // Get all methods definition for every interface
          var promise_list = [],
            i;
          for (i = 0; i < required_interface_list.length; i += 1) {
            promise_list.push(
              getDefinedInterfaceMethodList(required_interface_list[i],
                                            error_list)
            );
          }
          return RSVP.all(promise_list);
        })

        .push(function (method_table) {
          var interface_method_list = [],
            i,
            j,
            promise_list = [];

          for (i = 0; i < method_table.length; i += 1) {
            for (j = 0; j < method_table[i].length; j += 1) {
              // Check method declared twice
              if (interface_method_list.indexOf(method_table[i][j].name) >= 0) {
                error_list.push({
                  details: "Method documented in multiple interface\n" +
                           method_table[i][j].name
                });
              } else {
                interface_method_list.push(method_table[i][j].name);
              }
            }
          }

          // Check unknown method declaration
          for (i = 0; i < gadget_method_list.length; i += 1) {
            if (interface_method_list.indexOf(
                gadget_method_list[i]
              ) < 0) {
              error_list.push({
                details: "Method not documented in the interface\n" +
                         gadget_method_list[i]
              });
            }
          }

          // Check that all interfaces are implemented
          for (i = 0; i < required_interface_list.length; i += 1) {
            promise_list.push(
              verifyAllMethodDeclared(method_table[i], gadget_method_list,
                                      error_list)
            );
          }
          return RSVP.all(promise_list);

        })
        .push(function () {
          // Display result
          var i,
            error_message = '',
            summary_message;

          if (error_list.length === 0) {
            summary_message = 'Success';
          } else {
            summary_message = 'Failure';
          }

          for (i = 0; i < error_list.length; i += 1) {
            error_message += (error_list[i].details + '\n\n');
          }

          if (context.state.summary) {
            if (error_message !== '') {
              console.warn(error_message, error_list);
            }
            error_message = summary_message;
          } else {
            error_message = summary_message + '\n\n' + error_message;
          }
          context.element.firstElementChild.textContent = error_message;
        })

        .push(undefined, function (error) {
          console.warn(error);
          context.element.firstElementChild.textContent =
            "Unexpected error";
        });

    });

}(window, rJS, RSVP, DOMParser, jIO, console, document));