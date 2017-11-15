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

"use strict";

// Import
var c_oAscError = Asc.c_oAscError;

/////////////////////////////////////////////////////////
//////////////        OPEN       ////////////////////////
/////////////////////////////////////////////////////////

(/**
 * @param {jQuery} $
 * @param {Window} window
 * @param {undefined} undefined
 */
	function($, window, undefined) {

	var asc = window["Asc"];
	var prot;

	asc['spreadsheet_api'].prototype._OfflineAppDocumentStartLoad = function()
	{
		this.asc_registerCallback('asc_onDocumentContentReady', function(){
			DesktopOfflineUpdateLocalName(window["Asc"]["editor"]);

			setTimeout(function(){window["UpdateInstallPlugins"]();}, 10);
		});
	
		window["AscDesktopEditor"]["LocalStartOpen"]();
	};
	
	asc['spreadsheet_api'].prototype._OfflineAppDocumentEndLoad = function(_data, _len)
	{
		AscCommon.g_oIdCounter.m_sUserId = window["AscDesktopEditor"]["CheckUserId"]();
		if (_data == "")
		{
			this.sendEvent("asc_onError", c_oAscError.ID.ConvertationOpenError, c_oAscError.Level.Critical);
			return;
		}

		var _binary = getBinaryArray(_data, _len);
		this.openDocument(_binary);
		AscCommon.History.UserSaveMode = true;
		
		DesktopOfflineUpdateLocalName(this);

		window["DesktopAfterOpen"](this);
		
		this.onUpdateDocumentModified(AscCommon.History.Have_Changes());
	};
	
	asc['spreadsheet_api'].prototype._onNeedParams = function(data, opt_isPassword)
	{
		var options;
		if(opt_isPassword){
			options = new AscCommon.asc_CAdvancedOptions(Asc.c_oAscAdvancedOptionsID.DRM);
		} else {
			var cp = JSON.parse("{\"codepage\":46,\"delimiter\":1}");
			cp['encodings'] = AscCommon.getEncodingParams();
			options = new AscCommon.asc_CAdvancedOptions(Asc.c_oAscAdvancedOptionsID.CSV, cp);
		}
		this.handlers.trigger("asc_onAdvancedOptions", options, AscCommon.c_oAscAdvancedOptionsAction.Open);
	};
	
	asc['spreadsheet_api'].prototype.asc_addImageDrawingObject = function(url)
	{
		var _url = window["AscDesktopEditor"]["LocalFileGetImageUrl"](url);
		
		var ws = this.wb.getWorksheet();
		if (ws) 
		{
			var _url = window["AscDesktopEditor"]["LocalFileGetImageUrl"](url);
			ws.objectRender.addImageDrawingObject(AscCommon.g_oDocumentUrls.getImageUrl(_url) , null);
		}
	};
	asc['spreadsheet_api'].prototype.asc_showImageFileDialog = function()
	{
		window["AscDesktopEditor"]["LocalFileGetImageUrlFromOpenFileDialog"]();
	};
	asc['spreadsheet_api'].prototype.asc_addImage = function()
	{
	  window["AscDesktopEditor"]["LocalFileGetImageUrlFromOpenFileDialog"]();
	};
})(jQuery, window);

window["Asc"]['spreadsheet_api'].prototype.asc_setAdvancedOptions = function(idOption, option) 
{
	if (window["Asc"].c_oAscAdvancedOptionsID.CSV === idOption) {
		var delimiter = option.asc_getDelimiter();
		var delimiterChar = option.asc_getDelimiterChar();
        var _param = "";
	    _param += ("<m_nCsvTxtEncoding>" + option.asc_getCodePage() + "</m_nCsvTxtEncoding>");
		if (null != delimiter) {
			_param += ("<m_nCsvDelimiter>" + delimiter + "</m_nCsvDelimiter>");
		}
		if (null != delimiterChar) {
			_param += ("<m_nCsvDelimiterChar>" + delimiterChar + "</m_nCsvDelimiterChar>");
		}

		window["AscDesktopEditor"]["SetAdvancedOptions"](_param);
	}
	else if (window["Asc"].c_oAscAdvancedOptionsID.DRM === idOption) {
        var _param = "";
        _param += ("<m_sPassword>" + AscCommon.CopyPasteCorrectString(option.asc_getPassword()) + "</m_sPassword>");
        window["AscDesktopEditor"]["SetAdvancedOptions"](_param);
    }
};
window["Asc"]['spreadsheet_api'].prototype["asc_setAdvancedOptions"] = window["Asc"]['spreadsheet_api'].prototype.asc_setAdvancedOptions;

