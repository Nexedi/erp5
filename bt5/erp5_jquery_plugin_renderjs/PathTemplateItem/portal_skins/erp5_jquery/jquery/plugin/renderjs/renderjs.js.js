<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="File" module="OFS.Image"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>_Cacheable__manager_id</string> </key>
            <value> <string>http_cache</string> </value>
        </item>
        <item>
            <key> <string>_EtagSupport__etag</string> </key>
            <value> <string>ts62060037.0</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>renderjs.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*! RenderJs v0.2  */\n
/*global console, require, $, localStorage, document, jIO */\n
/*jslint evil: true, white: true */\n
"use strict";\n
/*\n
 * RenderJs - Generic Gadget library renderer.\n
 * http://www.renderjs.org/documentation\n
 */\n
\n
// by default RenderJs will render all gadgets when page is loaded\n
// still it\'s possible to override this and use explicit gadget rendering\n
var RENDERJS_ENABLE_IMPLICIT_GADGET_RENDERING = true;\n
\n
// by default RenderJs will examine and bind all interaction gadgets\n
// available\n
var RENDERJS_ENABLE_IMPLICIT_INTERACTION_BIND = true;\n
\n
// by default RenderJs will examine and create all routes\n
var RENDERJS_ENABLE_IMPLICIT_ROUTE_CREATE = true;\n
\n
// fallback for IE\n
if (console === undefined || console.log === undefined) {\n
    var console = {};\n
    console.log = function () {};\n
}\n
\n
var RenderJs = (function () {\n
    // a variable indicating if current gadget loading is over or not\n
    var is_ready = false, current_gadget;\n
\n
    function setSelfGadget (gadget) {\n
      /*\n
       * Only used internally to set current gadget being executed.\n
       */\n
      current_gadget = gadget;\n
    }\n
\n
    return {\n
\n
        init: function () {\n
          /*\n
           * Do all initialization\n
           */\n
          if (RENDERJS_ENABLE_IMPLICIT_GADGET_RENDERING) {\n
              RenderJs.bootstrap($(\'body\'));\n
          }\n
          var root_gadget = RenderJs.GadgetIndex.getRootGadget();\n
          if (RENDERJS_ENABLE_IMPLICIT_INTERACTION_BIND||RENDERJS_ENABLE_IMPLICIT_ROUTE_CREATE) {\n
            // We might have a page without gadgets.\n
            // Be careful, right now we can be in this case because\n
            // asynchronous gadget loading is not finished\n
            if (root_gadget !== undefined) {\n
              RenderJs.bindReady(\n
                function () {\n
                  if (RENDERJS_ENABLE_IMPLICIT_INTERACTION_BIND) {\n
                    // examine all Intaction Gadgets and bind accordingly\n
                    RenderJs.InteractionGadget.init();\n
                  }\n
                  if (RENDERJS_ENABLE_IMPLICIT_ROUTE_CREATE) {\n
                    // create all routes between gadgets\n
                    RenderJs.RouteGadget.init();\n
                  }\n
                });\n
            }\n
          }\n
        },\n
\n
        bootstrap: function (root) {\n
            /*\n
             * Load all gadgets for this DOM element\n
             * (including recursively contained ones)\n
             */\n
            var gadget_id, is_gadget;\n
            gadget_id = root.attr("id");\n
            is_gadget = root.attr("data-gadget") !== undefined;\n
            // this will make RenderJs fire "ready" event when all gadgets are loaded.\n
            RenderJs.setReady(false);\n
            if (is_gadget && gadget_id !== undefined ) {\n
              // bootstart root gadget only if it is indeed a gadget\n
              RenderJs.loadGadget(root);\n
            }\n
            RenderJs.loadRecursiveGadget(root);\n
        },\n
\n
        loadRecursiveGadget: function (root) {\n
            /*\n
             * Load all contained gadgets inside passed DOM element.\n
             */\n
            var gadget_list, gadget, gadget_id, gadget_js;\n
            gadget_list = root.find("[data-gadget]");\n
\n
            // register all gadget in advance so checkAndTriggerReady\n
            // can have accurate information for list of all gadgets\n
            gadget_list.each(function () {\n
              gadget = $(this);\n
              gadget_id = gadget.attr("id");\n
              gadget_js = new RenderJs.Gadget(gadget_id, gadget);\n
              RenderJs.GadgetIndex.registerGadget(gadget_js);\n
            });\n
\n
            // Load chilren\n
            gadget_list.each(function () {\n
                RenderJs.loadGadget($(this));\n
            });\n
        },\n
\n
        setGadgetAndRecurse: function (gadget, data) {\n
            /*\n
             * Set gadget data and recursively load it in case it holds another\n
             * gadgets.\n
             */\n
            // set current gadget as being loaded so gadget instance itself knows which gadget it is\n
            setSelfGadget(RenderJs.GadgetIndex.getGadgetById(gadget.attr("id")));\n
            gadget.append(data);\n
            // reset as no longer current gadget\n
            setSelfGadget(undefined);\n
            // a gadget may contain sub gadgets\n
            RenderJs.loadRecursiveGadget(gadget);\n
        },\n
\n
        getSelfGadget: function () {\n
           /*\n
            * Get current gadget being loaded\n
            * This function must be used with care as it relies on Javascript nature of being a single\n
            * threaded application. Currently current gadget is set in a global RenderJs variable\n
            * before its HTML is inserted into DOM and if multiple threads were running (which is not the case currently)\n
            * this could lead to reace conditions and unreliable getSelfGadget results.\n
            * Additionally this function is available only at gadget\'s script load time - i.e.\n
            * it can\'t be used in after that calls. In this case gagdget can save this value internally.\n
            */\n
           return current_gadget;\n
        },\n
\n
        loadGadget: function (gadget) {\n
            /*\n
             * Load gadget\'s SPECs from URL\n
             */\n
            var url, gadget_id, gadget_property, cacheable, cache_id,\n
                i, gadget_index, gadget_index_id,\n
                app_cache, data, gadget_js, is_update_gadget_data_running;\n
\n
            url = gadget.attr("data-gadget");\n
            gadget_id = gadget.attr("id");\n
            gadget_js = RenderJs.GadgetIndex.getGadgetById(gadget_id);\n
            gadget_index = RenderJs.GadgetIndex.getGadgetList();\n
\n
            if (gadget_js === undefined) {\n
              // register gadget in javascript namespace if not already registered\n
              gadget_js = new RenderJs.Gadget(gadget_id, gadget);\n
              RenderJs.GadgetIndex.registerGadget(gadget_js);\n
            }\n
\n
            if (gadget_js.isReady()) {\n
              // avoid loading again gadget which was loaded before in same page\n
              return ;\n
            }\n
\n
            // update Gadget\'s instance with contents of "data-gadget-property"\n
            gadget_property = gadget.attr("data-gadget-property");\n
            if (gadget_property !== undefined) {\n
              gadget_property = $.parseJSON(gadget_property);\n
              $.each(gadget_property, function (key, value) {\n
                gadget_js[key] = value;\n
              });\n
            }\n
\n
            if (url !== undefined && url !== "") {\n
                cacheable = gadget.attr("data-gadget-cacheable");\n
                cache_id = gadget.attr("data-gadget-cache-id");\n
                if (cacheable !== undefined && cache_id !== undefined) {\n
                    cacheable = Boolean(parseInt(cacheable, 10));\n
                }\n
                //cacheable = false ; // to develop faster\n
                if (cacheable) {\n
                    // get from cache if possible, use last part from URL as\n
                    // cache_key\n
                    app_cache = RenderJs.Cache.get(cache_id, undefined);\n
                    if (app_cache === undefined || app_cache === null) {\n
                        // not in cache so we pull from network and cache\n
                        $.ajax({\n
                            url: url,\n
                            yourCustomData: {\n
                                "gadget_id": gadget_id,\n
                                "cache_id": cache_id\n
                            },\n
                            success: function (data) {\n
                                cache_id = this.yourCustomData.cache_id;\n
                                gadget_id = this.yourCustomData.gadget_id;\n
                                RenderJs.Cache.set(cache_id, data);\n
                                RenderJs.GadgetIndex.getGadgetById(gadget_id).\n
                                    setReady();\n
                                RenderJs.setGadgetAndRecurse(gadget, data);\n
                                RenderJs.checkAndTriggerReady();\n
                                RenderJs.updateGadgetData(gadget);\n
                            }\n
                        });\n
                    } else {\n
                        // get from cache\n
                        data = app_cache;\n
                        gadget_js.setReady();\n
                        this.setGadgetAndRecurse(gadget, data);\n
                        this.checkAndTriggerReady();\n
                        RenderJs.updateGadgetData(gadget);\n
                    }\n
                } else {\n
                    // not to be cached\n
                    $.ajax({\n
                        url: url,\n
                        yourCustomData: {"gadget_id": gadget_id},\n
                        success: function (data) {\n
                            gadget_id = this.yourCustomData.gadget_id;\n
                            RenderJs.GadgetIndex.getGadgetById(gadget_id).\n
                                setReady();\n
                            RenderJs.setGadgetAndRecurse(gadget, data);\n
                            RenderJs.checkAndTriggerReady();\n
                            RenderJs.updateGadgetData(gadget);\n
                        }\n
                    });\n
                }\n
            }\n
            else {\n
                // gadget is an inline (InteractorGadget or one using\n
                // data-gadget-source / data-gadget-handler) so no need\n
                // to load it from network\n
                is_update_gadget_data_running = RenderJs.updateGadgetData(gadget);\n
                if (!is_update_gadget_data_running) {\n
                  // no update is running so gadget is basically ready\n
                  // if update is running then it should take care and set status\n
                  gadget_js.setReady();\n
                }\n
                RenderJs.checkAndTriggerReady();\n
            }\n
        },\n
\n
        isReady: function () {\n
            /*\n
             * Get rendering status\n
             */\n
            return is_ready;\n
        },\n
\n
        setReady: function (value) {\n
            /*\n
             * Update rendering status\n
             */\n
            is_ready = value;\n
        },\n
\n
        bindReady: function (ready_function) {\n
            /*\n
             * Bind a function on ready gadget loading.\n
             */\n
            $("body").one("ready", ready_function);\n
        },\n
\n
        checkAndTriggerReady: function () {\n
            /*\n
             * Trigger "ready" event only if all gadgets were marked as "ready"\n
             */\n
            var is_gadget_list_loaded;\n
            is_gadget_list_loaded = RenderJs.GadgetIndex.isGadgetListLoaded();\n
            if (is_gadget_list_loaded) {\n
                if (!RenderJs.isReady()) {\n
                    // backwards compatability with already written code\n
                    RenderJs.GadgetIndex.getRootGadget().getDom().\n
                        trigger("ready");\n
                    // trigger ready on root body element\n
                    $("body").trigger("ready");\n
                    // this set will make sure we fire this event only once\n
                    RenderJs.setReady(true);\n
                }\n
            }\n
            return is_gadget_list_loaded;\n
        },\n
\n
        updateGadgetData: function (gadget) {\n
            /*\n
             * Gadget can be updated from "data-gadget-source" (i.e. a json)\n
             * and "data-gadget-handler" attributes (i.e. a namespace Javascript)\n
             */\n
            var data_source, data_handler;\n
            data_source = gadget.attr("data-gadget-source");\n
            data_handler = gadget.attr("data-gadget-handler");\n
            // acquire data and pass it to method handler\n
            if (data_source !== undefined && data_source !== "") {\n
                $.ajax({\n
                    url: data_source,\n
                    dataType: "json",\n
                    yourCustomData: {"data_handler": data_handler,\n
                                     "gadget_id": gadget.attr("id")},\n
                    success: function (result) {\n
                              var data_handler, gadget_id;\n
                              data_handler = this.yourCustomData.data_handler;\n
                              gadget_id = this.yourCustomData.gadget_id;\n
                              if (data_handler !== undefined) {\n
                                  // eval is not nice to use\n
                                  eval(data_handler + "(result)");\n
                                  gadget = RenderJs.GadgetIndex.getGadgetById(gadget_id);\n
                                  // mark gadget as loaded and fire a check\n
                                  // to see if all gadgets are loaded\n
                                  gadget.setReady();\n
                                  RenderJs.checkAndTriggerReady();\n
                              }\n
                             }\n
                });\n
                // asynchronous update happens and respective thread will update status\n
                return true;\n
            }\n
            return false;\n
        },\n
\n
        addGadget: function (dom_id, gadget_id, gadget, gadget_data_handler,\n
                            gadget_data_source, bootstrap) {\n
            /*\n
             * add new gadget and render it\n
             */\n
            var html_string, tab_container, tab_gadget;\n
            tab_container = $(\'#\' + dom_id);\n
            tab_container.empty();\n
            html_string = [\n
                \'<div  id="\' + gadget_id + \'"\',\n
                \'data-gadget="\' + gadget + \'"\',\n
                \'data-gadget-handler="\' + gadget_data_handler + \'" \',\n
                \'data-gadget-source="\' + gadget_data_source + \'"></div>\'\n
            ].join(\'\\n\');\n
\n
            tab_container.append(html_string);\n
            tab_gadget = tab_container.find(\'#\' + gadget_id);\n
\n
            // render new gadget\n
            if (bootstrap !== false) {\n
              RenderJs.bootstrap(tab_container);\n
            }\n
\n
            return tab_gadget;\n
        },\n
\n
        Cache: (function () {\n
            /*\n
             * Generic cache implementation that can fall back to local\n
             * namespace storage if no "modern" storage like localStorage\n
             * is available\n
             */\n
            return {\n
                ROOT_CACHE_ID: \'APP_CACHE\',\n
\n
                getCacheId: function (cache_id) {\n
                    /*\n
                     * We should have a way to \'purge\' localStorage by setting a\n
                     * ROOT_CACHE_ID in all browser instances\n
                     */\n
                    return this.ROOT_CACHE_ID + cache_id;\n
                },\n
\n
                hasLocalStorage: function () {\n
                    /*\n
                     * Feature test if localStorage is supported\n
                     */\n
                    var mod;\n
                    mod = \'localstorage_test_12345678\';\n
                    try {\n
                        localStorage.setItem(mod, mod);\n
                        localStorage.removeItem(mod);\n
                        return true;\n
                    } catch (e) {\n
                        return false;\n
                    }\n
                },\n
\n
                get: function (cache_id, default_value) {\n
                    /* Get cache key value */\n
                    cache_id = this.getCacheId(cache_id);\n
                    if (this.hasLocalStorage()) {\n
                        return this.LocalStorageCachePlugin.\n
                            get(cache_id, default_value);\n
                    }\n
                    //fallback to javscript namespace cache\n
                    return this.NameSpaceStorageCachePlugin.\n
                        get(cache_id, default_value);\n
                },\n
\n
                set: function (cache_id, data) {\n
                    /* Set cache key value */\n
                    cache_id = this.getCacheId(cache_id);\n
                    if (this.hasLocalStorage()) {\n
                        this.LocalStorageCachePlugin.set(cache_id, data);\n
                    } else {\n
                        this.NameSpaceStorageCachePlugin.set(cache_id, data);\n
                    }\n
                },\n
\n
                LocalStorageCachePlugin: (function () {\n
                    /*\n
                     * This plugin saves using HTML5 localStorage.\n
                     */\n
                    return {\n
                        get: function (cache_id, default_value) {\n
                            /* Get cache key value */\n
                            if (localStorage.getItem(cache_id) !== null) {\n
                              return JSON.parse(localStorage.getItem(cache_id));\n
                            }\n
                            return default_value;\n
                        },\n
\n
                        set: function (cache_id, data) {\n
                            /* Set cache key value */\n
                            localStorage.setItem(cache_id, JSON.stringify(data));\n
                        }\n
                    };\n
                }()),\n
\n
                NameSpaceStorageCachePlugin: (function () {\n
                    /*\n
                     * This plugin saves within current page namespace.\n
                     */\n
                    var namespace = {};\n
\n
                    return {\n
                        get: function (cache_id, default_value) {\n
                            /* Get cache key value */\n
                            return namespace[cache_id];\n
                        },\n
\n
                        set: function (cache_id, data) {\n
                            /* Set cache key value */\n
                            namespace[cache_id] = data;\n
                        }\n
                    };\n
                }())\n
            };\n
        }()),\n
\n
        Gadget: function (gadget_id, dom) {\n
            /*\n
             * Javascript Gadget representation\n
             */\n
            this.id = gadget_id;\n
            this.dom = dom;\n
            this.is_ready = false;\n
\n
            this.getId = function () {\n
                return this.id;\n
            };\n
\n
            this.getDom = function () {\n
                return this.dom;\n
            };\n
\n
            this.isReady = function () {\n
                /*\n
                 * Return True if remote gadget is loaded into DOM.\n
                 */\n
                return this.is_ready;\n
            };\n
\n
            this.setReady = function () {\n
                /*\n
                 * Return True if remote gadget is loaded into DOM.\n
                 */\n
                this.is_ready = true;\n
            };\n
\n
            this.remove = function () {\n
                /*\n
                 * Remove gadget (including its DOM element).\n
                 */\n
                var gadget;\n
                // unregister root from GadgetIndex\n
                RenderJs.GadgetIndex.unregisterGadget(this);\n
                // gadget might contain sub gadgets so before remove entire\n
                // DOM we must unregister them from GadgetIndex\n
                this.getDom().find("[data-gadget]").each( function () {\n
                  gadget = RenderJs.GadgetIndex.getGadgetById($(this).attr("id"));\n
                  RenderJs.GadgetIndex.unregisterGadget(gadget);\n
                });\n
                // remove root\'s entire DOM element\n
                $(this.getDom()).remove();\n
            };\n
        },\n
\n
        TabbularGadget: (function () {\n
            /*\n
             * Generic tabular gadget\n
             */\n
            var gadget_list = [];\n
            return {\n
                toggleVisibility: function (visible_dom) {\n
                    /*\n
                     * Set tab as active visually and mark as not active rest.\n
                     */\n
                    $(".selected").addClass("not_selected");\n
                    $(".selected").removeClass("selected");\n
                    visible_dom.addClass("selected");\n
                    visible_dom.removeClass("not_selected");\n
                },\n
\n
                addNewTabGadget: function (dom_id, gadget_id, gadget, gadget_data_handler,\n
                                          gadget_data_source, bootstrap) {\n
                    /*\n
                     * add new gadget and render it\n
                     */\n
                    var tab_gadget;\n
                    tab_gadget = RenderJs.addGadget(\n
                        dom_id, gadget_id, gadget, gadget_data_handler, gadget_data_source, bootstrap\n
                    );\n
\n
                    // we should unregister all gadgets part of this TabbularGadget\n
                    $.each(gadget_list,\n
                         function (index, gadget_id) {\n
                           var gadget = RenderJs.GadgetIndex.getGadgetById(gadget_id);\n
                           gadget.remove();\n
                           // update list of root gadgets inside TabbularGadget\n
                           gadget_list.splice($.inArray(gadget_id, gadget_list), 1);\n
                        }\n
                    );\n
                    // add it as root gadget\n
                    gadget_list.push(tab_gadget.attr("id"));\n
                }\n
            };\n
        }()),\n
\n
        GadgetIndex: (function () {\n
            /*\n
             * Generic gadget index placeholder\n
             */\n
            var gadget_list = [];\n
\n
            return {\n
\n
                getGadgetIdListFromDom: function (dom) {\n
                  /*\n
                   * Get list of all gadget\'s ID from DOM\n
                   */\n
                  var gadget_id_list = [];\n
                  $.each(dom.find(\'[data-gadget]\'),\n
                         function (index, value) {\n
                           gadget_id_list.push($(value).attr("id"));}\n
                    );\n
                  return gadget_id_list;\n
                },\n
\n
                setGadgetList: function (gadget_list_value) {\n
                    /*\n
                     * Set list of registered gadgets\n
                     */\n
                    gadget_list = gadget_list_value;\n
                },\n
\n
                getGadgetList: function () {\n
                    /*\n
                     * Return list of registered gadgets\n
                     */\n
                    return gadget_list;\n
                },\n
\n
                registerGadget: function (gadget) {\n
                    /*\n
                     * Register gadget\n
                     */\n
                    if (RenderJs.GadgetIndex.getGadgetById(gadget.id) === undefined) {\n
                      // register only if not already added\n
                      gadget_list.push(gadget);\n
                    }\n
                },\n
\n
                unregisterGadget: function (gadget) {\n
                    /*\n
                     * Unregister gadget\n
                     */\n
                    var index = $.inArray(gadget, gadget_list);\n
                    if (index !== -1) {\n
                        gadget_list.splice(index, 1);\n
                    }\n
                },\n
\n
                getGadgetById: function (gadget_id) {\n
                    /*\n
                     * Get gadget javascript representation by its Id\n
                     */\n
                    var gadget;\n
                    gadget = undefined;\n
                    $(RenderJs.GadgetIndex.getGadgetList()).each(\n
                        function (index, value) {\n
                            if (value.getId() === gadget_id) {\n
                                gadget = value;\n
                            }\n
                        }\n
                    );\n
                    return gadget;\n
                },\n
\n
                getRootGadget: function () {\n
                    /*\n
                     * Return root gadget (always first one in list)\n
                     */\n
                    return this.getGadgetList()[0];\n
                },\n
\n
                isGadgetListLoaded: function () {\n
                    /*\n
                     * Return True if all gadgets were loaded from network or\n
                     * cache\n
                     */\n
                    var result;\n
                    result = true;\n
                    $(this.getGadgetList()).each(\n
                        function (index, value) {\n
                            if (value.isReady() === false) {\n
                                result = false;\n
                            }\n
                        }\n
                    );\n
                    return result;\n
                }\n
            };\n
        }()),\n
\n
        GadgetCatalog : (function () {\n
            /*\n
             * Gadget catalog provides API to get list of gadgets from a repository\n
             */\n
            var cache_id = "setGadgetIndexUrlList";\n
\n
            function updateGadgetIndexFromURL(url) {\n
              // split to base and document url\n
              var url_list = url.split(\'/\'),\n
                  document_url = url_list[url_list.length-1],\n
                  d = url_list.splice($.inArray(document_url, url_list), 1),\n
                  base_url = url_list.join(\'/\'),\n
                  web_dav = jIO.newJio({\n
                      "type": "dav",\n
                      "username": "",\n
                      "password": "",\n
                      "url": base_url});\n
              web_dav.get(document_url,\n
                          function (err, response) {\n
                            RenderJs.Cache.set(url, response);\n
              });\n
            }\n
\n
            return {\n
                updateGadgetIndex: function () {\n
                  /*\n
                   * Update gadget index from all configured remote repositories.\n
                   */\n
                  $.each(RenderJs.GadgetCatalog.getGadgetIndexUrlList(),\n
                         function(index, value) {\n
                          updateGadgetIndexFromURL(value);\n
                         });\n
                },\n
\n
                setGadgetIndexUrlList: function (url_list) {\n
                  /*\n
                   * Set list of Gadget Index repositories.\n
                   */\n
                  // store in Cache (html5 storage)\n
                  RenderJs.Cache.set(cache_id, url_list);\n
                },\n
\n
                getGadgetIndexUrlList: function () {\n
                  /*\n
                   * Get list of Gadget Index repositories.\n
                   */\n
                  // get from Cache (html5 storage)\n
                  return RenderJs.Cache.get(cache_id, undefined);\n
                },\n
\n
                getGadgetListThatProvide: function (service) {\n
                  /*\n
                   * Return list of all gadgets that providen a given service.\n
                   * Read this list from data structure created in HTML5 local\n
                   * storage by updateGadgetIndexFromURL\n
                   */\n
                  // get from Cache stored index and itterate over it\n
                  // to find matching ones\n
                  var gadget_list = [];\n
                  $.each(RenderJs.GadgetCatalog.getGadgetIndexUrlList(),\n
                         function(index, url) {\n
                           // get repos from cache\n
                           var cached_repo = RenderJs.Cache.get(url);\n
                           $.each(cached_repo.gadget_list,\n
                                   function(index, gadget) {\n
                                     if ($.inArray(service, gadget.service_list) > -1) {\n
                                       // gadget provides a service, add to list\n
                                       gadget_list.push(gadget);\n
                                     }\n
                                  }\n
                                 );\n
                         });\n
                  return gadget_list;\n
                },\n
\n
                registerServiceList: function (gadget, service_list) {\n
                  /*\n
                   * Register a service provided by a gadget.\n
                   */\n
                }\n
            };\n
        }()),\n
\n
        InteractionGadget : (function () {\n
            /*\n
             * Basic gadget interaction gadget implementation.\n
             */\n
            return {\n
\n
                init: function (force) {\n
                        /*\n
                        * Inspect DOM and initialize this gadget\n
                        */\n
                        var dom_list, gadget_id;\n
                        if (force===1) {\n
                          // we explicitly want to re-init elements even if already this is done before\n
                          dom_list = $("div[data-gadget-connection]");\n
                        }\n
                        else {\n
                          // XXX: improve and save \'bound\' on javascript representation of a gadget not DOM\n
                          dom_list = $("div[data-gadget-connection]")\n
                                       .filter(function() { return $(this).data("bound") !== true; })\n
                                       .data(\'bound\', true );\n
                        }\n
                        dom_list.each(function (index, element) {\n
                          RenderJs.InteractionGadget.bind($(element));});\n
                },\n
\n
                bind: function (gadget_dom) {\n
                    /*\n
                     * Bind event between gadgets.\n
                     */\n
                    var gadget_id, gadget_connection_list,\n
                      createMethodInteraction = function (\n
                        original_source_method_id, source_gadget_id,\n
                        source_method_id, destination_gadget_id,\n
                        destination_method_id) {\n
                        var interaction = function () {\n
                            // execute source method\n
                            RenderJs.GadgetIndex.getGadgetById(\n
                                source_gadget_id)[original_source_method_id].\n
                                apply(null, arguments);\n
                            // call trigger so bind can be asynchronously called\n
                            RenderJs.GadgetIndex.getGadgetById(\n
                                destination_gadget_id).dom.trigger(source_method_id);\n
                        };\n
                        return interaction;\n
                    },\n
                    createTriggerInteraction = function (\n
                        destination_gadget_id, destination_method_id) {\n
                        var interaction = function () {\n
                            RenderJs.GadgetIndex.getGadgetById(\n
                                destination_gadget_id)[destination_method_id].\n
                                apply(null, arguments);\n
                        };\n
                        return interaction;\n
                    };\n
                    gadget_id = gadget_dom.attr("id");\n
                    gadget_connection_list = gadget_dom.attr("data-gadget-connection");\n
                    gadget_connection_list = $.parseJSON(gadget_connection_list);\n
                    $.each(gadget_connection_list, function (key, value) {\n
                        var source, source_gadget_id, source_method_id,\n
                        source_gadget, destination, destination_gadget_id,\n
                        destination_method_id, destination_gadget,\n
                        original_source_method_id;\n
                        source = value.source.split(".");\n
                        source_gadget_id = source[0];\n
                        source_method_id = source[1];\n
                        source_gadget = RenderJs.GadgetIndex.\n
                            getGadgetById(source_gadget_id);\n
\n
                        destination = value.destination.split(".");\n
                        destination_gadget_id = destination[0];\n
                        destination_method_id = destination[1];\n
                        destination_gadget = RenderJs.GadgetIndex.\n
                            getGadgetById(destination_gadget_id);\n
\n
                        if (source_gadget.hasOwnProperty(source_method_id)) {\n
                            // direct javascript use case\n
                            original_source_method_id = "original_" +\n
                                source_method_id;\n
                            source_gadget[original_source_method_id] =\n
                                source_gadget[source_method_id];\n
                            source_gadget[source_method_id] =\n
                                createMethodInteraction(\n
                                    original_source_method_id,\n
                                    source_gadget_id,\n
                                    source_method_id,\n
                                    destination_gadget_id,\n
                                    destination_method_id\n
                                );\n
                            // we use html custom events for asyncronous method call so\n
                            // bind destination_gadget to respective event\n
                            destination_gadget.dom.bind(\n
                                source_method_id,\n
                                createTriggerInteraction(\n
                                    destination_gadget_id, destination_method_id\n
                                )\n
                            );\n
                        }\n
                        else {\n
                            // this is a custom event attached to HTML gadget\n
                            // representation\n
                            source_gadget.dom.bind(\n
                                source_method_id,\n
                                createTriggerInteraction(\n
                                    destination_gadget_id, destination_method_id\n
                                )\n
                            );\n
                        }\n
                    });\n
                }\n
            };\n
        }()),\n
\n
        RouteGadget : (function () {\n
            /*\n
             * A gadget that defines possible routes (i.e. URL changes) between gadgets.\n
             */\n
            var route_list = [];\n
            return {\n
\n
                init: function () {\n
                  /*\n
                   * Inspect DOM and initialize this gadget\n
                   */\n
                  $("div[data-gadget-route]").each(function (index, element) {\n
                      RenderJs.RouteGadget.route($(element));\n
                  });\n
                },\n
\n
                route: function (gadget_dom) {\n
                    /*\n
                     * Create routes between gadgets.\n
                     */\n
                  var body = $("body"),\n
                      handler_func, priority,\n
                      gadget_route_list = gadget_dom.attr("data-gadget-route");\n
                  gadget_route_list = $.parseJSON(gadget_route_list);\n
                  $.each(gadget_route_list, function (key, gadget_route) {\n
                    handler_func = function () {\n
                        var gadget_id = gadget_route.destination.split(\'.\')[0],\n
                            method_id = gadget_route.destination.split(\'.\')[1],\n
                            gadget = RenderJs.GadgetIndex.getGadgetById(gadget_id);\n
                        // set gadget value so getSelfGadget can work\n
                        setSelfGadget(gadget);\n
                        gadget[method_id].apply(null, arguments);\n
                        // reset as no longer needed\n
                        setSelfGadget(undefined);\n
                    };\n
                    // add route itself\n
                    priority = gadget_route.priority;\n
                    if (priority === undefined) {\n
                      // default is 1 -i.e.first level\n
                      priority = 1;\n
                    }\n
                    RenderJs.RouteGadget.add(gadget_route.source, handler_func, priority);\n
                  });\n
                },\n
\n
                add: function (path, handler_func, priority) {\n
                    /*\n
                     * Add a route between path (hashable) and a handler function (part of Gadget\'s API).\n
                     */\n
                  var body = $("body");\n
                  body\n
                      .route("add", path, 1)\n
                      .done(handler_func);\n
                  // save locally\n
                  route_list.push({"path": path,\n
                                   "handler_func": handler_func,\n
                                   "priority": priority});\n
                },\n
\n
                go: function (path, handler_func, priority) {\n
                    /*\n
                     * Go a route.\n
                     */\n
                  var body = $("body");\n
                  body\n
                      .route("go", path, priority)\n
                      .fail(handler_func);\n
                },\n
\n
                remove: function (path) {\n
                    /*\n
                     * Remove a route.\n
                     */\n
\n
                    // XXX: implement remove a route when route.js supports it\n
                },\n
\n
                getRouteList: function () {\n
                    /*\n
                     * Get list of all router\n
                     */\n
                  return route_list;\n
                }\n
            };\n
        }())\n
    };\n
}());

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>36851</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>renderjs.js</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
