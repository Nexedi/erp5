/*
 * (c) Copyright Ascensio System SIA 2010-2017
 *
 * This program is a free software product. You can redistribute it and/or
 * modify it under the terms of the GNU Affero General Public License (AGPL)
 * version 3 as published by the Free Software Foundation. In accordance with
 * Section 7(a) of the GNU AGPL its Section 15 shall be amended to the effect
 * that Ascensio System SIA expressly excludes the warranty of non-infringement
 * of any third-party rights.
 *
 * This program is distributed WITHOUT ANY WARRANTY; without even the implied
 * warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR  PURPOSE. For
 * details, see the GNU AGPL at: http://www.gnu.org/licenses/agpl-3.0.html
 *
 * You can contact Ascensio System SIA at Lubanas st. 125a-25, Riga, Latvia,
 * EU, LV-1021.
 *
 * The  interactive user interfaces in modified source and object code versions
 * of the Program must display Appropriate Legal Notices, as required under
 * Section 5 of the GNU AGPL version 3.
 *
 * Pursuant to Section 7(b) of the License you must retain the original Product
 * logo when distributing the program. Pursuant to Section 7(e) we decline to
 * grant you any rights under trademark law for use of our trademarks.
 *
 * All the Product's GUI elements, including illustrations and icon sets, as
 * well as technical writing content are licensed under the terms of the
 * Creative Commons Attribution-ShareAlike 4.0 International. See the License
 * terms at http://creativecommons.org/licenses/by-sa/4.0/legalcode
 *
 */

