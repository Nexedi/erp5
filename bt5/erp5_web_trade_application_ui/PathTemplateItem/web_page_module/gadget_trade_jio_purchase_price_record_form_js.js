/*globals window, document, RSVP, rJS,promiseEventListener,
            getSequentialID*/
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, RSVP, rJS) {
  "use strict";

  /////////////////////////////////////////
  // PreviousOwner changed
  /////////////////////////////////////////
  function changePreviousOwner(gadget, previous_owner_change) {
    var page_gadget = gadget,
      form_gadget,
      result_tmp,
      disabled = 0,
      previous_owner_title,
      previous_owner_reference,
      default_telephone_coordinate_text,
      default_address_city,
      default_address_region,
      default_address_street_address,
      default_address_zip_code,
      default_email_coordinate_text;
    return new RSVP.Queue()
      .push(function () {
        return gadget.allDocs({
          query: 'portal_type:Organisation AND title_lowercase: "'
                  + page_gadget.valueChange.toLowerCase() + '"',
          limit: [0, 2]
        });
      })
      .push(function (result) {
        if (result.data.total_rows === 1) {
          return gadget.jio_get(result.data.rows[0].id);
        }
      })
      .push(function (result) {
        result_tmp = result;
        return page_gadget.getDeclaredGadget("trade_form");
      })
      .push(function (gadget) {
        form_gadget = gadget;
        if (result_tmp !== undefined) {
          previous_owner_title =  result_tmp.organisation_title;
          previous_owner_reference =  result_tmp.organisation_reference;
          default_telephone_coordinate_text =
            result_tmp.default_telephone_coordinate_text;
          default_address_city =  result_tmp.default_address_city;
          default_address_region =  result_tmp.default_address_region;
          default_address_street_address =
            result_tmp.default_address_street_address;
          default_address_zip_code =
            result_tmp.default_address_zip_code;
          default_email_coordinate_text =
            result_tmp.default_email_coordinate_text;

          return RSVP.all([
            form_gadget.render({
              erp5_document: {"_embedded": {"_view": {
                field_json : {
                  "description": "",
                  "title": "Client",
                  "default": previous_owner_title,
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "next_owner_title",
                  "hidden": 0,
                  "type": "StringField",
                  "disabled" : disabled
                }
              }
                                         }},

              gadget_created: "previous_owner_title"
            }),

            form_gadget.render({
              erp5_document: {"_embedded": {"_view": {
                field_json : {
                  "description": "",
                  "title": "Client Reference",
                  "default": previous_owner_reference,
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "next_owner_reference",
                  "hidden": 0,
                  "type": "StringField",
                  "disabled" : disabled
                }
              }
                                         }},

              gadget_created: "previous_owner_reference"
            }),

            form_gadget.render({
              erp5_document: {"_embedded": {"_view": {
                field_json : {
                  "description": "",
                  "title": "Default Telephone",
                  "default": default_telephone_coordinate_text,
                  "css_class": "",
                  "required": 0,
                  "editable": 1,
                  "key": "default_telephone_coordinate_text",
                  "hidden": 0,
                  "type": "StringField",
                  "disabled" : disabled
                }
              }
                                         }},

              gadget_created: "default_telephone_coordinate_text"
            }),

            form_gadget.render({
              erp5_document: {"_embedded": {"_view": {
                field_json : {
                  "description": "",
                  "title": "Default Address City",
                  "default": default_address_city,
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "default_address_city",
                  "hidden": 0,
                  "type": "StringField",
                  "disabled" : disabled
                }
              }
                                         }},

              gadget_created: "default_address_city"
            }),

            form_gadget.render({
              erp5_document: {"_embedded": {"_view": {
                field_json : {
                  "description": "",
                  "title": "Region",
                  "default": default_address_region,
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "default_address_region",
                  "hidden": 0,
                  "type": "ListField",
                  "disabled" : disabled
                }
              }
                                         }},

              gadget_created: "default_address_region"
            }),

            form_gadget.render({
              erp5_document: {"_embedded": {"_view": {
                field_json : {
                  "description": "",
                  "title": "Street Address",
                  "default": default_address_street_address,
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "default_address_street_address",
                  "hidden": 0,
                  "type": "StringField",
                  "disabled" : disabled
                }
              }
                                         }},

              gadget_created: "default_address_street_address"
            }),

            form_gadget.render({
              erp5_document: {"_embedded": {"_view": {
                field_json : {
                  "description": "",
                  "title": "Postal Code",
                  "default": default_address_zip_code,
                  "css_class": "",
                  "required": 0,
                  "editable": 1,
                  "key": "default_address_zip_code",
                  "hidden": 0,
                  "type": "StringField",
                  "disabled" : disabled
                }
              }
                                         }},

              gadget_created: "default_address_zip_code"
            }),

            form_gadget.render({
              erp5_document: {"_embedded": {"_view": {
                field_json : {
                  "description": "",
                  "title": "Email",
                  "default": default_email_coordinate_text,
                  "css_class": "",
                  "required": 0,
                  "editable": 1,
                  "key": "default_email_coordinate_text",
                  "hidden": 0,
                  "type": "StringField",
                  "disabled" : disabled
                }
              }
                                         }},
              gadget_created: "default_email_coordinate_text"
            })

          ]);
        }
        if (previous_owner_change === 1) {
          previous_owner_title = page_gadget.valueChange;
          return form_gadget.render({
            erp5_document: {"_embedded": {"_view": {
              field_json : {
                "description": "",
                "title": "Client",
                "default": previous_owner_title,
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "previous_owner_title",
                "hidden": 0,
                "type": "StringField",
                "disabled" : disabled
              }
            }
                                         }},

            gadget_created: "previous_owner_title"
          });
        }
      })
        .push(function () {
        var change_previous_owner_flag;
        if (previous_owner_change === 1) {
          if (result_tmp !== undefined  &&
                result_tmp.organisation_title !== page_gadget.valueChange) {
            change_previous_owner_flag = 1;
            page_gadget.valueChange = result_tmp.organisation_title;
          }
        } else {
          change_previous_owner_flag = 1;
          if (result_tmp !== undefined
              && result_tmp.organisation_title !== page_gadget.valueChange) {
            page_gadget.valueChange = result_tmp.organisation_title;
          }
        }

        if (change_previous_owner_flag === 1) {
          return form_gadget.render({
            erp5_document: {"_embedded": {"_view": {
              field_json : {
                "description": "",
                "title": "Client",
                "default": page_gadget.valueChange,
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "next_owner_title",
                "hidden": 0,
                "type": "StringField",
                "disabled" : disabled
              }
            }
                                         }},

            gadget_created: "previous_owner"
          });
        }
      });
  }

    /////////////////////////////////////////
    // Product changed.
    /////////////////////////////////////////
  function changeProduct(gadget, product_change) {
    var page_gadget = gadget,
      form_gadget,
      result_tmp,
      disabled = 0,
      product_title,
      product_reference,
      product_line;
    return new RSVP.Queue()
      .push(function () {
        return page_gadget.allDocs({
          query: 'portal_type:Product AND title_lowercase: "'
                  + page_gadget.valueChange.toLowerCase() + '"',
          limit: [0, 2]
        });
      })
      .push(function (result) {
        if (result.data.total_rows === 1) {
          return page_gadget.jio_get(result.data.rows[0].id);
        }
      })
      .push(function (result) {
        result_tmp = result;
        return page_gadget.getDeclaredGadget("trade_form");
      })
      .push(function (gadget) {
        form_gadget = gadget;
        if (result_tmp !== undefined) {
          product_title =  result_tmp.product_title;
          product_reference =  result_tmp.product_reference;
          product_line = result_tmp.product_line;
          if (page_gadget.productTitleChange) {
            product_title = page_gadget.valueChange;
            page_gadget.productTitleChange = 0;
          }
          return RSVP.all([
            form_gadget.render({
              erp5_document: {"_embedded": {"_view": {
                field_json : {
                  "description": "",
                  "title": "Title",
                  "default": product_title,
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "product_title",
                  "hidden": 0,
                  "type": "StringField",
                  "disabled" : disabled
                }
              }
                                         }},

              gadget_created: "product_title"
            }),

            form_gadget.render({
              erp5_document: {"_embedded": {"_view": {
                field_json : {
                  "description": "",
                  "title": "Product or Material Line",
                  "default": product_line,
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "product_line",
                  "hidden": 0,
                  "type": "ListField",
                  "disabled" : disabled
                }
              }
                                         }},

              gadget_created: "product_line"
            }),

            form_gadget.render({
              erp5_document: {"_embedded": {"_view": {
                field_json : {
                  "description": "",
                  "title": "Reference",
                  "default": product_reference,
                  "css_class": "",
                  "required": 0,
                  "editable": 1,
                  "key": "product_reference",
                  "hidden": 0,
                  "type": "StringField",
                  "disabled" : disabled
                }
              }
                                         }},

              gadget_created: "product_reference"
            })
          ]);
        }
        if (product_change === 1) {
          product_title = page_gadget.valueChange;
          return form_gadget.render({
            erp5_document: {"_embedded": {"_view": {
              field_json : {
                "description": "",
                "title": "Title",
                "default": product_title,
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "product_title",
                "hidden": 0,
                "type": "StringField",
                "disabled" : disabled
              }
            }
                                         }},

            gadget_created: "product_title"
          });
        }
      })
           .push(function () {
        var change_product_flag;
        if (product_change === 1) {
          if (result_tmp !== undefined  &&
                result_tmp.product_title !== page_gadget.valueChange) {
            change_product_flag = 1;
            page_gadget.valueChange = result_tmp.product_title;
          }
        } else {
          change_product_flag = 1;
          if (result_tmp !== undefined
              && result_tmp.product_title !== page_gadget.valueChange) {
            page_gadget.valueChange = result_tmp.product_title;
          }
        }

        if (change_product_flag === 1) {
          return form_gadget.render({
            erp5_document: {"_embedded": {"_view": {
              field_json : {
                "description": "",
                "title": "Product or Material Title",
                "default": page_gadget.valueChange,
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "product",
                "hidden": 0,
                "type": "StringField",
                "disabled" : 0
              }
            }
                                         }},
            gadget_created: "product"
          });
        }
      });
  }


  rJS(window)
    /////////////////////////////////////////////////////////////////
    // ready
    /////////////////////////////////////////////////////////////////
    // Init local properties
    .ready(function (g) {
      g.props = {};
      g.props.region = [];
      g.props.quantity_unit = [];
      g.props.currency = [];
      g.props.product_line = [];
    })

    // Assign the element to a variable
    .ready(function (g) {
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
        });
    })

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("setSetting", "setSetting")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod('allDocs', 'jio_allDocs')

    .allowPublicAcquisition("inputChange", function (param_list) {
      this.gadgetChange = param_list[1];
      if (this.gadgetChange === "previous_owner") {
        this.valueChange = param_list[0].previous_owner;
        return changePreviousOwner(this, 1);
      }
      if (this.gadgetChange === "previous_owner_title") {
        this.valueChange = param_list[0].previous_owner_title;
        return changePreviousOwner(this, 0);
      }
      if (this.gadgetChange === "product") {
        this.valueChange = param_list[0].product;
        return changeProduct(this, 1);
      }
      if (this.gadgetChange === "product_title") {
        this.valueChange = param_list[0].product_title;
        return changeProduct(this, 0);
      }
    })


    .declareMethod("getContent", function () {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return gadget.getDeclaredGadget("trade_form");
        })
        .push(function (trade_form) {
          return trade_form.getContent({"format": "json"});
        })
        .push(function (result) {
          return result;
        });
    })

    .declareMethod("render", function (options) {
      var page_gadget = this,
        title,
        relative_url,
        editable = 1;
      page_gadget.options = options;
      if (page_gadget.options.doc.date === undefined) {
        page_gadget.options.doc.date = new Date().toISOString().split('T')[0];
      }
      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            page_gadget.allDocs({
              query: 'portal_type:' +
                '"Currency" AND validation_state: "validated"',
              select_list: ["title", "logical_path", "relative_url"],
              // sort_on: [["id", "ascending"]],
              limit: [0, 1234567890]
            }),

            page_gadget.allDocs({
              query: 'portal_type:' +
                '"Category" AND relative_url: "quantity_unit/%"',
              select_list: ["title", "logical_path", "category_relative_url"],
              // sort_on: [["id", "ascending"]],
              limit: [0, 1234567890]
            }),

            page_gadget.allDocs({
              query: 'portal_type:' +
                '"Category" AND relative_url: "region/%"',
              select_list: ["title", "logical_path", "category_relative_url"],
              // sort_on: [["id", "ascending"]],
              limit: [0, 1234567890]
            }),

            page_gadget.allDocs({
              query: 'portal_type: "Category"' +
                'AND relative_url: "product_line/%"',
              select_list: ["title", "logical_path", "category_relative_url"],
            // sort_on: [["id", "ascending"]],
              limit: [0, 1234567890]
            })
          ]);
        })
        .push(function (all_result) {
          var i;
          for (i = 0; i < all_result[0].data.total_rows; i += 1) {
            title = all_result[0].data.rows[i].value.title;
            relative_url = all_result[0].data.rows[i].value.relative_url;
            page_gadget.props.currency.push([title, relative_url]);
          }

          for (i = 0; i < all_result[1].data.total_rows; i += 1) {
            title =  all_result[1].data.rows[i]
              .value.logical_path || all_result[1].data.rows[i]
              .value.title;
            relative_url = all_result[1].data.rows[i]
              .value.category_relative_url;
            page_gadget.props.quantity_unit.push([title, relative_url]);
          }

          page_gadget.props.region.push(["", ""]);

          for (i = 0; i < all_result[2].data.total_rows; i += 1) {
            title = all_result[2].data.rows[i]
              .value.logical_path || all_result[2].data.rows[i]
              .value.title;
            relative_url = all_result[2].data.rows[i]
              .value.category_relative_url;
            page_gadget.props.region.push([title, relative_url]);
          }

          page_gadget.props.product_line.push(["", ""]);

          for (i = 0; i < all_result[3].data.total_rows; i += 1) {
            title = all_result[3].data.rows[i]
              .value.logical_path || all_result[3].data.rows[i]
              .value.title;
            relative_url = all_result[3].data.rows[i]
              .value.category_relative_url;
            page_gadget.props.product_line.push([title, relative_url]);
          }
          return;
        })
        .push(function () {
          return page_gadget.getDeclaredGadget("trade_form");
        })
        .push(function (form_gadget) {
          return form_gadget.render({
            erp5_document: {"_embedded": {"_view": {
              "purchase_price": {
                "description": "",
                "title": "",
                "default": "Purchase price of a specific product" +
                  "or material from a specific supplier",
                "css_class": "ui-content-header-inline",
                "required": 1,
                "editable": 0,
                "key": "purchase_price",
                "hidden": 0,
                "type": "ReadonlyField"
              },

              "product": {
                "description": "",
                "title": "Product or Material Title",
                "default": page_gadget.options.doc.product,
                "css_class": "",
                "required": 1,
                "editable": editable,
                "key": "product",
                "hidden": 0,
                "type": "StringField"
              },
              "previous_owner": {
                "description": "",
                "title": "Supplier",
                "default": page_gadget.options.doc.previous_owner,
                "css_class": "",
                "required": 1,
                "editable": editable,
                "key": "previous_owner",
                "hidden": 0,
                "type": "StringField"
              },
              "next_owner": {
                "description": "",
                "title": "Purchase Organisation",
                "default": page_gadget.options.doc.next_owner,
                "css_class": "",
                "required": 1,
                "editable": editable,
                "key": "next_owner",
                "hidden": 0,
                "type": "StringField"
              },
              "price": {
                "description": "",
                "title": "Price",
                "default": page_gadget.options.doc.base_price,
                "css_class": "",
                "required": 1,
                "editable": editable,
                "key": "base_price",
                "precision": 2,
                "hidden": 0,
                "type": "FloatField"
              },
              "currency": {
                "description": "",
                "title": "Currency",
                "default": page_gadget.options.doc.price_currency,
                "items": page_gadget.props.currency,
                "css_class": "",
                "required": 1,
                "editable": editable,
                "key": "price_currency",
                "hidden": 0,
                "type": "ListField"
              },
              "priced_quantity": {
                "description": "",
                "title": "Priced Quantity",
                "default": 1,
                "css_class": "",
                "required": 1,
                "editable": 0,
                "key": "priced_quantity",
                "hidden": 0,
                "precision": 0,
                "type": "FloatField"
              },
              "quantity_unit": {
                "description": "",
                "title": "Quantity Unit",
                "default": page_gadget.options.doc.quantity_unit,
                "items": page_gadget.props.quantity_unit,
                "css_class": "",
                "required": 1,
                "editable": editable,
                "key": "quantity_unit",
                "hidden": 0,
                "type": "ListField"
              },
              "date": {
                "description": "",
                "title": "Input Date",
                "default": page_gadget.options.doc.date,
                "css_class": "",
                "required": 0,
                "date_only": 1,
                "date_only_style": 1,
                "subfield_year_key": "year",
                "subfield_month_key": "month",
                "subfield_day_key": "day",
                "timezone_style": 0,
                "editable": editable,
                "key": "date",
                "hidden": 0,
                "type": "DateTimeField"
              },
              "contract_no": {
                "description": "",
                "title": "Contract No",
                "default": page_gadget.options.doc.contract_no,
                "css_class": "",
                "required": 1,
                "editable": editable,
                "key": "contract_no",
                "hidden": 0,
                "type": "StringField"
              },
              "comment": {
                "description": "",
                "title": "Comment",
                "default": page_gadget.options.doc.comment,
                "css_class": "",
                "required": 1,
                "editable": editable,
                "key": "comment",
                "hidden": 0,
                "type": "TextAreaField"
              },
              "purchased_product": {
                "description": "",
                "title": "",
                "default": "Purchased product or material",
                "css_class": "ui-content-header-inline",
                "required": 1,
                "editable": editable,
                "key": "purchased_product",
                "hidden": 0,
                "type": "ReadonlyField"
              },

              "product_title": {
                "description": "",
                "title": "Title",
                "default": page_gadget.options.doc.product_title,
                "css_class": "",
                "required": 1,
                "editable": editable,
                "key": "product_title",
                "hidden": 0,
                "type": "StringField"
              },
              "product_line": {
                "description": "",
                "title": "Product or Material Line",
                "default": page_gadget.options.doc.product_line,
                "items": page_gadget.props.product_line,
                "css_class": "",
                "required": 1,
                "editable": editable,
                "key": "product_line",
                "hidden": 0,
                "type": "ListField"
              },
              "product_reference": {
                "description": "",
                "title": "Reference",
                "default": page_gadget.options.doc.product_reference,
                "css_class": "",
                "required": 1,
                "editable": editable,
                "key": "product_reference",
                "hidden": 0,
                "type": "StringField"
              },

              "client_head": {
                "description": "",
                "title": "",
                "default": "Supplier",
                "css_class": "ui-content-header-inline",
                "required": 1,
                "editable": 1,
                "key": "client_head",
                "hidden": 0,
                "type": "ReadonlyField"
              },

              "client": {
                "description": "",
                "title": "Supplier Title",
                "default": page_gadget.options.doc.previous_owner_title,
                "css_class": "",
                "required": 1,
                "editable": editable,
                "key": "previous_owner_title",
                "hidden": 0,
                "type": "StringField"
              },
              "client_reference": {
                "description": "",
                "title": "Supplier Reference",
                "default": page_gadget.options.doc.previous_owner_reference,
                "css_class": "",
                "required": 1,
                "editable": editable,
                "key": "previous_owner_reference",
                "hidden": 0,
                "type": "StringField"
              },
              "telephone": {
                "description": "",
                "title": "Default Telephone",
                "default":
                  page_gadget.options.doc.default_telephone_coordinate_text,
                "css_class": "",
                "required": 0,
                "editable": editable,
                "key": "default_telephone_coordinate_text",
                "hidden": 0,
                "precision": 0,
                "type": "StringField"
              },
              "address_city": {
                "description": "",
                "title": "Default Address City",
                "default": page_gadget.options.doc.default_address_city,
                "css_class": "",
                "required": 1,
                "editable": editable,
                "key": "default_address_city",
                "hidden": 0,
                "type": "StringField"
              },
              "region": {
                "description": "",
                "title": "Region",
                "default": page_gadget.options.doc.default_address_region,
                "items": page_gadget.props.region,
                "css_class": "",
                "required": 1,
                "editable": editable,
                "key": "default_address_region",
                "hidden": 0,
                "type": "ListField"
              },
              "address_street": {
                "description": "",
                "title": "Street Address",
                "default":
                  page_gadget.options.doc.default_address_street_address,
                "css_class": "",
                "required": 1,
                "editable": editable,
                "key": "default_address_street_address",
                "hidden": 0,
                "type": "StringField"
              },
              "postal_code": {
                "description": "",
                "title": "Postal Code",
                "default":
                  page_gadget.options.doc.default_address_zip_code,
                "css_class": "",
                "required": 0,
                "editable": editable,
                "key": "default_address_zip_code",
                "hidden": 0,
                "precision": 0,
                "type": "StringField"
              },
              "email": {
                "description": "",
                "title": "Email",
                "default":
                  page_gadget.options.doc.default_email_coordinate_text,
                "css_class": "",
                "required": 0,
                "editable": editable,
                "key": "default_email_coordinate_text",
                "hidden": 0,
                "type": "StringField"
              }
            }}},
            form_definition: {
              group_list: [
                ["left",
                  [["purchase_price"], ["product"], ["previous_owner"],
                    ["next_owner"], ["price"], ["currency"],
                    ["priced_quantity"], ["quantity_unit"], ["date"],
                    ["contract_no"], ["comment"]]
                  ],
                ["right",
                  [["purchased_product"],
                    ["product_title"], ["product_line"], ["product_reference"],
                    ["client_head"],
                    ["client"], ["client_reference"], ["telephone"],
                    ["address_city"], ["region"], ["address_street"],
                    ["postal_code"], ["email"]]
                  ]
              ]
            }
          });
        });
    });
}(window, RSVP, rJS));
