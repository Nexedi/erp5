<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="File" module="OFS.Image"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>_EtagSupport__etag</string> </key>
            <value> <string>ts44308802.08</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>application.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

﻿/*\r\n
 * (c) Copyright Ascensio System SIA 2010-2015\r\n
 *\r\n
 * This program is a free software product. You can redistribute it and/or \r\n
 * modify it under the terms of the GNU Affero General Public License (AGPL) \r\n
 * version 3 as published by the Free Software Foundation. In accordance with \r\n
 * Section 7(a) of the GNU AGPL its Section 15 shall be amended to the effect \r\n
 * that Ascensio System SIA expressly excludes the warranty of non-infringement\r\n
 * of any third-party rights.\r\n
 *\r\n
 * This program is distributed WITHOUT ANY WARRANTY; without even the implied \r\n
 * warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR  PURPOSE. For \r\n
 * details, see the GNU AGPL at: http://www.gnu.org/licenses/agpl-3.0.html\r\n
 *\r\n
 * You can contact Ascensio System SIA at Lubanas st. 125a-25, Riga, Latvia,\r\n
 * EU, LV-1021.\r\n
 *\r\n
 * The  interactive user interfaces in modified source and object code versions\r\n
 * of the Program must display Appropriate Legal Notices, as required under \r\n
 * Section 5 of the GNU AGPL version 3.\r\n
 *\r\n
 * Pursuant to Section 7(b) of the License you must retain the original Product\r\n
 * logo when distributing the program. Pursuant to Section 7(e) we decline to\r\n
 * grant you any rights under trademark law for use of our trademarks.\r\n
 *\r\n
 * All the Product\'s GUI elements, including illustrations and icon sets, as\r\n
 * well as technical writing content are licensed under the terms of the\r\n
 * Creative Commons Attribution-ShareAlike 4.0 International. See the License\r\n
 * terms at http://creativecommons.org/licenses/by-sa/4.0/legalcode\r\n
 *\r\n
 */\r\n
 (function () {\r\n
    var resolveNamespace = function (className, root) {\r\n
        var parts = className.split("."),\r\n
        current = root || window;\r\n
        for (var a = 0, b = parts.length; a < b; a++) {\r\n
            current = current[parts[a]] || {};\r\n
        }\r\n
        return current;\r\n
    };\r\n
    var Application = function (options) {\r\n
        _.extend(this, options || {});\r\n
        this.eventbus = new EventBus({\r\n
            application: this\r\n
        });\r\n
        this.createApplicationNamespace();\r\n
        this.initialize.apply(this, arguments);\r\n
        if (this.autoCreate !== false) {\r\n
            $($.proxy(this.onReady, this));\r\n
        }\r\n
    };\r\n
    _.extend(Application.prototype, {\r\n
        nameSpace: "Application",\r\n
        models: {},\r\n
        collections: {},\r\n
        controllers: {},\r\n
        allocationMap: {\r\n
            model: "Models",\r\n
            collection: "Collections",\r\n
            controller: "Controllers",\r\n
            view: "Views"\r\n
        },\r\n
        createApplicationNamespace: function () {\r\n
            var nameSpace = window;\r\n
            if (this.nameSpace) {\r\n
                if (typeof nameSpace[this.nameSpace] == "undefined") {\r\n
                    nameSpace[this.nameSpace] = {};\r\n
                }\r\n
            }\r\n
            nameSpace[this.nameSpace] = this;\r\n
            _.each(this.allocationMap, function (name, key) {\r\n
                this[name] = this[name] || {};\r\n
            },\r\n
            this);\r\n
        },\r\n
        initialize: function () {},\r\n
        onReady: function () {\r\n
            this.start();\r\n
        },\r\n
        start: function () {\r\n
            this.initializeControllers(this.controllers || {});\r\n
            this.launchControllers();\r\n
            this.launch.call(this);\r\n
        },\r\n
        getClasseRefs: function (type, classes) {\r\n
            var hashMap = {},\r\n
            allocationMap = this.allocationMap[type],\r\n
            root = this[allocationMap];\r\n
            _.each(classes, function (cls) {\r\n
                hashMap[cls] = resolveNamespace(cls, (cls.indexOf(".") > -1) ? window : root);\r\n
            },\r\n
            this);\r\n
            return hashMap;\r\n
        },\r\n
        initializeControllers: function (controllers) {\r\n
            this.controllers = {};\r\n
            _.each(controllers, function (ctrl) {\r\n
                var root = (ctrl.indexOf(".") > -1) ? window : this[this.allocationMap.controller],\r\n
                classReference = resolveNamespace(ctrl, root),\r\n
                id = ctrl.split(".").pop();\r\n
                var controller = new classReference({\r\n
                    id: ctrl,\r\n
                    application: this\r\n
                });\r\n
                controller.views = this.getClasseRefs("view", controller.views || []);\r\n
                _.extend(this.models, this.getClasseRefs("model", controller.models || []));\r\n
                _.extend(this.collections, this.getClasseRefs("collection", controller.collections || {}));\r\n
                this.buildCollections();\r\n
                this.controllers[ctrl] = controller;\r\n
            },\r\n
            this);\r\n
        },\r\n
        launchControllers: function () {\r\n
            _.each(this.controllers, function (ctrl, id) {\r\n
                ctrl.onLaunch(this);\r\n
            },\r\n
            this);\r\n
        },\r\n
        launch: function () {},\r\n
        addListeners: function (listeners, controller) {\r\n
            this.eventbus.addListeners(listeners, controller);\r\n
        },\r\n
        getController: function (name) {\r\n
            return this.controllers[name];\r\n
        },\r\n
        getModel: function (name) {\r\n
            this._modelsCache = this._modelsCache || {};\r\n
            var model = this._modelsCache[name],\r\n
            modelClass = this.getModelConstructor(name);\r\n
            if (!model && modelClass) {\r\n
                model = this.createModel(name);\r\n
                this._modelsCache[name] = model;\r\n
            }\r\n
            return model || null;\r\n
        },\r\n
        getModelConstructor: function (name) {\r\n
            return this.models[name];\r\n
        },\r\n
        createModel: function (name, options) {\r\n
            var modelClass = this.getModelConstructor(name),\r\n
            model = null;\r\n
            if (modelClass) {\r\n
                model = new modelClass(_.extend(options || {}));\r\n
            }\r\n
            return model;\r\n
        },\r\n
        getCollection: function (name) {\r\n
            this._collectionsCache = this._collectionsCache || {};\r\n
            var collection = this._collectionsCache[name],\r\n
            collectionClass = this.getCollectionConstructor(name);\r\n
            if (!collection && collectionClass) {\r\n
                collection = this.createCollection(name);\r\n
                this._collectionsCache[name] = collection;\r\n
            }\r\n
            return collection || null;\r\n
        },\r\n
        getCollectionConstructor: function (name) {\r\n
            return this.collections[name];\r\n
        },\r\n
        createCollection: function (name) {\r\n
            var collectionClass = this.getCollectionConstructor(name),\r\n
            collection = null;\r\n
            if (collectionClass) {\r\n
                collection = new collectionClass();\r\n
            }\r\n
            return collection;\r\n
        },\r\n
        buildCollections: function () {\r\n
            _.each(this.collections, function (collection, alias) {\r\n
                this.getCollection(alias);\r\n
            },\r\n
            this);\r\n
        }\r\n
    });\r\n
    if (typeof Backbone.Application == "undefined") {\r\n
        Backbone.Application = Application;\r\n
        Backbone.Application.extend = Backbone.Model.extend;\r\n
    } else {\r\n
        throw ("Native Backbone.Application instance already defined.");\r\n
    }\r\n
    var Controller = function (options) {\r\n
        _.extend(this, options || {});\r\n
        this.initialize.apply(this, arguments);\r\n
    };\r\n
    _.extend(Controller.prototype, {\r\n
        name: null,\r\n
        views: {},\r\n
        models: {},\r\n
        collections: {},\r\n
        initialize: function (options) {},\r\n
        addListeners: function (listeners) {\r\n
            this.getApplication().addListeners(listeners, this);\r\n
        },\r\n
        onLaunch: function (application) {},\r\n
        getApplication: function () {\r\n
            return this.application;\r\n
        },\r\n
        getView: function (name) {\r\n
            return this._viewsCache[name];\r\n
        },\r\n
        getViewConstructor: function (name) {\r\n
            return this.views[name];\r\n
        },\r\n
        createView: function (name, options) {\r\n
            var view = this.getViewConstructor(name),\r\n
            viewOptions = _.extend(options || {},\r\n
            {\r\n
                alias: name\r\n
            });\r\n
            this._viewsCache = this._viewsCache || {};\r\n
            this._viewsCache[name] = new view(viewOptions);\r\n
            this._viewsCache[name].options = _.extend({},\r\n
            viewOptions);\r\n
            return this._viewsCache[name];\r\n
        },\r\n
        getModel: function (name) {\r\n
            return this.application.getModel(name);\r\n
        },\r\n
        getModelConstructor: function (name) {\r\n
            return this.application.getModelConstructor(name);\r\n
        },\r\n
        createModel: function (name, options) {\r\n
            return this.application.createModel(name);\r\n
        },\r\n
        getCollection: function (name) {\r\n
            return this.application.getCollection(name);\r\n
        },\r\n
        getCollectionConstructor: function (name) {\r\n
            return this.application.getCollectionConstructor(name);\r\n
        },\r\n
        createCollection: function (name) {\r\n
            return this.application.createCollection(name);\r\n
        },\r\n
        fireEvent: function (selector, event, args) {\r\n
            this.application.eventbus.fireEvent(selector, event, args);\r\n
        },\r\n
        bindViewEvents: function (view, events) {\r\n
            this.unbindViewEvents(view);\r\n
            events = _.isFunction(events) ? events.call(this) : events;\r\n
            for (var key in events) {\r\n
                var method = events[key];\r\n
                if (!_.isFunction(method)) {\r\n
                    method = this[events[key]];\r\n
                }\r\n
                var match = key.match(/^(\\S+)\\s*(.*)$/);\r\n
                var eventName = match[1],\r\n
                selector = match[2];\r\n
                method = _.bind(method, this);\r\n
                eventName += ".bindViewEvents" + view.cid;\r\n
                view.$el.on(eventName, selector, method);\r\n
            }\r\n
            return this;\r\n
        },\r\n
        unbindViewEvents: function (view) {\r\n
            view.$el.off(".bindViewEvents" + view.cid);\r\n
            return this;\r\n
        }\r\n
    });\r\n
    if (typeof Backbone.Controller == "undefined") {\r\n
        Backbone.Controller = Controller;\r\n
        Backbone.Controller.extend = Backbone.Model.extend;\r\n
    } else {\r\n
        throw ("Native Backbone.Controller instance already defined.");\r\n
    }\r\n
    var EventBus = function (options) {\r\n
        var me = this;\r\n
        _.extend(this, options || {});\r\n
        _.extend(Backbone.View.prototype, {\r\n
            alias: null,\r\n
            hidden: false,\r\n
            getAlias: function () {\r\n
                return this.options.alias;\r\n
            },\r\n
            fireEvent: function (event, args) {\r\n
                this.trigger.apply(this, arguments);\r\n
                me.fireEvent(this.getAlias(), event, args);\r\n
            },\r\n
            hide: function () {\r\n
                this.$el.hide();\r\n
                this.hidden = true;\r\n
            },\r\n
            show: function () {\r\n
                this.$el.show();\r\n
                this.hidden = false;\r\n
            }\r\n
        });\r\n
    };\r\n
    _.extend(EventBus.prototype, {\r\n
        pool: {},\r\n
        addListeners: function (selectors, controller) {\r\n
            this.pool[controller.id] = this.pool[controller.id] || {};\r\n
            var pool = this.pool[controller.id];\r\n
            if (_.isArray(selectors)) {\r\n
                _.each(selectors, function (selector) {\r\n
                    this.addListeners(selector, controller);\r\n
                },\r\n
                this);\r\n
            } else {\r\n
                if (_.isObject(selectors)) {\r\n
                    _.each(selectors, function (listeners, selector) {\r\n
                        _.each(listeners, function (listener, event) {\r\n
                            pool[selector] = pool[selector] || {};\r\n
                            pool[selector][event] = pool[selector][event] || [];\r\n
                            pool[selector][event].push(listener);\r\n
                        },\r\n
                        this);\r\n
                    },\r\n
                    this);\r\n
                }\r\n
            }\r\n
        },\r\n
        fireEvent: function (selector, event, args) {\r\n
            var application = this.getApplication();\r\n
            _.each(this.pool, function (eventsPoolByAlias, controllerId) {\r\n
                var events = eventsPoolByAlias[selector];\r\n
                if (events) {\r\n
                    var listeners = events[event],\r\n
                    controller = application.getController(controllerId);\r\n
                    _.each(listeners, function (fn) {\r\n
                        fn.apply(controller, args);\r\n
                    });\r\n
                }\r\n
            },\r\n
            this);\r\n
        },\r\n
        getApplication: function () {\r\n
            return this.application;\r\n
        }\r\n
    });\r\n
    if (typeof Backbone.EventBus == "undefined") {\r\n
        Backbone.EventBus = EventBus;\r\n
    } else {\r\n
        throw ("Native Backbone.Application instance already defined.");\r\n
    }\r\n
})();

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>13127</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
