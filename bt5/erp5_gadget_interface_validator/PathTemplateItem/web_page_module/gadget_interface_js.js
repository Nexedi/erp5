/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80 */
/*global DOMParser, document, rJS, RSVP, window,
         jIO*/
(function (window, rJS, RSVP, DOMParser, jIO) {
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
    return verifyAllMethodDeclared(interface_method_list,
                                   gadget_method_list);
/*    Commented till figure out the way to fetch the argument length of a
      defined function.
      .push(function() {
        return verifyAllMethodSignature(interface_method_list,
                                        gadget_method_list[1]);
      })
*/
  }

  function getOrDeclareGadget(context, gadget_to_check_url) {
    return context.getDeclaredGadget(gadget_to_check_url)
      .push(undefined, function (error) {
        if (error instanceof rJS.ScopeError) {
          // XXX Load in an iframe
          return context.declareGadget(gadget_to_check_url, {
            scope: gadget_to_check_url
          });
        }
        throw error;
      });
  }

  function getDefinedInterfaceMethodList(interface_url) {
    return GadgetInterface.fetch(interface_url)
      .push(function (interface_data) {
        return interface_data.method_list;
      });
  }

  function getGadgetMethodList(context, gadget_to_check_url) {
    return getOrDeclareGadget(context, gadget_to_check_url)
      .push(function (gadget) {
        var declared_method_dict = {},
          declared_method_list = [],
          item;
        for (item in gadget.constructor.prototype) {
          if (gadget.constructor.prototype.hasOwnProperty(item)) {
            if (!(/__/).test(item) && (item !== 'constructor') &&
                (typeof gadget[item] === "function")) {
              declared_method_dict[item] = gadget[item];
            }
          }
        }
        for (item in declared_method_dict) {
          if (declared_method_dict.hasOwnProperty(item)) {
            declared_method_list.push(item);
          }
        }
        return declared_method_list;
          // gadget.getDeclaredMethodList()
      });
  }

  function verifyGadgetSingleInterfaceImplementation(interface_gadget,
                                                     gadget_to_check_url,
                                                     absolute_interface_url) {
    var verify_result = {};
    return new RSVP.Queue()
      .push(function () {
        return RSVP.all([
          getDefinedInterfaceMethodList(
            absolute_interface_url
          ),
          getGadgetMethodList(interface_gadget, gadget_to_check_url)
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
        gadget_to_check;

      return getOrDeclareGadget(context, context.state.gadget_to_check_url)
        .push(function (result) {
          gadget_to_check = result;
          return gadget_to_check.getInterfaceList();
        })
        .push(function (required_interface_list) {
          var result_list = [],
            i;
          for (i = 0; i < required_interface_list.length; i += 1) {
            result_list.push(
              verifyGadgetSingleInterfaceImplementation(
                context,
                context.state.gadget_to_check_url,
                required_interface_list[i]
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
          if (result_list.length === 0) {
            context.element.firstElementChild.textContent = 'N/A';
            if (!context.state.summary) {
              context.element.firstElementChild.textContent +=
                '\n' + error_message;
            }
          } else if (failed) {
            context.element.firstElementChild.textContent = 'Failure';
            if (!context.state.summary) {
              context.element.firstElementChild.textContent +=
                '\n' + error_message;
            }
          } else {
            context.element.firstElementChild.textContent = 'Success';
            if (!context.state.summary) {
              context.element.firstElementChild.textContent +=
                '\n' + error_message;
            }
          }
        })
        .push(undefined, function (error) {
          console.warn(error);
          context.element.firstElementChild.textContent =
            "Error with gadget loading";
        });

    });

}(window, rJS, RSVP, DOMParser, jIO));