window["DesktopOfflineAppDocumentEndLoad"] = function(_url, _data, _len)
{
	AscCommon.g_oDocumentUrls.documentUrl = _url;
	if (AscCommon.g_oDocumentUrls.documentUrl.indexOf("file:") != 0)
	{
		if (AscCommon.g_oDocumentUrls.documentUrl.indexOf("/") != 0)
			AscCommon.g_oDocumentUrls.documentUrl = "/" + AscCommon.g_oDocumentUrls.documentUrl;
		AscCommon.g_oDocumentUrls.documentUrl = "file://" + AscCommon.g_oDocumentUrls.documentUrl;
	}
	
    window["Asc"]["editor"]._OfflineAppDocumentEndLoad(_data, _len);
};

/////////////////////////////////////////////////////////
//////////////        CHANGES       /////////////////////
/////////////////////////////////////////////////////////
AscCommon.CHistory.prototype.Reset_SavedIndex = function(IsUserSave)
{
	this.SavedIndex = (null === this.SavedIndex && -1 === this.Index ? null : this.Index);
	if (true === this.Is_UserSaveMode())
	{
		if (true === IsUserSave)
		{
			this.UserSavedIndex = this.Index;
			this.ForceSave      = false;
		}
	}
	else
	{
		this.ForceSave  = false;
	}
};

AscCommon.CHistory.prototype.Have_Changes = function(IsNotUserSave, IsNoSavedNoModifyed) 
{
	var checkIndex = (this.Is_UserSaveMode() && !IsNotUserSave) ? this.UserSavedIndex : this.SavedIndex;
	if (-1 === this.Index && null === checkIndex && false === this.ForceSave) 
	{
		if (window["AscDesktopEditor"])
		{
			if (0 != window["AscDesktopEditor"]["LocalFileGetOpenChangesCount"]())
				return true;
			if (!window["AscDesktopEditor"]["LocalFileGetSaved"]() && IsNoSavedNoModifyed !== true)
				return true;
		}
		return false;
	}
	return (this.Index != checkIndex || true === this.ForceSave);
};
	
window["DesktopOfflineAppDocumentApplyChanges"] = function(_changes)
{
	for (var i = 0, l = _changes.length; i < l; ++i) 
	{
		window["Asc"]["editor"].CoAuthoringApi.onSaveChanges(_changes[i], null, true);
    }
};

/////////////////////////////////////////////////////////
////////////////        SAVE       //////////////////////
/////////////////////////////////////////////////////////
window["Asc"]['spreadsheet_api'].prototype.onUpdateDocumentModified = function(bIsModified) 
{
    // Обновляем только после окончания сохранения
    if (this.canSave) {
      this.handlers.trigger("asc_onDocumentModifiedChanged", bIsModified);
      this._onUpdateDocumentCanSave();

      if (undefined !== window["AscDesktopEditor"]) {
        window["AscDesktopEditor"]["onDocumentModifiedChanged"](AscCommon.History ? AscCommon.History.Have_Changes(undefined, true) : bValue);
      }
    }
};
  
window["Asc"]['spreadsheet_api'].prototype.asc_Save = function (isNoUserSave, isSaveAs)
{
	if (this.isChartEditor || AscCommon.c_oAscAdvancedOptionsAction.None !== this.advancedOptionsAction)
		return;
    	
	var t = this;
    if (true !== isNoUserSave)
        this.IsUserSave = true;
	
	if (this.IsUserSave)
	{
		this.LastUserSavedIndex = AscCommon.History.UserSavedIndex;
	}

    if (true === this.canSave && !this.isLongAction())
	{
		var _isNaturalSave = this.IsUserSave;
		this.canSave = false;
		this.CoAuthoringApi.askSaveChanges(function(e){t.onSaveCallback(e);});
		
		if (this.CoAuthoringApi.onUnSaveLock)
			this.CoAuthoringApi.onUnSaveLock();
		
		if (_isNaturalSave === true)
			window["DesktopOfflineAppDocumentStartSave"](isSaveAs);
	}
};
window["Asc"]['spreadsheet_api'].prototype.asc_DownloadAs = function(typeFile, bIsDownloadEvent) 
{
	this.asc_Save(false, true);
};

