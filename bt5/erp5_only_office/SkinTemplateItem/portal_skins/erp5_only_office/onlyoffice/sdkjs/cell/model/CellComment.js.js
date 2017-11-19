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

(
/**
* @param {Window} window
* @param {undefined} undefined
*/
function (window, undefined) {
	// Import
	var CellAddress = AscCommon.CellAddress;
	var History = AscCommon.History;
	
	var c_oAscInsertOptions = Asc.c_oAscInsertOptions;
	var c_oAscDeleteOptions = Asc.c_oAscDeleteOptions;
	
/** @constructor */
function asc_CCommentCoords(obj) {

	this.nRow = null;
	this.nCol = null;

	this.nLeft = null;
	this.nLeftOffset = null;
	this.nTop = null;
	this.nTopOffset = null;
	this.nRight = null;
	this.nRightOffset = null;
	this.nBottom = null;
	this.nBottomOffset = null;

	this.dLeftMM = null;
	this.dTopMM = null;
	this.dLeftPX = null;
	this.dReverseLeftPX = null;
	this.dTopPX = null;

	this.dWidthMM = null;
	this.dHeightMM = null;
	this.dWidthPX = null;
	this.dHeightPX = null;

	this.bMoveWithCells = false;
	this.bSizeWithCells = false;

	if (obj) {
		this.nRow = obj.nRow;
		this.nCol = obj.nCol;

		this.nLeft = obj.nLeft;
		this.nLeftOffset = obj.nLeftOffset;
		this.nTop = obj.nTop;
		this.nTopOffset = obj.nTopOffset;
		this.nRight = obj.nRight;
		this.nRightOffset = obj.nRightOffset;
		this.nBottom = obj.nBottom;
		this.nBottomOffset = obj.nBottomOffset;

		this.dLeftMM = obj.dLeftMM;
		this.dTopMM = obj.dTopMM;
		this.dLeftPX = obj.dLeftPX;
		this.dReverseLeftPX = obj.dReverseLeftPX;
		this.dTopPX = obj.dTopPX;

		this.dWidthMM = obj.dWidthMM;
		this.dHeightMM = obj.dHeightMM;
		this.dWidthPX = obj.dWidthPX;
		this.dHeightPX = obj.dHeightPX;

		this.bMoveWithCells = obj.bMoveWithCells;
		this.bSizeWithCells = obj.bSizeWithCells;
	}
}
asc_CCommentCoords.prototype = {

	asc_setRow: function(val) { this.nRow = val; },
	asc_getRow: function() { return this.nRow; },

	asc_setCol: function(val) { this.nCol = val; },
	asc_getCol: function() { return this.nCol; },

	asc_setLeft: function(val) { this.nLeft = val; },
	asc_getLeft: function() { return this.nLeft; },

	asc_setLeftOffset: function(val) { this.nLeftOffset = val; },
	asc_getLeftOffset: function() { return this.nLeftOffset; },

	asc_setTop: function(val) { this.nTop = val; },
	asc_getTop: function() { return this.nTop; },

	asc_setTopOffset: function(val) { this.nTopOffset = val; },
	asc_getTopOffset: function() { return this.nTopOffset; },

	asc_setRight: function(val) { this.nRight = val; },
	asc_getRight: function() { return this.nRight; },

	asc_setRightOffset: function(val) { this.nRightOffset = val; },
	asc_getRightOffset: function() { return this.nRightOffset; },

	asc_setBottom: function(val) { this.nBottom = val; },
	asc_getBottom: function() { return this.nBottom; },

	asc_setBottomOffset: function(val) { this.nBottomOffset = val; },
	asc_getBottomOffset: function() { return this.nBottomOffset; },

	asc_setLeftMM: function(val) { this.dLeftMM = val; },
	asc_getLeftMM: function() { return this.dLeftMM; },

	asc_setLeftPX: function(val) { this.dLeftPX = val; },
	asc_getLeftPX: function() { return this.dLeftPX; },
	
	asc_setReverseLeftPX: function(val) { this.dReverseLeftPX = val; },
	asc_getReverseLeftPX: function() { return this.dReverseLeftPX; },

	asc_setTopMM: function(val) { this.dTopMM = val; },
	asc_getTopMM: function() { return this.dTopMM; },

	asc_setTopPX: function(val) { this.dTopPX = val; },
	asc_getTopPX: function() { return this.dTopPX; },

	asc_setWidthMM: function(val) { this.dWidthMM = val; },
	asc_getWidthMM: function() { return this.dWidthMM; },

	asc_setHeightMM: function(val) { this.dHeightMM = val; },
	asc_getHeightMM: function() { return this.dHeightMM; },

	asc_setWidthPX: function(val) { this.dWidthPX = val; },
	asc_getWidthPX: function() { return this.dWidthPX; },

	asc_setHeightPX: function(val) { this.dHeightPX = val; },
	asc_getHeightPX: function() { return this.dHeightPX; },

	asc_setMoveWithCells: function(val) { this.bMoveWithCells = val; },
	asc_getMoveWithCells: function() { return this.bMoveWithCells; },

	asc_setSizeWithCells: function(val) { this.bSizeWithCells = val; },
	asc_getSizeWithCells: function() { return this.bSizeWithCells; }
};

/** @constructor */
function asc_CCommentData(obj) {
	this.Properties = {
		wsId: 0,
		nCol: 1,
		nRow: 2,
		nId: 3,
		nLevel: 5,
		sText: 6,
		sTime: 8,
		sUserId: 9,
		sUserName: 10,
		bDocument: 11,
		bSolved: 12,
		aReplies: 13,
		bHidden: 14,
		sOOTime: 15
	};

	this.bHidden = false;
	this.wsId = null;
	this.nCol = 0;
	this.nRow = 0;
	this.nId = null;
	this.oParent = null;
	this.nLevel = 0;

	// Common
	this.sText = "";
	this.sTime = "";
	this.sOOTime = "";
	this.sUserId = "";
	this.sUserName = "";
	this.bDocument = true; 	// For compatibility with 'Word Comment Control'
	this.bSolved = false;
	this.aReplies = [];

	if (obj) {
		this.bHidden = obj.bHidden;
		this.wsId = obj.wsId;
		this.nCol = obj.nCol;
		this.nRow = obj.nRow;
		this.nId = obj.nId;
		this.oParent = obj.oParent;
		this.nLevel = (null === this.oParent) ? 0 : this.oParent.asc_getLevel() + 1;

		// Common
		this.sText = obj.sText;
		this.sTime = obj.sTime;
		this.sOOTime = obj.sOOTime;
		this.sUserId = obj.sUserId;
		this.sUserName = obj.sUserName;
		this.bDocument = obj.bDocument;
		this.bSolved = obj.bSolved;
		this.aReplies = [];

		for (var i = 0; i < obj.aReplies.length; i++) {
			var item = new asc_CCommentData(obj.aReplies[i]);
			this.aReplies.push(item);
		}
	}
}
asc_CCommentData.prototype = {
	guid: function () {
		function S4() {
			return (((1 + Math.random()) * 0x10000) | 0).toString(16).substring(1);
		}
		return (S4() + S4() + "-" + S4() + "-" + S4() + "-" + S4() + "-" + S4() + S4() + S4());
	},
	setId: function () {
		if (this.bDocument)
			this.nId = "doc_" + this.guid();
		else
			this.nId = "sheet" + this.wsId + "_" + this.guid();
	},

	asc_putQuoteText: function(val) {},
	asc_getQuoteText: function() {
		return this.bDocument ? null : AscCommon.g_oCellAddressUtils.getCellId(this.nRow, this.nCol);
	},

	asc_putRow: function(val) { this.nRow = val; },
	asc_getRow: function() { return this.nRow; },

	asc_putCol: function(val) { this.nCol = val; },
	asc_getCol: function() { return this.nCol; },

	asc_putId: function(val) { this.nId = val; },
	asc_getId: function() { return this.nId; },

	asc_putLevel: function(val) { this.nLevel = val; },
	asc_getLevel: function() { return this.nLevel; },

	asc_putParent: function(obj) { this.oParent = obj; },
	asc_getParent: function() { return this.oParent; },

	asc_putText: function(val) { this.sText = val ? val.slice(0, Asc.c_oAscMaxCellOrCommentLength) : val; },
	asc_getText: function() { return this.sText; },

	asc_putTime: function(val) { this.sTime = val; },
	asc_getTime: function() { return this.sTime; },
	
	asc_putOnlyOfficeTime: function(val) { this.sOOTime = val; },
	asc_getOnlyOfficeTime: function() { return this.sOOTime; },

	asc_putUserId: function(val) { this.sUserId = val; },
	asc_getUserId: function() { return this.sUserId; },

	asc_putUserName: function(val) { this.sUserName = val; },
	asc_getUserName: function() { return this.sUserName; },

	asc_putDocumentFlag: function(val) { this.bDocument = val; },
	asc_getDocumentFlag: function() { return this.bDocument; },
	
	asc_putHiddenFlag: function(val) { this.bHidden = val; },
	asc_getHiddenFlag: function() { return this.bHidden; },

	asc_putSolved: function(val) { this.bSolved = val; },
	asc_getSolved: function() { return this.bSolved; },

	asc_getRepliesCount: function() { return this.aReplies.length; },
	asc_getReply: function(index) { return this.aReplies[index]; },

	asc_addReply: function(oReply) {

		oReply.asc_putParent(this);
		oReply.asc_putDocumentFlag(this.asc_getDocumentFlag());
		oReply.asc_putLevel((oReply.oParent == null) ? 0 : oReply.oParent.asc_getLevel() + 1);
		oReply.wsId = (oReply.oParent == null) ? -1 : oReply.oParent.wsId;
		oReply.setId();
		oReply.asc_putCol(this.nCol);
		oReply.asc_putRow(this.nRow);
		this.aReplies.push(oReply);

		return oReply;
	},

	asc_getMasterCommentId: function () {
		return this.wsId;
	},

	//	For collaborative editing
	getType: function() {
		return AscCommonExcel.UndoRedoDataTypes.CommentData;
	},

	getProperties: function() {
		return this.Properties;
	},

	getProperty: function(nType) {
		switch (nType) {
			case this.Properties.wsId: return this.wsId; break;
			case this.Properties.nCol: return this.nCol; break;
			case this.Properties.nRow: return this.nRow; break;
			case this.Properties.nId: return this.nId; break;
			case this.Properties.nLevel: return this.nLevel; break;
			case this.Properties.sText: return this.sText; break;
			case this.Properties.sTime: return this.sTime; break;
			case this.Properties.sOOTime: return this.sOOTime; break;
			case this.Properties.sUserId: return this.sUserId; break;
			case this.Properties.sUserName: return this.sUserName; break;
			case this.Properties.bDocument: return this.bDocument; break;
			case this.Properties.bSolved: return this.bSolved; break;
			case this.Properties.aReplies: return this.aReplies; break;
			case this.Properties.bHidden: return this.bHidden; break;
		}
		return null;
	},

	setProperty: function(nType, value) {
		switch (nType) {
			case this.Properties.wsId: this.wsId = value; break;
			case this.Properties.nCol: this.nCol = value; break;
			case this.Properties.nRow: this.nRow = value; break;
			case this.Properties.nId: this.nId = value; break;
			case this.Properties.nLevel: this.nLevel = value; break;
			case this.Properties.sText: this.sText = value; break;
			case this.Properties.sTime: this.sTime = value; break;
			case this.Properties.sOOTime: this.sOOTime = value; break;
			case this.Properties.sUserId: this.sUserId = value; break;
			case this.Properties.sUserName: this.sUserName = value; break;
			case this.Properties.bDocument: this.bDocument = value; break;
			case this.Properties.bSolved: this.bSolved = value; break;
			case this.Properties.aReplies: this.aReplies = value; break;
			case this.Properties.bHidden: this.bHidden = value; break;
		}
	},
	
	applyCollaborative: function (nSheetId, collaborativeEditing) {
		if ( !this.bDocument ) {
			this.nCol = collaborativeEditing.getLockMeColumn2(nSheetId, this.nCol);
			this.nRow = collaborativeEditing.getLockMeRow2(nSheetId, this.nRow);
		}
	}
};

	function CompositeCommentData() {
		this.commentBefore = null;
		this.commentAfter = null;

		this.Properties = {
			commentBefore: 0, commentAfter: 1
		};
	}

	CompositeCommentData.prototype.getType = function () {
		return AscCommonExcel.UndoRedoDataTypes.CompositeCommentData;
	};

	CompositeCommentData.prototype.getProperties = function () {
		return this.Properties;
	};

	CompositeCommentData.prototype.getProperty = function (nType) {
		switch (nType) {
			case this.Properties.commentBefore:
				return this.commentBefore;
				break;
			case this.Properties.commentAfter:
				return this.commentAfter;
				break;
		}
		return null;
	};

	CompositeCommentData.prototype.setProperty = function (nType, value) {
		switch (nType) {
			case this.Properties.commentBefore:
				this.commentBefore = value;
				break;
			case this.Properties.commentAfter:
				this.commentAfter = value;
				break;
		}
	};

/** @constructor */
function CCellCommentator(currentSheet) {
	this.worksheet = currentSheet;
	this.model = this.worksheet.model;
	this.overlayCtx = currentSheet.overlayCtx;
	this.drawingCtx = currentSheet.drawingCtx;

	// Drawing settings
	this.commentIconColor = new AscCommon.CColor(255, 144, 0);
	this.commentFillColor = new AscCommon.CColor(255, 255, 0);
	this.commentPadding = 4; 	// px
	this.minAreaWidth = 160; 	// px
	this.minAreaHeight = 80; 	// px

	this.lastSelectedId = null;
	this.bSaveHistory = true;
}
CCellCommentator.sStartCommentId = 'comment_';

//-----------------------------------------------------------------------------------
// Public methods
//-----------------------------------------------------------------------------------

CCellCommentator.prototype.isViewerMode = function () {
	return this.worksheet.handlers.trigger("getViewerMode");
};
CCellCommentator.prototype.isLockedComment = function(oComment, callbackFunc) {
	var objectGuid = oComment.asc_getId();
	if (objectGuid) {
		// Комментарии не должны влиять на lock-листа, поэтому вместо добавления нового c_oAscLockTypeElem, поменяем имя листа
		var sheetId = CCellCommentator.sStartCommentId;
		if (!oComment.bDocument)
			sheetId += this.model.getId();

		var lockInfo = this.worksheet.collaborativeEditing.getLockInfo(AscCommonExcel.c_oAscLockTypeElem.Object, /*subType*/null,
			sheetId, objectGuid);

		if (false === this.worksheet.collaborativeEditing.getCollaborativeEditing()) {
			// Пользователь редактирует один: не ждем ответа, а сразу продолжаем редактирование
			AscCommonExcel.applyFunction(callbackFunc, true);
			callbackFunc = undefined;
		}
		if (false !== this.worksheet.collaborativeEditing.getLockIntersection(lockInfo,
				AscCommon.c_oAscLockTypes.kLockTypeMine, /*bCheckOnlyLockAll*/false)) {
			// Редактируем сами
			AscCommonExcel.applyFunction(callbackFunc, true);
			return;
		} else if (false !== this.worksheet.collaborativeEditing.getLockIntersection(lockInfo,
				AscCommon.c_oAscLockTypes.kLockTypeOther, /*bCheckOnlyLockAll*/false)) {
			// Уже ячейку кто-то редактирует
			AscCommonExcel.applyFunction(callbackFunc, false);
			return;
		}

		this.worksheet.collaborativeEditing.onStartCheckLock();
		this.worksheet.collaborativeEditing.addCheckLock(lockInfo);
		this.worksheet.collaborativeEditing.onEndCheckLock(callbackFunc);
	}
};

	CCellCommentator.prototype.moveRangeComments = function (rangeFrom, rangeTo, copy) {
		if (rangeFrom && rangeTo) {
			var colOffset = rangeTo.c1 - rangeFrom.c1;
			var rowOffset = rangeTo.r1 - rangeFrom.r1;

			this.model.workbook.handlers.trigger("asc_onHideComment");
			var aComments = this.model.aComments;

			for (var i = 0; i < aComments.length; i++) {
				var comment = aComments[i];
				if (rangeFrom.contains(comment.nCol, comment.nRow)) {
					if (copy) {
						var newComment = new asc_CCommentData(comment);
						newComment.nCol += colOffset;
						newComment.nRow += rowOffset;
						newComment.setId();
						this.addComment(newComment, true);
					} else {
						var commentBefore = new asc_CCommentData(comment);
						comment.nCol += colOffset;
						comment.nRow += rowOffset;
						this.model.workbook.handlers.trigger("asc_onChangeCommentData", comment.asc_getId(), comment);

						var commentAfter = new asc_CCommentData(comment);

						var compositeComment = new CompositeCommentData();
						compositeComment.commentBefore = commentBefore;
						compositeComment.commentAfter = commentAfter;

						History.Create_NewPoint();
						History.Add(AscCommonExcel.g_oUndoRedoComment, AscCH.historyitem_Comment_Change, this.model.getId(),
							null, compositeComment);
					}
				}
			}
		}
	};

CCellCommentator.prototype.deleteCommentsRange = function(range) {
	if ( range ) {
		var aCommentId = [], i;
		var aComments = this.model.aComments;
		for (i = 0; i < aComments.length; ++i) {
			var comment = aComments[i];
			if (range.contains(comment.nCol, comment.nRow)) {
				aCommentId.push(comment.asc_getId());
			}
		}
		History.StartTransaction();
		for (i = 0; i < aCommentId.length; i++) {
			this.removeComment(aCommentId[i]);
		}
		History.EndTransaction();
	}
};

CCellCommentator.prototype.getCommentsXY = function(x, y) {
	var findCol = this.worksheet._findColUnderCursor(this.pxToPt(x), true);
	var findRow = this.worksheet._findRowUnderCursor(this.pxToPt(y), true);

	return (findCol && findRow) ? this.getComments(findCol.col, findRow.row) : [];
};

	CCellCommentator.prototype.drawCommentCells = function () {

		if (this.isViewerMode() || this.hiddenComments()) {
			return;
		}

		this.drawingCtx.setFillStyle(this.commentIconColor);
		var commentCell, mergedRange, nCol, nRow, x, y, metrics;
		var aComments = this.model.aComments;
		for (var i = 0; i < aComments.length; ++i) {
			commentCell = aComments[i];
			if (commentCell.asc_getDocumentFlag() || commentCell.asc_getHiddenFlag() ||
				(commentCell.asc_getSolved() && !this.showSolved())) {
				continue;
			}

			mergedRange = this.model.getMergedByCell(commentCell.nRow, commentCell.nCol);
			nCol = mergedRange ? mergedRange.c2 : commentCell.nCol;
			nRow = mergedRange ? mergedRange.r1 : commentCell.nRow;

			if (metrics = this.worksheet.getCellMetrics(nCol, nRow)) {
				if (0 === metrics.width || 0 === metrics.height) {
					continue;
				}
				x = metrics.left + metrics.width;
				y = metrics.top;
				this.drawingCtx.beginPath();
				this.drawingCtx.moveTo(x - this.pxToPt(7), y);
				this.drawingCtx.lineTo(x - this.pxToPt(1), y);
				this.drawingCtx.lineTo(x - this.pxToPt(1), y + this.pxToPt(6));
				this.drawingCtx.fill();
			}
		}
	};

CCellCommentator.prototype.getTextMetrics = function(text, units) {
	var metrics = { width: 0, height: 0 };

	if (text && text.length && ((typeof (text) == 'string') || (typeof (text) == 'number'))) {
		var textOptions = this.overlayCtx.measureText(text, units);
		metrics.width = textOptions.width;
		metrics.height = textOptions.lineHeight;
	}
	return metrics;
};

CCellCommentator.prototype.updateCommentPosition = function() {
	if (this.lastSelectedId) {
		var comment = this.findComment(this.lastSelectedId);
		if (comment) {

			var commentList = this.getComments(comment.asc_getCol(), comment.asc_getRow());
			if (commentList.length) {

				this.drawCommentCells();
				var coords = this.getCommentsCoords(commentList);

				var indexes = [];
				for (var i = 0; i < commentList.length; i++) {
					indexes.push(commentList[i].asc_getId());
				}
				var isVisible = (null !== this.worksheet.getCellVisibleRange(comment.asc_getCol(), comment.asc_getRow()));

				this.model.workbook.handlers.trigger( "asc_onUpdateCommentPosition", indexes,
					(isVisible ? coords.asc_getLeftPX() : -1),
					(isVisible ? coords.asc_getTopPX() : -1),
					(isVisible ? coords.asc_getReverseLeftPX() : -1) );
			}
		}
	}
};

CCellCommentator.prototype.updateCommentsDependencies = function(bInsert, operType, updateRange) {
	// ToDo переделать функцию, странная какая-то
	var t = this;
	var UpdatePair = function (comment, bChange) {
		this.comment = comment;
		this.bChange = bChange;
	};
	var aChangedComments = [];		// Array of UpdatePair

	function updateCommentsList(aComments) {
		if (aComments.length) {
			var changeArray = [];
			var removeArray = [];

			for (var i = 0; i < aComments.length; i++) {
				if (aComments[i].bChange) {
					t.bSaveHistory = false;
					t.changeComment(aComments[i].comment.asc_getId(), aComments[i].comment,
						/*bChangeCoords*/true, /*bNoEvent*/true, /*bNoAscLock*/true, /*bNoDraw*/false);
					changeArray.push({"Id": aComments[i].comment.asc_getId(), "Comment": aComments[i].comment});
					t.bSaveHistory = true;
				} else {
					t.removeComment(aComments[i].comment.asc_getId(), /*bNoEvent*/true,
						/*bNoAscLock*/true, /*bNoDraw*/false);
					removeArray.push(aComments[i].comment.asc_getId());
				}
			}

			if (changeArray.length)
				t.model.workbook.handlers.trigger("asc_onChangeComments", changeArray);
			if (removeArray.length)
				t.model.workbook.handlers.trigger("asc_onRemoveComments", removeArray);
		}
	}

	var i, comment;
	var aComments = this.model.aComments;
	if (bInsert) {
		switch (operType) {
			case c_oAscInsertOptions.InsertCellsAndShiftDown:
				for (i = 0; i < aComments.length; i++) {
					comment = new asc_CCommentData(aComments[i]);
					if ((comment.nRow >= updateRange.r1) && (comment.nCol >= updateRange.c1) && (comment.nCol <= updateRange.c2)) {
						comment.nRow += updateRange.r2 - updateRange.r1 + 1;
						aChangedComments.push(new UpdatePair(comment, true));
					}
				}
				break;

			case c_oAscInsertOptions.InsertCellsAndShiftRight:
				for (i = 0; i < aComments.length; i++) {
					comment = new asc_CCommentData(aComments[i]);
					if ((comment.nCol >= updateRange.c1) && (comment.nRow >= updateRange.r1) && (comment.nRow <= updateRange.r2)) {
						comment.nCol += updateRange.c2 - updateRange.c1 + 1;
						aChangedComments.push(new UpdatePair(comment, true));
					}
				}
				break;

			case c_oAscInsertOptions.InsertColumns:
				for (i = 0; i < aComments.length; i++) {
					comment = new asc_CCommentData(aComments[i]);
					if (comment.nCol >= updateRange.c1) {
						comment.nCol += updateRange.c2 - updateRange.c1 + 1;
						aChangedComments.push(new UpdatePair(comment, true));
					}
				}
				break;

			case c_oAscInsertOptions.InsertRows:
				for (i = 0; i < aComments.length; i++) {
					comment = new asc_CCommentData(aComments[i]);
					if (comment.nRow >= updateRange.r1) {
						comment.nRow += updateRange.r2 - updateRange.r1 + 1;
						aChangedComments.push(new UpdatePair(comment, true));
					}
				}
				break;
		}
	} else {
		switch (operType) {
			case c_oAscDeleteOptions.DeleteCellsAndShiftTop:
				for (i = 0; i < aComments.length; i++) {
					comment = new asc_CCommentData(aComments[i]);
					if ((comment.nRow > updateRange.r1) && (comment.nCol >= updateRange.c1) && (comment.nCol <= updateRange.c2)) {
						comment.nRow -= updateRange.r2 - updateRange.r1 + 1;
						aChangedComments.push(new UpdatePair(comment, true));
					} else if (updateRange.contains(comment.nCol, comment.nRow)) {
						aChangedComments.push(new UpdatePair(comment, false));
					}
				}
				break;

			case c_oAscDeleteOptions.DeleteCellsAndShiftLeft:
				for (i = 0; i < aComments.length; i++) {
					comment = new asc_CCommentData(aComments[i]);
					if ((comment.nCol > updateRange.c2) && (comment.nRow >= updateRange.r1) && (comment.nRow <= updateRange.r2)) {
						comment.nCol -= updateRange.c2 - updateRange.c1 + 1;
						aChangedComments.push(new UpdatePair(comment, true));
					} else if (updateRange.contains(comment.nCol, comment.nRow)) {
						aChangedComments.push(new UpdatePair(comment, false));
					}
				}
				break;

			case c_oAscDeleteOptions.DeleteColumns:
				for (i = 0; i < aComments.length; i++) {
					comment = new asc_CCommentData(aComments[i]);
					if (comment.nCol > updateRange.c2) {
						comment.nCol -= updateRange.c2 - updateRange.c1 + 1;
						aChangedComments.push(new UpdatePair(comment, true));
					} else if ((updateRange.c1 <= comment.nCol) && (updateRange.c2 >= comment.nCol)) {
						aChangedComments.push(new UpdatePair(comment, false));
					}
				}
				break;

			case c_oAscDeleteOptions.DeleteRows:
				for (i = 0; i < aComments.length; i++) {
					comment = new asc_CCommentData(aComments[i]);
					if (comment.nRow > updateRange.r2) {
						comment.nRow -= updateRange.r2 - updateRange.r1 + 1;
						aChangedComments.push(new UpdatePair(comment, true));
					} else if ((updateRange.r1 <= comment.nRow) && (updateRange.r2 >= comment.nRow)) {
						aChangedComments.push(new UpdatePair(comment, false));
					}
				}
				break;
		}
	}
	updateCommentsList(aChangedComments);
};

CCellCommentator.prototype.sortComments = function(sortData) {
	if (null === sortData)
		return;
	var comment, places = sortData.places, i = 0, l = places.length, j, row, line;
	var range = sortData.bbox, oComments = this.getRangeComments(new Asc.Range(range.c1, range.r1, range.c2, range.r2));
	if (null === oComments)
		return;

	History.StartTransaction();

	for (; i < l; ++i) {
		if (oComments.hasOwnProperty((row = places[i].from))) {
			for (j = 0, line = oComments[row]; j < line.length; ++j) {
				comment = new asc_CCommentData(line[j]);
				comment.nRow = places[i].to;
				this.changeComment(comment.asc_getId(), comment, true, false, true, true);
			}
		}
	}

	History.EndTransaction();
};

CCellCommentator.prototype.resetLastSelectedId = function() {
	this.cleanLastSelection();
	this.lastSelectedId = null;
};

CCellCommentator.prototype.cleanLastSelection = function() {
	var metrics;
	if (this.lastSelectedId) {
		var lastComment = this.findComment(this.lastSelectedId);
		if (lastComment && (metrics = this.worksheet.getCellMetrics(lastComment.nCol, lastComment.nRow))) {
			var extraOffset = this.pxToPt(1);
			this.overlayCtx.clearRect(metrics.left, metrics.top, metrics.width - extraOffset, metrics.height - extraOffset);
		}
	}
};

	CCellCommentator.prototype.getCoordsToSave = function () {
		/*	Calculate the coords of comments for:
		 *	first visible col = 0
		 *	first visible row = 0
		 *	+ document comments -> A1
		 */

		var aCommentsCoords = [];

		var aComments = this.model.aComments;
		for (var i = 0; i < aComments.length; i++) {

			var commentCell = aComments[i];
			var commentList = this.getComments(commentCell.asc_getCol(), commentCell.asc_getRow());

			// Calculate coords for document comments
			if (commentCell.asc_getCol() == 0 && commentCell.asc_getRow() == 0) {
				var documentComments = this.getDocumentComments();
				for (var j = 0; j < documentComments.length; j++) {
					commentList.push(documentComments[j]);
				}
			}

			if (commentList.length) {
				aCommentsCoords.push(this.getCommentsCoords(commentList));
			}
		}

		return aCommentsCoords;
	};

CCellCommentator.prototype.calcCommentArea = function (comment, coords) {
	/*	User name
	 *	Time
	 *	Text
	 */

	var originalFont = this.overlayCtx.getFont();
	var outputFont = originalFont.clone();

	// Set to bold
	outputFont.Bold = true;
	outputFont.FontSize = 9;
	this.overlayCtx.setFont(outputFont);

	// Title
	var txtMetrics = this.getTextMetrics(comment.sUserName, 1);
	coords.dHeightPX += this.ptToPx(txtMetrics.height);
	var userWidth = this.ptToPx(txtMetrics.width);

	if (coords.dWidthPX < userWidth)
		coords.dWidthPX = userWidth;

	txtMetrics = this.getTextMetrics(comment.sTime, 1);
	coords.dHeightPX += this.ptToPx(txtMetrics.height);
	var timeWidth = this.ptToPx(txtMetrics.width);

	if (coords.dWidthPX < timeWidth)
		coords.dWidthPX = timeWidth;

	// Set to normal
	outputFont.Bold = false;
	outputFont.FontSize = 9;
	this.overlayCtx.setFont(outputFont);

	// Comment text
	var commentSpl = comment.sText.split('\n'), i;
	for (i = 0; i < commentSpl.length; i++) {

		txtMetrics = this.getTextMetrics(commentSpl[i], 1);
		coords.dHeightPX += this.ptToPx(txtMetrics.height);
		var lineWidth = this.ptToPx(txtMetrics.width);
		if (coords.dWidthPX < lineWidth)
			coords.dWidthPX = lineWidth;
	}

	for (i = 0; i < comment.aReplies.length; i++) {
		this.calcCommentArea(comment.aReplies[i], coords);
	}

	// Min values
	if (coords.dWidthPX < this.minAreaWidth)
		coords.dWidthPX = this.minAreaWidth;

	if (coords.dHeightPX < this.minAreaHeight)
		coords.dHeightPX = this.minAreaHeight;

	// Calc other coords
	coords.dWidthMM = this.pxToMm(coords.dWidthPX);
	coords.dHeightMM = this.pxToMm(coords.dHeightPX);

	var headerRowOffPx = this.worksheet.getCellTop(0, 0);
	var headerColOffPx = this.worksheet.getCellLeft(0, 0);

	var headerCellsOffsetPt = this.worksheet.getCellsOffset(1);

	coords.nCol = comment.nCol;
	coords.nRow = comment.nRow;

	var mergedRange = this.model.getMergedByCell(comment.nRow, comment.nCol);

	coords.nLeft = (mergedRange ? mergedRange.c2 : comment.nCol) + 1;
	if ( !this.worksheet.cols[coords.nLeft] ) {
		this.worksheet.expandColsOnScroll(true);
		this.worksheet.handlers.trigger("reinitializeScrollX");
	}

	coords.nTop = mergedRange ? mergedRange.r1 : comment.nRow;
	coords.nLeftOffset = 0;
	coords.nTopOffset = 0;

	var fvr = this.worksheet.getFirstVisibleRow(false);
	var fvc = this.worksheet.getFirstVisibleCol(false);

	var frozenOffset = this.worksheet.getFrozenPaneOffset();
	if (this.worksheet.topLeftFrozenCell) {
		if (comment.nCol < fvc) {
			frozenOffset.offsetX = 0;
			fvc = 0;
		}
		if (comment.nRow < fvr) {
			frozenOffset.offsetY = 0;
			fvr = 0;
		}
	}

	var fvrLeft = this.worksheet.getCellLeft(fvc, 1) - headerCellsOffsetPt.left;
	var fvcTop = this.worksheet.getCellTop(fvr, 1) - headerCellsOffsetPt.top;

	// Tooltip coords
	coords.dReverseLeftPX = this.ptToPx(this.worksheet.getCellLeft(comment.nCol, 1) - fvrLeft + frozenOffset.offsetX);
	coords.dLeftPX = this.ptToPx(this.worksheet.getCellLeft(coords.nLeft, 1) - fvrLeft + frozenOffset.offsetX);
	coords.dTopPX = this.ptToPx(this.worksheet.getCellTop(coords.nTop, 1) - fvcTop + frozenOffset.offsetY);

	// Correction for merged cell
	var fvrPx = this.worksheet.getCellTop(0, 0);
	if (coords.dTopPX < fvrPx)
		coords.dTopPX = fvrPx;

	coords.dLeftMM = this.worksheet.getCellLeft(coords.nLeft, 3) - this.worksheet.getCellLeft(fvc, 3);
	coords.dTopMM = this.worksheet.getCellTop(coords.nTop, 3) - this.worksheet.getCellTop(fvr, 3);

	var findCol = this.worksheet._findColUnderCursor(this.worksheet.getCellLeft(coords.nLeft, 1) + this.pxToPt(coords.dWidthPX + headerColOffPx) - this.worksheet.getCellLeft(fvc, 1), true);
	var findRow = this.worksheet._findRowUnderCursor(this.worksheet.getCellTop(coords.nTop, 1) + this.pxToPt(coords.dHeightPX + headerRowOffPx) - this.worksheet.getCellTop(fvr, 1), true);

	coords.nRight = findCol ? findCol.col : 0;
	coords.nBottom = findRow ? findRow.row : 0;

	coords.nRightOffset = this.worksheet.getCellLeft(coords.nLeft, 0) + coords.nLeftOffset + coords.dWidthPX + headerColOffPx - this.worksheet.getCellLeft(coords.nRight, 0);
	coords.nBottomOffset = this.worksheet.getCellTop(coords.nTop, 0) + coords.nTopOffset + coords.dHeightPX + headerRowOffPx - this.worksheet.getCellTop(coords.nBottom, 0);

	// Return original font
	this.overlayCtx.setFont(originalFont);
};

CCellCommentator.prototype.getCommentsCoords = function(comments) {
	var coords = new asc_CCommentCoords();

	for (var i = 0; i < comments.length; i++) {
		this.calcCommentArea(comments[i], coords);
	}

	if (comments.length) {
		coords.dWidthPX += this.commentPadding * 2;
		coords.dWidthMM = this.pxToMm(coords.dWidthPX);

		coords.dHeightPX += this.commentPadding * 2;
		coords.dHeightMM = this.pxToMm(coords.dHeightPX);

    if (AscCommon.AscBrowser.isRetina) {
      coords.dWidthPX 		= AscCommon.AscBrowser.convertToRetinaValue(coords.dWidthPX);
      coords.dHeightPX 		= AscCommon.AscBrowser.convertToRetinaValue(coords.dHeightPX);
      coords.dLeftPX 		= AscCommon.AscBrowser.convertToRetinaValue(coords.dLeftPX);
      coords.dTopPX 		= AscCommon.AscBrowser.convertToRetinaValue(coords.dTopPX);
      coords.dReverseLeftPX = AscCommon.AscBrowser.convertToRetinaValue(coords.dReverseLeftPX);
    }
	}

	return coords;
};

	CCellCommentator.prototype.cleanSelectedComment = function () {
		var metrics;
		if (this.lastSelectedId) {
			var comment = this.findComment(this.lastSelectedId);
			if (comment && !comment.asc_getDocumentFlag() && (this.showSolved() || !comment.asc_getSolved()) &&
				(metrics = this.worksheet.getCellMetrics(comment.asc_getCol(), comment.asc_getRow()))) {
				this.overlayCtx.clearRect(metrics.left, metrics.top, metrics.width, metrics.height);
			}
		}
	};

//-----------------------------------------------------------------------------------
// Misc methods
//-----------------------------------------------------------------------------------

CCellCommentator.prototype.pxToPt = function(val) {
	return val * this.ascCvtRatio(0, 1);
};

CCellCommentator.prototype.ptToPx = function(val) {
	return val * this.ascCvtRatio(1, 0);
};

CCellCommentator.prototype.mmToPx = function(val) {
	return val * this.ascCvtRatio(3, 0);
};

CCellCommentator.prototype.pxToMm = function(val) {
	return val * this.ascCvtRatio(0, 3);
};

CCellCommentator.prototype.ascCvtRatio = function(fromUnits, toUnits) {
	return Asc.getCvtRatio(fromUnits, toUnits, this.overlayCtx.getPPIX());
};

// Main

CCellCommentator.prototype.showComment = function(id, bNew) {
	var comment = this.findComment(id);
	if (comment) {
		var commentList = this.getComments(comment.asc_getCol(), comment.asc_getRow());
		var coords = this.getCommentsCoords(commentList);

		var indexes = [];
		for (var i = 0; i < commentList.length; i++) {
			indexes.push(commentList[i].asc_getId());
		}

		// Second click - hide comment
		if (indexes.length) {
			this.model.workbook.handlers.trigger("asc_onShowComment", indexes, coords.asc_getLeftPX(),
				coords.asc_getTopPX(), coords.asc_getReverseLeftPX(), bNew);
			this.drawCommentCells();
		}
		this.lastSelectedId = id;
	} else
		this.lastSelectedId = null;
};

CCellCommentator.prototype.selectComment = function(id, bMove) {
	var comment = this.findComment(id);
	var metrics;

	// Чистим предыдущий селект
	this.cleanLastSelection();
	this.lastSelectedId = null;

	if (comment && !comment.asc_getDocumentFlag() && (this.showSolved() || !comment.asc_getSolved())) {

		this.lastSelectedId = id;

		var col = comment.asc_getCol();
		var row = comment.asc_getRow();
		var fvc = this.worksheet.getFirstVisibleCol(true);
		var fvr = this.worksheet.getFirstVisibleRow(true);
		var lvc = this.worksheet.getLastVisibleCol();
		var lvr = this.worksheet.getLastVisibleRow();

		var offset;
		if ( bMove ) {
			if ( (row < fvr) || (row > lvr) ) {
				offset = row - fvr - Math.round(( lvr - fvr ) / 2);
				this.worksheet.scrollVertical(offset);
				this.worksheet.handlers.trigger("reinitializeScrollY");
			}
			if ( (col < fvc) || (col > lvc) ) {
				offset = col - fvc - Math.round(( lvc - fvc ) / 2);
				this.worksheet.scrollHorizontal(offset);
				this.worksheet.handlers.trigger("reinitializeScrollX");
			}
		}

		if (metrics = this.worksheet.getCellMetrics(col, row)) {
			var extraOffset = this.pxToPt(1);
			this.overlayCtx.ctx.globalAlpha = 0.2;
			this.overlayCtx.beginPath();
			this.overlayCtx.clearRect(metrics.left, metrics.top, metrics.width - extraOffset, metrics.height - extraOffset);
			this.overlayCtx.setFillStyle(this.commentFillColor);
			this.overlayCtx.fillRect(metrics.left, metrics.top, metrics.width - extraOffset, metrics.height - extraOffset);
			this.overlayCtx.ctx.globalAlpha = 1;
		}
	}
};

CCellCommentator.prototype.findComment = function(id) {
	function checkCommentId(id, commentObject) {

		if (commentObject.asc_getId() == id)
			return commentObject;

		for (var i = 0; i < commentObject.aReplies.length; i++) {
			var comment = checkCommentId(id, commentObject.aReplies[i]);
			if (comment)
				return comment;
		}
		return null;
	}

	var aComments = this.model.aComments;
	for (var i = 0; i < aComments.length; i++) {
		var commentCell = aComments[i];
		var obj = checkCommentId(id, commentCell);
		if (obj)
			return obj;
	}
	return null;
};

CCellCommentator.prototype.addComment = function(comment, bIsNotUpdate) {
};

CCellCommentator.prototype.changeComment = function(id, oComment, bChangeCoords, bNoEvent, bNoAscLock, bNoDraw) {
	var t = this;
	var comment = this.findComment(id);
	if (null === comment)
		return;

	var onChangeCommentCallback = function (isSuccess) {
		if (false === isSuccess)
			return;

		var commentBefore = new asc_CCommentData(comment);
		if (comment) {
			if ( bChangeCoords ) {
				comment.asc_putCol(oComment.asc_getCol());
				comment.asc_putRow(oComment.asc_getRow());
			}
			comment.asc_putText(oComment.asc_getText());
			comment.asc_putQuoteText(oComment.asc_getQuoteText());
			comment.asc_putUserId(oComment.asc_getUserId());
			comment.asc_putUserName(oComment.asc_getUserName());
			comment.asc_putTime(oComment.asc_getTime());
			comment.asc_putSolved(oComment.asc_getSolved());
			comment.asc_putHiddenFlag(oComment.asc_getHiddenFlag());
			comment.aReplies = [];

			var count = oComment.asc_getRepliesCount();
			for (var i = 0; i < count; i++) {
				comment.asc_addReply(oComment.asc_getReply(i));
			}
			if ( !bNoEvent )
				t.model.workbook.handlers.trigger("asc_onChangeCommentData", comment.asc_getId(), comment);
		}

		if ( t.bSaveHistory ) {
			var commentAfter = new asc_CCommentData(comment);

			var compositeComment = new CompositeCommentData();
			compositeComment.commentBefore = commentBefore;
			compositeComment.commentAfter = commentAfter;

			History.Create_NewPoint();
			History.Add(AscCommonExcel.g_oUndoRedoComment, AscCH.historyitem_Comment_Change, t.model.getId(), null, compositeComment);
		}

		if (!bNoDraw)
			t.drawCommentCells();
	};

	if (bNoAscLock)
		onChangeCommentCallback(true);
	else
		this.isLockedComment(comment, onChangeCommentCallback);
};

CCellCommentator.prototype.removeComment = function(id, bNoEvent, bNoAscLock, bNoDraw) {
	var t = this;
	var comment = this.findComment(id);
	if (null === comment)
		return;

	var onRemoveCommentCallback = function (isSuccess) {
		if (false === isSuccess)
			return;

		t._removeComment(comment, bNoEvent, !bNoDraw);
	};

	if (bNoAscLock)
		onRemoveCommentCallback(true);
	else
		this.isLockedComment(comment, onRemoveCommentCallback);
};

// Extra functions

	CCellCommentator.prototype.getComments = function (col, row) {
		// Array of root items
		var comments = [];
		var _col = col, _row = row, mergedRange = null;
		var aComments = this.model.aComments;
		var length = aComments.length;

		if (this.hiddenComments()) {
			return comments;
		}

		if (0 < length) {
			if (null == _col || null == _row) {
				var activeCell = this.model.selectionRange.activeCell;
				_col = activeCell.col;
				_row = activeCell.row;
			} else {
				mergedRange = this.model.getMergedByCell(row, col);
			}

			for (var i = 0; i < length; i++) {
				var commentCell = aComments[i];
				if (!commentCell.asc_getDocumentFlag() && !commentCell.asc_getHiddenFlag() &&
					(!commentCell.asc_getSolved() || this.showSolved()) && 0 === commentCell.nLevel) {
					if (!mergedRange) {
						if (_col === commentCell.nCol && _row === commentCell.nRow) {
							comments.push(commentCell);
						}
					} else {
						if (mergedRange.contains(commentCell.nCol, commentCell.nRow)) {
							comments.push(commentCell);
						}
					}
				}
			}
		}
		return comments;
	};

	CCellCommentator.prototype.getRangeComments = function (range) {
		var oComments = {};
		if (this.hiddenComments()) {
			return null;
		}

		var aComments = this.model.aComments;
		var i, length, comment, bEmpty = true;
		for (i = 0, length = aComments.length; i < length; ++i) {
			comment = aComments[i];
			if (range.contains(comment.nCol, comment.nRow)) {
				bEmpty = false;
				if (!oComments.hasOwnProperty(comment.nRow)) {
					oComments[comment.nRow] = [];
				}
				oComments[comment.nRow].push(comment);
			}
		}

		return bEmpty ? null : oComments;
	};

CCellCommentator.prototype.getDocumentComments = function() {

	// Array of root items
	var comments = [];
	var aComments = this.model.aComments;

	for (var i = 0; i < aComments.length; i++) {
		var commentCell = aComments[i];
		if ((commentCell.nLevel == 0) && commentCell.asc_getDocumentFlag())
			comments.push(commentCell);
	}
	return comments;
};

CCellCommentator.prototype._addComment = function (oComment, bChange, bIsNotUpdate) {
	// Add new comment
	if (!bChange) {
		History.Create_NewPoint();
		History.Add(AscCommonExcel.g_oUndoRedoComment, AscCH.historyitem_Comment_Add, this.model.getId(), null, new asc_CCommentData(oComment));

		this.model.aComments.push(oComment);

		if (!bIsNotUpdate)
			this.drawCommentCells();
	}
	this.model.workbook.handlers.trigger('addComment', oComment.asc_getId(), oComment);
};

CCellCommentator.prototype._removeComment = function (comment, bNoEvent, isDraw) {
	if (!comment)
		return;

	var aComments = this.model.aComments;
	var i, id = comment.asc_getId();
	if (comment.oParent) {
		for (i = 0; i < comment.oParent.aReplies.length; ++i) {
			if (comment.asc_getId() == comment.oParent.aReplies[i].asc_getId()) {

				if (this.bSaveHistory) {
					History.Create_NewPoint();
					History.Add(AscCommonExcel.g_oUndoRedoComment, AscCH.historyitem_Comment_Remove, this.model.getId(), null, new asc_CCommentData(comment.oParent.aReplies[i]));
				}

				comment.oParent.aReplies.splice(i, 1);
				break;
			}
		}
	} else {
		for (i = 0; i < aComments.length; i++) {
			if (comment.asc_getId() == aComments[i].asc_getId()) {

				if (this.bSaveHistory) {
					History.Create_NewPoint();
					History.Add(AscCommonExcel.g_oUndoRedoComment, AscCH.historyitem_Comment_Remove, this.model.getId(), null, new asc_CCommentData(aComments[i]));
				}

				aComments.splice(i, 1);
				break;
			}
		}
		if (isDraw)
			this.worksheet.draw();
	}

	if (isDraw)
		this.drawCommentCells();
	if (!bNoEvent)
		this.model.workbook.handlers.trigger('removeComment', id);
};

CCellCommentator.prototype.isMissComments = function (range) {
	var aComments = this.model.aComments;
	var oComment, bMiss = false;
	for (var i = 0, length = aComments.length; i < length; ++i) {
		oComment = aComments[i];
		if (!oComment.bHidden && range.contains(oComment.nCol, oComment.nRow)) {
			if (bMiss)
				return true;
			bMiss = true;
		}
	}

	return false;
};

CCellCommentator.prototype.mergeComments = function (range) {
	var aComments = this.model.aComments;
	var i, length, deleteComments = [], oComment, r1 = range.r1, c1 = range.c1, mergeComment = null;
	for (i = 0, length = aComments.length; i < length; ++i) {
		oComment = aComments[i];
		if (range.contains(oComment.nCol, oComment.nRow)) {
			if (null === mergeComment)
				mergeComment = oComment;
			else if (oComment.nRow <= mergeComment.nRow && oComment.nCol < mergeComment.nCol) {
				deleteComments.push(mergeComment);
				mergeComment = oComment;
			} else
				deleteComments.push(oComment);
		}
	}

	if (mergeComment && (mergeComment.nCol !== c1 || mergeComment.nRow !== r1)) {
		this._removeComment(mergeComment, false, false);

		// add Comment
		mergeComment.nCol = c1;
		mergeComment.nRow = r1;
		this._addComment(mergeComment, false, true);
	}
	for (i = 0, length = deleteComments.length; i < length; ++i) {
		this._removeComment(deleteComments[i], false, false);
	}
};

// Undo/Redo

CCellCommentator.prototype.Undo = function(type, data) {
	var aComments = this.model.aComments;
	var i, parentComment;
	switch (type) {

		case AscCH.historyitem_Comment_Add:
			if (data.oParent) {
				parentComment = this.findComment(data.oParent.asc_getId());
				for (i = 0; i < parentComment.aReplies.length; i++) {
					if (parentComment.aReplies[i].asc_getId() == data.asc_getId()) {
						parentComment.aReplies.splice(i, 1);
						break;
					}
				}
			} else {
				for (i = 0; i < aComments.length; i++) {
					if (aComments[i].asc_getId() == data.asc_getId()) {
						aComments.splice(i, 1);
						this.model.workbook.handlers.trigger('removeComment', data.asc_getId());
						break;
					}
				}
			}
			break;

		case AscCH.historyitem_Comment_Remove:
			if (data.oParent) {
				parentComment = this.findComment(data.oParent.asc_getId());
				parentComment.aReplies.push(data);
			} else {
				aComments.push(data);
				this.model.workbook.handlers.trigger('addComment', data.asc_getId(), data);
			}
			break;

		case AscCH.historyitem_Comment_Change:
			if (data.commentAfter.oParent) {
				parentComment = this.findComment(data.commentAfter.oParent.asc_getId());
				for (i = 0; i < parentComment.aReplies.length; i++) {
					if (parentComment.aReplies[i].asc_getId() == data.asc_getId()) {
						parentComment.aReplies.splice(i, 1);
						parentComment.aReplies.push(data.commentBefore);
						break;
					}
				}
			} else {
				for (i = 0; i < aComments.length; i++) {
					if (aComments[i].asc_getId() == data.commentAfter.asc_getId()) {
						aComments.splice(i, 1);
						aComments.push(data.commentBefore);
						this.model.workbook.handlers.trigger("asc_onChangeCommentData", data.commentBefore.asc_getId(), data.commentBefore);
						break;
					}
				}
			}
			break;
	}
};

CCellCommentator.prototype.Redo = function(type, data) {
	var aComments = this.model.aComments;
	var parentComment, i;
	switch (type) {

		case AscCH.historyitem_Comment_Add:
			if (data.oParent) {
				parentComment = this.findComment(data.oParent.asc_getId());
				parentComment.aReplies.push(data);
			} else {
				aComments.push(data);
				this.model.workbook.handlers.trigger('addComment', data.asc_getId(), data);
			}
			break;

		case AscCH.historyitem_Comment_Remove:
			if (data.oParent) {
				parentComment = this.findComment(data.oParent.asc_getId());
				for (i = 0; i < parentComment.aReplies.length; i++) {
					if (parentComment.aReplies[i].asc_getId() == data.asc_getId()) {
						parentComment.aReplies.splice(i, 1);
						break;
					}
				}
			} else {
				for (i = 0; i < aComments.length; i++) {
					if (aComments[i].asc_getId() == data.asc_getId()) {
						aComments.splice(i, 1);
						this.model.workbook.handlers.trigger('removeComment', data.asc_getId());
						break;
					}
				}
			}
			break;

		case AscCH.historyitem_Comment_Change:
			if (data.commentBefore.oParent) {
				parentComment = this.findComment(data.commentBefore.oParent.asc_getId());
				for (i = 0; i < parentComment.aReplies.length; i++) {
					if (parentComment.aReplies[i].asc_getId() == data.asc_getId()) {
						parentComment.aReplies.splice(i, 1);
						parentComment.aReplies.push(data.commentAfter);
						break;
					}
				}
			} else {
				for (i = 0; i < aComments.length; i++) {
					if (aComments[i].asc_getId() == data.commentBefore.asc_getId()) {
						aComments.splice(i, 1);
						aComments.push(data.commentAfter);
						this.model.workbook.handlers.trigger("asc_onChangeCommentData", data.commentAfter.asc_getId(), data.commentAfter);
						break;
					}
				}
			}
			break;
	}
};

	CCellCommentator.prototype.hiddenComments = function () {
		return this.model.workbook.handlers.trigger('hiddenComments');
	};
	CCellCommentator.prototype.showSolved = function () {
		return this.model.workbook.handlers.trigger('showSolved');
	};

	//----------------------------------------------------------export----------------------------------------------------
	var prot;
	window['AscCommonExcel'] = window['AscCommonExcel'] || {};
	window["AscCommonExcel"].asc_CCommentCoords = asc_CCommentCoords;
	window["AscCommonExcel"].CompositeCommentData = CompositeCommentData;
	window["AscCommonExcel"].CCellCommentator = CCellCommentator;

	window['Asc'] = window['Asc'] || {};
	window["Asc"]["asc_CCommentData"] = window["Asc"].asc_CCommentData = asc_CCommentData;
	prot = asc_CCommentData.prototype;
	prot["asc_putRow"] = prot.asc_putRow;
	prot["asc_getRow"] = prot.asc_getRow;
	prot["asc_putCol"] = prot.asc_putCol;
	prot["asc_getCol"] = prot.asc_getCol;
	prot["asc_putId"] = prot.asc_putId;
	prot["asc_getId"] = prot.asc_getId;
	prot["asc_putLevel"] = prot.asc_putLevel;
	prot["asc_getLevel"] = prot.asc_getLevel;
	prot["asc_putParent"] = prot.asc_putParent;
	prot["asc_getParent"] = prot.asc_getParent;
	prot["asc_putText"] = prot.asc_putText;
	prot["asc_getText"] = prot.asc_getText;
	prot["asc_putQuoteText"] = prot.asc_putQuoteText;
	prot["asc_getQuoteText"] = prot.asc_getQuoteText;
	prot["asc_putTime"] = prot.asc_putTime;
	prot["asc_getTime"] = prot.asc_getTime;
	prot["asc_putOnlyOfficeTime"] = prot.asc_putOnlyOfficeTime;
	prot["asc_getOnlyOfficeTime"] = prot.asc_getOnlyOfficeTime;
	prot["asc_putUserId"] = prot.asc_putUserId;
	prot["asc_getUserId"] = prot.asc_getUserId;
	prot["asc_putUserName"] = prot.asc_putUserName;
	prot["asc_getUserName"] = prot.asc_getUserName;
	prot["asc_putDocumentFlag"] = prot.asc_putDocumentFlag;
	prot["asc_getDocumentFlag"] = prot.asc_getDocumentFlag;
	prot["asc_putHiddenFlag"] = prot.asc_putHiddenFlag;
	prot["asc_getHiddenFlag"] = prot.asc_getHiddenFlag;
	prot["asc_putSolved"] = prot.asc_putSolved;
	prot["asc_getSolved"] = prot.asc_getSolved;
	prot["asc_getRepliesCount"] = prot.asc_getRepliesCount;
	prot["asc_getReply"] = prot.asc_getReply;
	prot["asc_addReply"] = prot.asc_addReply;
	prot["asc_getMasterCommentId"] = prot.asc_getMasterCommentId;
})(window);
