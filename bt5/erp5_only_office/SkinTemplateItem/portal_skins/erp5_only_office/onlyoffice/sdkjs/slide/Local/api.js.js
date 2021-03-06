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
Asc['asc_docs_api'].prototype._OfflineAppDocumentStartLoad = function()
{
	this.asc_registerCallback('asc_onDocumentContentReady', function(){
		DesktopOfflineUpdateLocalName(editor);

		//setTimeout(function(){window["UpdateInstallPlugins"]();}, 10);
	});

	AscCommon.History.UserSaveMode = true;
	return this.jio_open();
};
Asc['asc_docs_api'].prototype._OfflineAppDocumentEndLoad = function(_url, _binary)
{
	//AscCommon.g_oIdCounter.m_sUserId = window["AscDesktopEditor"]["CheckUserId"]();
	if (_binary == "")
	{
		this.sendEvent("asc_onError", c_oAscError.ID.ConvertationOpenError, c_oAscError.Level.Critical);
		return;
	}

    this.OpenDocument2(_url, _binary);
	this.WordControl.m_oLogicDocument.Set_FastCollaborativeEditing(false);
	this.DocumentOrientation = (null == this.WordControl.m_oLogicDocument) ? true : !this.WordControl.m_oLogicDocument.Orientation;
	DesktopOfflineUpdateLocalName(this);
};
window["DesktopOfflineAppDocumentEndLoad"] = function(_url, _data)
{
	AscCommon.g_oDocumentUrls.documentUrl = _url;
	if (AscCommon.g_oDocumentUrls.documentUrl.indexOf("file:") != 0)
	{
		if (AscCommon.g_oDocumentUrls.documentUrl.indexOf("/") != 0)
			AscCommon.g_oDocumentUrls.documentUrl = "/" + AscCommon.g_oDocumentUrls.documentUrl;
		AscCommon.g_oDocumentUrls.documentUrl = "file://" + AscCommon.g_oDocumentUrls.documentUrl;
	}

	editor._OfflineAppDocumentEndLoad(_url, _data);
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
	if (true === this.Is_UserSaveMode() && true !== IsNotUserSave)
	{
		if (-1 === this.Index && null === this.UserSavedIndex && false === this.ForceSave)
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

		if (this.Index != this.UserSavedIndex || true === this.ForceSave)
			return true;

		return false;
	}
	else
	{
		if (-1 === this.Index && null === this.SavedIndex && false === this.ForceSave)
			return false;

		if (this.Index != this.SavedIndex || true === this.ForceSave)
			return true;

		return false;
	}
};

window["DesktopOfflineAppDocumentApplyChanges"] = function(_changes)
{
	editor._coAuthoringSetChanges(_changes, new CDocumentColor( 191, 255, 199 ));
	//editor["asc_nativeApplyChanges"](_changes);
	//editor["asc_nativeCalculateFile"]();
};

/////////////////////////////////////////////////////////
////////////////        SAVE       //////////////////////
/////////////////////////////////////////////////////////
Asc['asc_docs_api'].prototype.SetDocumentModified = function(bValue)
{
	this.isDocumentModify = bValue;
	this.sendEvent("asc_onDocumentModifiedChanged");

	if (undefined !== window["AscDesktopEditor"])
	{
		window["AscDesktopEditor"]["onDocumentModifiedChanged"](AscCommon.History ? AscCommon.History.Have_Changes(undefined, true) : bValue);
	}
};

window["DesktopOfflineAppDocumentStartSave"] = function(isSaveAs)
{
	editor.sync_StartAction(Asc.c_oAscAsyncActionType.BlockInteraction, Asc.c_oAscAsyncAction.Save);

	var _param = "";
	if (isSaveAs === true)
		_param += "saveas=true;";
	if (AscCommon.AscBrowser.isRetina)
		_param += "retina=true;";

	window["AscDesktopEditor"]["LocalFileSave"](_param);
};
window["DesktopOfflineAppDocumentEndSave"] = function(error)
{
	editor.sync_EndAction(Asc.c_oAscAsyncActionType.BlockInteraction, Asc.c_oAscAsyncAction.Save);
	if (0 == error)
		DesktopOfflineUpdateLocalName(editor);
	else
		AscCommon.History.UserSavedIndex = editor.LastUserSavedIndex;

	editor.UpdateInterfaceState();
	editor.LastUserSavedIndex = undefined;

	if (2 == error)
		editor.sendEvent("asc_onError", c_oAscError.ID.ConvertationSaveError, c_oAscError.Level.Critical);
};
Asc['asc_docs_api'].prototype.asc_DownloadAs = function(typeFile, bIsDownloadEvent)
{
	this.asc_Save(false, true);
};

Asc['asc_docs_api'].prototype.asc_isOffline = function()
{
	return true;
};
Asc['asc_docs_api'].prototype.SetThemesPath = function(path)
{
	this.ThemeLoader.ThemesUrl = path;
	this.ThemeLoader.ThemesUrlAbs = path;
};

Asc['asc_docs_api'].prototype["asc_addImage"] = Asc['asc_docs_api'].prototype.asc_addImage;
Asc['asc_docs_api'].prototype["AddImageUrl"] = Asc['asc_docs_api'].prototype.AddImageUrl;
Asc['asc_docs_api'].prototype["AddImage"] = Asc['asc_docs_api'].prototype.AddImage;
Asc['asc_docs_api'].prototype["asc_Save"] = Asc['asc_docs_api'].prototype.asc_Save;
Asc['asc_docs_api'].prototype["asc_DownloadAs"] = Asc['asc_docs_api'].prototype.asc_DownloadAs;
Asc['asc_docs_api'].prototype["asc_isOffline"] = Asc['asc_docs_api'].prototype.asc_isOffline;
Asc['asc_docs_api'].prototype["SetDocumentModified"] = Asc['asc_docs_api'].prototype.SetDocumentModified;
Asc['asc_docs_api'].prototype["SetThemesPath"] = Asc['asc_docs_api'].prototype.SetThemesPath;

window["DesktopOfflineAppDocumentAddImageEnd"] = function(url)
{
	if (url == "")
		return;
	var _url = window["AscDesktopEditor"]["LocalFileGetImageUrl"](url);
	editor.AddImageUrlAction(AscCommon.g_oDocumentUrls.getImageUrl(_url));
};

window["on_editor_native_message"] = function(sCommand, sParam)
{
	if (!window.editor)
		return;

	if (sCommand == "save")
		editor.asc_Save();
	else if (sCommand == "saveAs")
		editor.asc_Save(false, true);
	else if (sCommand == "print")
		editor.asc_Print();
	else if (sCommand == "editor:stopDemonstration")
		editor.EndDemonstration(true);
};


AscCommon.baseEditorsApi.prototype.getEmpty = function() {
	return "PPTY;v1;20344;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";
};