window["Asc"]['spreadsheet_api'].prototype.asc_isOffline = function()
{
	return true;
};

window["DesktopOfflineAppDocumentStartSave"] = function(isSaveAs)
{
	window["Asc"]["editor"].sync_StartAction(Asc.c_oAscAsyncActionType.BlockInteraction, Asc.c_oAscAsyncAction.Save);
	
	var _param = "";
	if (isSaveAs === true)
		_param += "saveas=true;";
	if (AscCommon.AscBrowser.isRetina)
		_param += "retina=true;";
	
	window["AscDesktopEditor"]["LocalFileSave"](_param);
};
window["DesktopOfflineAppDocumentEndSave"] = function(error)
{
	window["Asc"]["editor"].sync_EndAction(Asc.c_oAscAsyncActionType.BlockInteraction, Asc.c_oAscAsyncAction.Save);
	if (0 == error)
		DesktopOfflineUpdateLocalName(window["Asc"]["editor"]);
	else
		AscCommon.History.UserSavedIndex = window["Asc"]["editor"].LastUserSavedIndex;		
	
	window["Asc"]["editor"].onUpdateDocumentModified(AscCommon.History.Have_Changes());
	window["Asc"]["editor"].LastUserSavedIndex = undefined;
	
	if (2 == error)
		window["Asc"]["editor"].sendEvent("asc_onError", c_oAscError.ID.ConvertationSaveError, c_oAscError.Level.NoCritical);

	if (0 == error)
	{
		if (window.SaveQuestionObjectBeforeSign)
		{
			var _obj = window.SaveQuestionObjectBeforeSign;
			editor.sendEvent("asc_onSignatureClick", _obj.guid, _obj.width, _obj.height);
			window.SaveQuestionObjectBeforeSign = null;
		}
	}
};

window["Asc"]['spreadsheet_api'].prototype["asc_addImageDrawingObject"] = window["Asc"]['spreadsheet_api'].prototype.asc_addImageDrawingObject;
window["Asc"]['spreadsheet_api'].prototype["asc_showImageFileDialog"] = window["Asc"]['spreadsheet_api'].prototype.asc_showImageFileDialog;
window["Asc"]['spreadsheet_api'].prototype["asc_Save"] = window["Asc"]['spreadsheet_api'].prototype.asc_Save;
window["Asc"]['spreadsheet_api'].prototype["asc_DownloadAs"] = window["Asc"]['spreadsheet_api'].prototype.asc_DownloadAs;
window["Asc"]['spreadsheet_api'].prototype["asc_isOffline"] = window["Asc"]['spreadsheet_api'].prototype.asc_isOffline;
window["Asc"]['spreadsheet_api'].prototype["asc_addImage"] = window["Asc"]['spreadsheet_api'].prototype.asc_addImage;

window["DesktopOfflineAppDocumentAddImageEnd"] = function(url)
{
	if (url == "")
		return;
	
	var ws = window["Asc"]["editor"].wb.getWorksheet();
    if (ws) 
	{
		var _url = window["AscDesktopEditor"]["LocalFileGetImageUrl"](url);
        ws.objectRender.addImageDrawingObject(AscCommon.g_oDocumentUrls.getImageUrl(_url) , null);
    }
};

window["on_editor_native_message"] = function(sCommand, sParam)
{
	if (!window["Asc"]["editor"])
		return;
	
	if (sCommand == "save")
		window["Asc"]["editor"].asc_Save();
	else if (sCommand == "saveAs")
		window["Asc"]["editor"].asc_Save(false, true);
	else if (sCommand == "print")
		window["Asc"]["editor"].asc_Print();
};