(function(window, undefined)
{

	function CPluginData()
	{
		this.privateData = {};
	}

	CPluginData.prototype =
	{
		setAttribute : function(name, value)
		{
			this.privateData[name] = value;
		},

		getAttribute : function(name)
		{
			return this.privateData[name];
		},

		serialize : function()
		{
			var _data = "";
			try
			{
				_data = JSON.stringify(this.privateData);
			}
			catch (err)
			{
				_data = "{ \"data\" : \"\" }";
			}
			return _data;
		},

		deserialize : function(_data)
		{
			try
			{
				this.privateData = JSON.parse(_data);
			}
			catch (err)
			{
				this.privateData = {"data" : ""};
			}
		}
	};

	function CPluginsManager(api)
	{
		this.plugins          = [];
		this.current          = null;
		this.currentInit      = false;
		this.currentVariation = 0;
		this.path             = "../../../../sdkjs-plugins/";
		this.api              = null;

		this.startData       = null;
		this.runAndCloseData = null;

		this.closeAttackTimer = -1; // защита от плагитнов, которые не закрываются

		this.methodReturnAsync = false;
	}

	CPluginsManager.prototype =
	{
		register  : function(basePath, plugins)
		{
			this.path = basePath;
			for (var i = 0; i < plugins.length; i++)
				this.plugins.push(plugins[i]);
		},
		run       : function(guid, variation, data)
		{
			if (null != this.current)
			{
				if (this.current.guid != guid)
				{
					this.runAndCloseData           = {};
					this.runAndCloseData.guid      = guid;
					this.runAndCloseData.variation = variation;
					this.runAndCloseData.data      = data;
				}
				// закрываем
				this.buttonClick(-1);
				return false;
			}

			for (var i = 0; i < this.plugins.length; i++)
			{
				if (this.plugins[i].guid == guid)
				{
					this.current = this.plugins[i];
					break;
				}
			}

			if (this.current == null)
				return false;

			this.currentVariation = Math.min(variation, this.current.variations.length - 1);

			this.startData = (data == null || data == "") ? new CPluginData() : data;
			this.startData.setAttribute("guid", guid)
			this.correctData(this.startData);
			this.show();
		},
		runResize : function(data)
		{
			var guid = data.getAttribute("guid");
			for (var i = 0; i < this.plugins.length; i++)
			{
				if (this.plugins[i].guid == guid)
				{
					if (this.plugins[i].variations[0].isUpdateOleOnResize !== true)
						return;
				}
			}

			data.setAttribute("resize", true);
			return this.run(guid, 0, data);
		},
		close     : function()
		{
			if (this.startData && this.startData.getAttribute("resize") === true)
				this.endLongAction();
			this.startData = null;

			if (true)
			{
				this.api.sendEvent("asc_onPluginClose", this.current, this.currentVariation);
				var _div = document.getElementById("plugin_iframe");
				if (_div)
					_div.parentNode.removeChild(_div);
			}
			this.current = null;

			if (this.runAndCloseData)
			{
				this.run(this.runAndCloseData.guid, this.runAndCloseData.variation, this.runAndCloseData.data);
				this.runAndCloseData = null;
			}
		},

		show : function()
		{
			if (this.startData.getAttribute("resize") === true)
				this.startLongAction();

		    if (this.api.WordControl && this.api.WordControl.m_oTimerScrollSelect != -1)
		    {
		        clearInterval(this.api.WordControl.m_oTimerScrollSelect);
                this.api.WordControl.m_oTimerScrollSelect = -1;
		    }

			if (this.current.variations[this.currentVariation].isVisual && this.startData.getAttribute("resize") !== true)
			{
				this.api.sendEvent("asc_onPluginShow", this.current, this.currentVariation);
			}
			else
			{
				var ifr            = document.createElement("iframe");
				ifr.name           = "plugin_iframe";
				ifr.id             = "plugin_iframe";
				var _add           = this.current.baseUrl == "" ? this.path : this.current.baseUrl;
				ifr.src            = _add + this.current.variations[this.currentVariation].url;
				ifr.style.position = 'absolute';
				ifr.style.top      = '-100px';
				ifr.style.left     = '0px';
				ifr.style.width    = '10000px';
				ifr.style.height   = '100px';
				ifr.style.overflow = 'hidden';
				ifr.style.zIndex   = -1000;
				document.body.appendChild(ifr);

				if (this.startData.getAttribute("resize") !== true)
					this.api.sendEvent("asc_onPluginShow", this.current, this.currentVariation);
			}

			this.currentInit = false;
		},

		buttonClick : function(id)
		{
			if (this.closeAttackTimer != -1)
			{
				clearTimeout(this.closeAttackTimer);
				this.closeAttackTimer = -1;
			}

			if (-1 == id)
			{
				if (!this.currentInit)
				{
					window.g_asc_plugins.close();
					this.close();
				}

				// защита от плохого плагина
				this.closeAttackTimer = setTimeout(function()
				{
					window.g_asc_plugins.close();
				}, 5000);
			}
			var _iframe = document.getElementById("plugin_iframe");
			if (_iframe)
			{
				var pluginData = new CPluginData();
				pluginData.setAttribute("guid", this.current.guid);
				pluginData.setAttribute("type", "button");
				pluginData.setAttribute("button", "" + id);
				_iframe.contentWindow.postMessage(pluginData.serialize(), "*");
			}
		},

		init                 : function()
		{
			switch (this.current.variations[this.currentVariation].initDataType)
			{
				case Asc.EPluginDataType.text:
				{
					var text_data = {
						data     : "",
						pushData : function(format, value)
						{
							this.data = value;
						}
					};

					this.api.asc_CheckCopy(text_data, 1);
					if (text_data.data == null)
					    text_data.data = "";
					this.startData.setAttribute("data", text_data.data);
					break;
				}
				case Asc.EPluginDataType.html:
				{
					var text_data = {
						data     : "",
						pushData : function(format, value)
						{
							this.data = value;
						}
					};

					this.api.asc_CheckCopy(text_data, 2);
					if (text_data.data == null)
                        text_data.data = "";
					this.startData.setAttribute("data", text_data.data);
					break;
				}
				case Asc.EPluginDataType.ole:
				{
					// теперь выше задается
					break;
				}
			}

			var _iframe = document.getElementById("plugin_iframe");
			if (_iframe)
			{
				this.startData.setAttribute("type", "init");
				_iframe.contentWindow.postMessage(this.startData.serialize(), "*");
			}

			this.currentInit = true;
		},
		correctData          : function(pluginData)
		{
			pluginData.setAttribute("editorType", this.api._editorNameById());

			var _mmToPx = AscCommon.g_dKoef_mm_to_pix;
			if (this.api.WordControl && this.api.WordControl.m_nZoomValue)
				_mmToPx *= this.api.WordControl.m_nZoomValue / 100;

			pluginData.setAttribute("mmToPx", _mmToPx);

			if (undefined == pluginData.getAttribute("data"))
				pluginData.setAttribute("data", "");
		},
		loadExtensionPlugins : function(_plugins)
		{
			if (!_plugins || _plugins.length < 1)
				return;

			var _map = {};
			for (var i = 0; i < this.plugins.length; i++)
				_map[this.plugins[i].guid] = true;

			for (var i = 0; i < _plugins.length; i++)
			{
				var _p = new Asc.CPlugin();
				_p["deserialize"](_plugins[i]);

				if (_map[_p.guid] === true)
					continue;

				this.plugins.push(_p);
			}

			var _pluginsInstall = {"url" : this.path, "pluginsData" : []};
			for (var i = 0; i < this.plugins.length; i++)
			{
				_pluginsInstall["pluginsData"].push(this.plugins[i].serialize());
			}

			this.api.sendEvent("asc_onPluginsInit", _pluginsInstall);
		},

		startLongAction : function()
		{
			//console.log("startLongAction");
			this.api.sync_StartAction(Asc.c_oAscAsyncActionType.BlockInteraction, Asc.c_oAscAsyncAction.SlowOperation);
		},
		endLongAction   : function()
		{
			//console.log("endLongAction");
			this.api.sync_EndAction(Asc.c_oAscAsyncActionType.BlockInteraction, Asc.c_oAscAsyncAction.SlowOperation);
		},

		sendMessage : function(pluginData)
		{
			if (!this.current)
				return;

			var _iframe = document.getElementById("plugin_iframe");
			if (_iframe)
			{
				pluginData.setAttribute("guid", this.current.guid);
				_iframe.contentWindow.postMessage(pluginData.serialize(), "*");
			}
		},

		onChangedSelectionData : function()
		{
			if (this.current && this.current.variations[this.currentVariation].initOnSelectionChanged === true)
			{
				// re-init
				this.init();
			}
		},

		onExternalMouseUp : function()
		{
		    if (!this.current)
		        return;

		    this.startData.setAttribute("type", "onExternalMouseUp");
		    this.correctData(this.startData);
		    this.sendMessage(this.startData);
		},

		onPluginMethodReturn : function(_return)
		{
			if (!this.current)
				return;

			var pluginData = new CPluginData();
			pluginData.setAttribute("guid", this.current.guid);
			pluginData.setAttribute("type", "onMethodReturn");
			pluginData.setAttribute("methodReturnData", _return);
			var _iframe = document.getElementById("plugin_iframe");
			if (_iframe)
				_iframe.contentWindow.postMessage(pluginData.serialize(), "*");
		},

		setPluginMethodReturnAsync : function()
		{
			this.methodReturnAsync = true;
		}
	};

	// export
	CPluginsManager.prototype["buttonClick"] = CPluginsManager.prototype.buttonClick;

	function onMessage(event)
	{
		if (!window.g_asc_plugins || !window.g_asc_plugins.current)
			return;

		if (typeof(event.data) == "string")
		{
			var pluginData = new CPluginData();
			pluginData.deserialize(event.data);

			var guid = pluginData.getAttribute("guid");

			if (guid != window.g_asc_plugins.current.guid)
				return;

			var name  = pluginData.getAttribute("type");
			var value = pluginData.getAttribute("data");

            if ("initialize_internal" == name)
            {
                window.g_asc_plugins.init();
            }
			else if ("initialize" == name)
			{
				var pluginData = new CPluginData();
                pluginData.setAttribute("guid", guid);
                pluginData.setAttribute("type", "plugin_init");
                pluginData.setAttribute("data", "!function(n,e){var i=!1;n.plugin_sendMessage=function(e){n.parent.postMessage(e,\"*\")},n.plugin_onMessage=function(t){if(n.Asc.plugin&&\"string\"==typeof t.data){var s={};try{s=JSON.parse(t.data)}catch(n){s={}}if(s.guid!=n.Asc.plugin.guid)return;var a=s.type;switch(\"init\"==a&&(n.Asc.plugin.info=s),a){case\"init\":n.Asc.plugin.executeCommand=function(e,i){n.Asc.plugin.info.type=e,n.Asc.plugin.info.data=i;var t=\"\";try{t=JSON.stringify(n.Asc.plugin.info)}catch(n){t=JSON.stringify({type:i})}n.plugin_sendMessage(t)},n.Asc.plugin.executeMethod=function(e,i){if(!0===n.Asc.plugin.isWaitMethod)return!1;n.Asc.plugin.isWaitMethod=!0,n.Asc.plugin.info.type=\"method\",n.Asc.plugin.info.methodName=e,n.Asc.plugin.info.data=i;var t=\"\";try{t=JSON.stringify(n.Asc.plugin.info)}catch(n){t=JSON.stringify({type:data})}return n.plugin_sendMessage(t),!0},n.Asc.plugin.resizeWindow=function(i,t,s,a,u,c){e==s&&(s=0),e==a&&(a=0),e==u&&(u=0),e==c&&(c=0);var g=JSON.stringify({width:i,height:t,minw:s,minh:a,maxw:u,maxh:c});n.Asc.plugin.info.type=\"resize\",n.Asc.plugin.info.data=g;var o=\"\";try{o=JSON.stringify(n.Asc.plugin.info)}catch(n){o=JSON.stringify({type:g})}n.plugin_sendMessage(o)},n.Asc.plugin.init(n.Asc.plugin.info.data);break;case\"button\":var u=parseInt(s.button);n.Asc.plugin.button||-1!=u?n.Asc.plugin.button(u):n.Asc.plugin.executeCommand(\"close\",\"\");break;case\"enableMouseEvent\":i=s.isEnabled,n.Asc.plugin.onEnableMouseEvent&&n.Asc.plugin.onEnableMouseEvent(i);break;case\"onExternalMouseUp\":n.Asc.plugin.onExternalMouseUp&&n.Asc.plugin.onExternalMouseUp();break;case\"onMethodReturn\":n.Asc.plugin.isWaitMethod=!1,n.Asc.plugin.onMethodReturn&&n.Asc.plugin.onMethodReturn(s.methodReturnData);break;case\"onCommandCallback\":n.Asc.plugin.onCommandCallback&&n.Asc.plugin.onCommandCallback();break;case\"onExternalPluginMessage\":n.Asc.plugin.onExternalPluginMessage&&s.data&&s.data.type&&n.Asc.plugin.onExternalPluginMessage(s.data)}}},n.onmousemove=function(t){if(i&&n.Asc.plugin&&n.Asc.plugin.executeCommand){var s=e===t.clientX?t.pageX:t.clientX,a=e===t.clientY?t.pageY:t.clientY;n.Asc.plugin.executeCommand(\"onmousemove\",JSON.stringify({x:s,y:a}))}},n.onmouseup=function(t){if(i&&n.Asc.plugin&&n.Asc.plugin.executeCommand){var s=e===t.clientX?t.pageX:t.clientX,a=e===t.clientY?t.pageY:t.clientY;n.Asc.plugin.executeCommand(\"onmouseup\",JSON.stringify({x:s,y:a}))}},n.plugin_sendMessage(JSON.stringify({guid:n.Asc.plugin.guid,type:\"initialize_internal\"}))}(window,void 0);");
                var _iframe = document.getElementById("plugin_iframe");
                if (_iframe)
                    _iframe.contentWindow.postMessage(pluginData.serialize(), "*");
				return;
			}
			else if ("close" == name || "command" == name)
			{
				if (window.g_asc_plugins.closeAttackTimer != -1)
				{
					clearTimeout(window.g_asc_plugins.closeAttackTimer);
					window.g_asc_plugins.closeAttackTimer = -1;
				}

				if (value && value != "")
				{
					var _command_callback_send = ("command" == name);
					try
					{
						if (pluginData.getAttribute("interface"))
						{
							var _script = "(function(){ var Api = window.g_asc_plugins.api;\n" + value + "\n})();";
							eval(_script);
						}
						else if (pluginData.getAttribute("resize") || window.g_asc_plugins.api.asc_canPaste())
						{
							var oLogicDocument, i;
							var editorId = window.g_asc_plugins.api.getEditorId();
							if (AscCommon.c_oEditorId.Word === editorId ||
								AscCommon.c_oEditorId.Presentation === editorId)
							{
								oLogicDocument = window.g_asc_plugins.api.WordControl ?
									window.g_asc_plugins.api.WordControl.m_oLogicDocument : null;
								if(AscCommon.c_oEditorId.Word === editorId){
									oLogicDocument.LockPanelStyles();
								}
							}
							
							var _script = "(function(){ var Api = window.g_asc_plugins.api;\n" + value + "\n})();";
							eval(_script);

							if (pluginData.getAttribute("recalculate") == true)
							{
								_command_callback_send = false;
								if (AscCommon.c_oEditorId.Word === editorId ||
									AscCommon.c_oEditorId.Presentation === editorId)
								{
									oLogicDocument = window.g_asc_plugins.api.WordControl ?
										window.g_asc_plugins.api.WordControl.m_oLogicDocument : null;
									var _fonts         = oLogicDocument.Document_Get_AllFontNames();
									var _imagesArray   = oLogicDocument.Get_AllImageUrls();
									var _images        = {};
									for (i = 0; i < _imagesArray.length; i++)
									{
										_images[_imagesArray[i]] = _imagesArray[i];
									}

									window.g_asc_plugins.images_rename = _images;
									AscCommon.Check_LoadingDataBeforePrepaste(window.g_asc_plugins.api, _fonts, _images,
										function()
										{
											if (window.g_asc_plugins.api.WordControl &&
												window.g_asc_plugins.api.WordControl.m_oLogicDocument &&
												window.g_asc_plugins.api.WordControl.m_oLogicDocument.Reassign_ImageUrls)
											{
												window.g_asc_plugins.api.WordControl.m_oLogicDocument.Reassign_ImageUrls(
													window.g_asc_plugins.images_rename);
											}
											delete window.g_asc_plugins.images_rename;

											if(AscCommon.c_oEditorId.Word === editorId) {
												oLogicDocument.UnlockPanelStyles(true);
												oLogicDocument.OnEndLoadScript();
											}

											window.g_asc_plugins.api.asc_Recalculate();

											var pluginData = new CPluginData();
											pluginData.setAttribute("guid", guid);
											pluginData.setAttribute("type", "onCommandCallback");
											var _iframe = document.getElementById("plugin_iframe");
											if (_iframe)
												_iframe.contentWindow.postMessage(pluginData.serialize(), "*");
										});
								}
								else if (AscCommon.c_oEditorId.Spreadsheet === editorId)
								{
									var oApi    = window.g_asc_plugins.api;
									var oFonts  = oApi.wbModel._generateFontMap();
									var aImages = oApi.wbModel.getAllImageUrls();
									var oImages = {};
									for (i = 0; i < aImages.length; i++)
									{
										oImages[aImages[i]] = aImages[i];
									}
									window.g_asc_plugins.images_rename = oImages;
									AscCommon.Check_LoadingDataBeforePrepaste(window.g_asc_plugins.api, oFonts, oImages,
										function(){
											oApi.wbModel.reassignImageUrls(window.g_asc_plugins.images_rename);
											delete window.g_asc_plugins.images_rename;
											window.g_asc_plugins.api.asc_Recalculate();

											var pluginData = new CPluginData();
											pluginData.setAttribute("guid", guid);
											pluginData.setAttribute("type", "onCommandCallback");
											var _iframe = document.getElementById("plugin_iframe");
											if (_iframe)
												_iframe.contentWindow.postMessage(pluginData.serialize(), "*");
										});
								}
							} else {
								if (AscCommon.c_oEditorId.Spreadsheet === editorId) {
									// На asc_canPaste создается точка в истории и startTransaction. Поэтому нужно ее закрыть без пересчета.
									window.g_asc_plugins.api.asc_endPaste();
								}
							}
						}
					} catch (err)
					{
					}

					if (_command_callback_send)
					{
						var pluginData = new CPluginData();
						pluginData.setAttribute("guid", guid);
						pluginData.setAttribute("type", "onCommandCallback");
						var _iframe = document.getElementById("plugin_iframe");
						if (_iframe)
							_iframe.contentWindow.postMessage(pluginData.serialize(), "*");
					}
				}

				if ("close" == name)
				{
					window.g_asc_plugins.close();
				}
			}
			else if ("resize" == name)
			{
				var _sizes = JSON.parse(value);

				window.g_asc_plugins.api.sendEvent("asc_onPluginResize",
					[_sizes["width"], _sizes["height"]],
					[_sizes["minw"], _sizes["minh"]],
					[_sizes["maxw"], _sizes["maxh"]], function() {
					// TODO: send resize end event
				});
			}
			else if ("onmousemove" == name)
			{
				var _pos = JSON.parse(value);
				window.g_asc_plugins.api.sendEvent("asc_onPluginMouseMove", _pos["x"], _pos["y"]);
			}
			else if ("onmouseup" == name)
			{
				var _pos = JSON.parse(value);
				window.g_asc_plugins.api.sendEvent("asc_onPluginMouseUp", _pos["x"], _pos["y"]);
			}
			else if ("method" == name)
			{
				var _apiMethodName = "pluginMethod_" + pluginData.getAttribute("methodName");
				var _return = undefined;
				if (window.g_asc_plugins.api[_apiMethodName])
					_return = window.g_asc_plugins.api[_apiMethodName].apply(window.g_asc_plugins.api, value);

				if (!window.g_asc_plugins.methodReturnAsync)
				{
					var pluginData = new CPluginData();
					pluginData.setAttribute("guid", guid);
					pluginData.setAttribute("type", "onMethodReturn");
					pluginData.setAttribute("methodReturnData", _return);
					var _iframe = document.getElementById("plugin_iframe");
					if (_iframe)
						_iframe.contentWindow.postMessage(pluginData.serialize(), "*");
				}
				window.g_asc_plugins.methodReturnAsync = false;
				return;
			}
		}
	}

	if (window.addEventListener)
	{
		window.addEventListener("message", onMessage, false);
	}
	else if (window.attachEvent)
	{
		window.attachEvent("onmessage", onMessage);
	}

	window["Asc"]                      = window["Asc"] ? window["Asc"] : {};
	window["Asc"].createPluginsManager = function(api)
	{
		if (window.g_asc_plugins)
			return window.g_asc_plugins;

		window.g_asc_plugins        = new CPluginsManager(api);
		window["g_asc_plugins"]     = window.g_asc_plugins;
		window.g_asc_plugins.api    = api;
		window.g_asc_plugins["api"] = window.g_asc_plugins.api;

		api.asc_registerCallback('asc_onSelectionEnd', function(){
			window.g_asc_plugins.onChangedSelectionData();
		});

		window.g_asc_plugins.api.asc_registerCallback('asc_onDocumentContentReady', function()
		{

			setTimeout(function()
			{
				window.g_asc_plugins.loadExtensionPlugins(window["Asc"]["extensionPlugins"]);
			}, 10);

		});

		return window.g_asc_plugins;
	};

	window["Asc"].CPluginData      = CPluginData;
	window["Asc"].CPluginData_wrap = function(obj)
	{
		if (!obj.getAttribute)
			obj.getAttribute = function(name)
			{
				return this[name];
			};
		if (!obj.setAttribute)
			obj.setAttribute = function(name, value)
			{
				return this[name] = value;
			};
	};
})(window, undefined);