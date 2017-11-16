"use strict";
/**
 * User: Ilja.Kirillov
 * Date: 10.06.2016
 * Time: 15:31
 */

/**
 * Специальный класс-обработчик команд в автофигурах
 * @param {CDocument} LogicDocument - Ссылка на главный документ.
 * @param {CDrawingsObjects} DrawingsObjects - ССылка на объект, работающий с автофигурами
 * @constructor
 * @extends {CDocumentControllerBase}
 */
function CDrawingsController(LogicDocument, DrawingsObjects)
{
	CDocumentControllerBase.call(this, LogicDocument);

	this.DrawingObjects = DrawingsObjects;
}
CDrawingsController.prototype = Object.create(CDocumentControllerBase.prototype);
CDrawingsController.prototype.constructor = CDrawingsController;

CDrawingsController.prototype.CanUpdateTarget = function()
{
	return true;
};
CDrawingsController.prototype.RecalculateCurPos = function()
{
	return this.DrawingObjects.recalculateCurPos();
};
CDrawingsController.prototype.GetCurPage = function()
{
	var ParaDrawing = this.DrawingObjects.getMajorParaDrawing();
	if (null !== ParaDrawing)
		return ParaDrawing.PageNum;

	return -1;
};
CDrawingsController.prototype.AddNewParagraph = function(bRecalculate, bForceAdd)
{
	return this.DrawingObjects.addNewParagraph(bRecalculate, bForceAdd);
};
CDrawingsController.prototype.AddInlineImage = function(nW, nH, oImage, oChart, bFlow)
{
	return this.DrawingObjects.addInlineImage(nW, nH, oImage, oChart, bFlow);
};
CDrawingsController.prototype.AddImages = function(aImages)
{
	return this.DrawingObjects.addImages(aImages);
};
CDrawingsController.prototype.AddSignatureLine = function(oSignatureDrawing)
{
	return this.DrawingObjects.addSignatureLine(oSignatureDrawing);
};
CDrawingsController.prototype.AddOleObject = function(W, H, nWidthPix, nHeightPix, Img, Data, sApplicationId)
{
	this.DrawingObjects.addOleObject(W, H, nWidthPix, nHeightPix, Img, Data, sApplicationId);
};
CDrawingsController.prototype.AddTextArt = function(nStyle)
{
	// ничего не делаем
};
CDrawingsController.prototype.EditChart = function(Chart)
{
	this.DrawingObjects.editChart(Chart);
};
CDrawingsController.prototype.AddInlineTable = function(Cols, Rows)
{
	this.DrawingObjects.addInlineTable(Cols, Rows);
};
CDrawingsController.prototype.ClearParagraphFormatting = function()
{
	this.DrawingObjects.paragraphClearFormatting();
};
CDrawingsController.prototype.AddToParagraph = function(oItem, bRecalculate)
{
	if (para_NewLine === oItem.Type && true === oItem.IsPageOrColumnBreak())
		return;

	this.DrawingObjects.paragraphAdd(oItem, bRecalculate);
	this.LogicDocument.Document_UpdateSelectionState();
	this.LogicDocument.Document_UpdateUndoRedoState();
	this.LogicDocument.Document_UpdateInterfaceState();
};
CDrawingsController.prototype.Remove = function(Count, bOnlyText, bRemoveOnlySelection, bOnTextAdd)
{
	return this.DrawingObjects.remove(Count, bOnlyText, bRemoveOnlySelection, bOnTextAdd);
};
CDrawingsController.prototype.GetCursorPosXY = function()
{
	return this.DrawingObjects.cursorGetPos();
};
CDrawingsController.prototype.MoveCursorToStartPos = function(AddToSelect)
{
	if (true === AddToSelect)
	{
		// TODO: Пока ничего не делаем, в дальнейшем надо будет делать в зависимости от селекта внутри
		//       автофигуры: если селект текста внутри, то делать для текста внутри, а если выделена
		//       сама автофигура, тогда мы перемещаем курсор влево от нее в контенте параграфа и выделяем все до конца
	}
	else
	{
		this.LogicDocument.controller_MoveCursorToStartPos(false);
	}
};
CDrawingsController.prototype.MoveCursorToEndPos = function(AddToSelect)
{
	if (true === AddToSelect)
	{
		// TODO: Пока ничего не делаем, в дальнейшем надо будет делать в зависимости от селекта внутри
		//       автофигуры: если селект текста внутри, то делать для текста внутри, а если выделена
		//       сама автофигура, тогда мы перемещаем курсор влево от нее в контенте параграфа и выделяем все до конца
	}
	else
	{
		this.LogicDocument.controller_MoveCursorToEndPos(false);
	}
};
CDrawingsController.prototype.MoveCursorLeft = function(AddToSelect, Word)
{
	return this.DrawingObjects.cursorMoveLeft(AddToSelect, Word);
};
CDrawingsController.prototype.MoveCursorRight = function(AddToSelect, Word, FromPaste)
{
	return this.DrawingObjects.cursorMoveRight(AddToSelect, Word, FromPaste);
};
CDrawingsController.prototype.MoveCursorUp = function(AddToSelect, CtrlKey)
{
	var RetValue = this.DrawingObjects.cursorMoveUp(AddToSelect, CtrlKey);
	this.LogicDocument.Document_UpdateInterfaceState();
	this.LogicDocument.Document_UpdateSelectionState();
	return RetValue;
};
CDrawingsController.prototype.MoveCursorDown = function(AddToSelect, CtrlKey)
{
	var RetValue = this.DrawingObjects.cursorMoveDown(AddToSelect, CtrlKey);
	this.LogicDocument.Document_UpdateInterfaceState();
	this.LogicDocument.Document_UpdateSelectionState();
	return RetValue;
};
CDrawingsController.prototype.MoveCursorToEndOfLine = function(AddToSelect)
{
	return this.DrawingObjects.cursorMoveEndOfLine(AddToSelect);
};
CDrawingsController.prototype.MoveCursorToStartOfLine = function(AddToSelect)
{
	return this.DrawingObjects.cursorMoveStartOfLine(AddToSelect);
};
CDrawingsController.prototype.MoveCursorToXY = function(X, Y, PageAbs, AddToSelect)
{
	return this.DrawingObjects.cursorMoveAt(X, Y, AddToSelect);
};
CDrawingsController.prototype.MoveCursorToCell = function(bNext)
{
	return this.DrawingObjects.cursorMoveToCell(bNext);
};
CDrawingsController.prototype.SetParagraphAlign = function(Align)
{
	if (true != this.DrawingObjects.isSelectedText())
	{
		var ParaDrawing = this.DrawingObjects.getMajorParaDrawing();
		if (null != ParaDrawing)
		{
			var Paragraph = ParaDrawing.Parent;
			Paragraph.Set_Align(Align);
		}
	}
	else
	{
		this.DrawingObjects.setParagraphAlign(Align);
	}
};
CDrawingsController.prototype.SetParagraphSpacing = function (Spacing)
{
	if (true != this.DrawingObjects.isSelectedText())
	{
		var ParaDrawing = this.DrawingObjects.getMajorParaDrawing();
		if (null != ParaDrawing)
		{
			var Paragraph = ParaDrawing.Parent;
			Paragraph.Set_Spacing(Spacing, false);
			this.LogicDocument.Recalculate();
		}
	}
	else
	{
		this.DrawingObjects.setParagraphSpacing(Spacing);
	}
};
CDrawingsController.prototype.SetParagraphTabs = function(Tabs)
{
	this.DrawingObjects.setParagraphTabs(Tabs);
};
CDrawingsController.prototype.SetParagraphIndent = function(Ind)
{
	this.DrawingObjects.setParagraphIndent(Ind);
};
CDrawingsController.prototype.SetParagraphNumbering = function(NumInfo)
{
	this.DrawingObjects.setParagraphNumbering(NumInfo);
};
CDrawingsController.prototype.SetParagraphShd = function(Shd)
{
	this.DrawingObjects.setParagraphShd(Shd);
};
CDrawingsController.prototype.SetParagraphStyle = function(Name)
{
	this.DrawingObjects.setParagraphStyle(Name);
};
CDrawingsController.prototype.SetParagraphContextualSpacing = function(Value)
{
	this.DrawingObjects.setParagraphContextualSpacing(Value);
};
CDrawingsController.prototype.SetParagraphPageBreakBefore = function(Value)
{
	this.DrawingObjects.setParagraphPageBreakBefore(Value);
};
CDrawingsController.prototype.SetParagraphKeepLines = function(Value)
{
	this.DrawingObjects.setParagraphKeepLines(Value);
};
CDrawingsController.prototype.SetParagraphKeepNext = function(Value)
{
	this.DrawingObjects.setParagraphKeepNext(Value);
};
CDrawingsController.prototype.SetParagraphWidowControl = function(Value)
{
	this.DrawingObjects.setParagraphWidowControl(Value);
};
CDrawingsController.prototype.SetParagraphBorders = function(Borders)
{
	this.DrawingObjects.setParagraphBorders(Borders);
};
CDrawingsController.prototype.SetParagraphFramePr = function(FramePr, bDelete)
{
	// Не добавляем и не работаем с рамками в автофигурах
};
CDrawingsController.prototype.IncreaseDecreaseFontSize = function(bIncrease)
{
	this.DrawingObjects.paragraphIncDecFontSize(bIncrease);
};
CDrawingsController.prototype.IncreaseDecreaseIndent = function(bIncrease)
{
	if (true != this.DrawingObjects.isSelectedText())
	{
		var ParaDrawing = this.DrawingObjects.getMajorParaDrawing();
		if (null != ParaDrawing)
		{
			var Paragraph = ParaDrawing.Parent;
			Paragraph.IncreaseDecreaseIndent(bIncrease);
		}
	}
	else
	{
		this.DrawingObjects.paragraphIncDecIndent(bIncrease);
	}
};
CDrawingsController.prototype.SetImageProps = function(Props)
{
	this.DrawingObjects.setProps(Props);
};
CDrawingsController.prototype.SetTableProps = function(Props)
{
	this.DrawingObjects.setTableProps(Props);
};
CDrawingsController.prototype.GetCalculatedParaPr = function()
{
	return this.DrawingObjects.getParagraphParaPr();
};
CDrawingsController.prototype.GetCalculatedTextPr = function()
{
	return this.DrawingObjects.getParagraphTextPr();
};
CDrawingsController.prototype.GetDirectParaPr = function()
{
	return this.DrawingObjects.getParagraphParaPrCopy();
};
CDrawingsController.prototype.GetDirectTextPr = function()
{
	return this.DrawingObjects.getParagraphTextPrCopy();
};
CDrawingsController.prototype.RemoveSelection = function(bNoCheckDrawing)
{
	var ParaDrawing = this.DrawingObjects.getMajorParaDrawing();
	if (ParaDrawing)
	{
		ParaDrawing.GoTo_Text(undefined, false);
	}
	return this.DrawingObjects.resetSelection(undefined, bNoCheckDrawing);
};
CDrawingsController.prototype.IsSelectionEmpty = function(bCheckHidden)
{
	return false;
};
CDrawingsController.prototype.DrawSelectionOnPage = function(PageAbs)
{
	this.DrawingDocument.SetTextSelectionOutline(true);
	this.DrawingObjects.drawSelectionPage(PageAbs);
};
CDrawingsController.prototype.GetSelectionBounds = function()
{
	return this.DrawingObjects.GetSelectionBounds();
};
CDrawingsController.prototype.IsMovingTableBorder = function()
{
	return this.DrawingObjects.selectionIsTableBorder();
};
CDrawingsController.prototype.CheckPosInSelection = function(X, Y, PageAbs, NearPos)
{
	return this.DrawingObjects.selectionCheck(X, Y, PageAbs, NearPos);
};
CDrawingsController.prototype.SelectAll = function()
{
	this.DrawingObjects.selectAll();
};
CDrawingsController.prototype.GetSelectedContent = function(SelectedContent)
{
	this.DrawingObjects.GetSelectedContent(SelectedContent);
};
CDrawingsController.prototype.UpdateCursorType = function(X, Y, PageAbs, MouseEvent)
{
	// TODO: Надо вызывать не у LogicDocument, а у DocumentContent заданного
	this.LogicDocument.controller_UpdateCursorType(X, Y, PageAbs, MouseEvent);
};
CDrawingsController.prototype.PasteFormatting = function(TextPr, ParaPr)
{
	this.DrawingObjects.paragraphFormatPaste(TextPr, ParaPr, false);
};
CDrawingsController.prototype.IsSelectionUse = function()
{
	return this.DrawingObjects.isSelectionUse();
};
CDrawingsController.prototype.IsTextSelectionUse = function()
{
	return this.DrawingObjects.isTextSelectionUse();
};
CDrawingsController.prototype.GetCurPosXY = function()
{
	return this.DrawingObjects.getCurPosXY();
};
CDrawingsController.prototype.GetSelectedText = function(bClearText, oPr)
{
	return this.DrawingObjects.getSelectedText(bClearText, oPr);
};
CDrawingsController.prototype.GetCurrentParagraph = function(bIgnoreSelection, arrSelectedParagraphs)
{
	return this.DrawingObjects.getCurrentParagraph(bIgnoreSelection, arrSelectedParagraphs);
};
CDrawingsController.prototype.GetSelectedElementsInfo = function(oInfo)
{
	this.DrawingObjects.getSelectedElementsInfo(oInfo);
};
CDrawingsController.prototype.AddTableRow = function(bBefore)
{
	this.DrawingObjects.tableAddRow(bBefore);
};
CDrawingsController.prototype.AddTableColumn = function(bBefore)
{
	this.DrawingObjects.tableAddCol(bBefore);
};
CDrawingsController.prototype.RemoveTableRow = function()
{
	this.DrawingObjects.tableRemoveRow();
};
CDrawingsController.prototype.RemoveTableColumn = function()
{
	this.DrawingObjects.tableRemoveCol();
};
CDrawingsController.prototype.MergeTableCells = function()
{
	this.DrawingObjects.tableMergeCells();
};
CDrawingsController.prototype.SplitTableCells = function(Cols, Rows)
{
	this.DrawingObjects.tableSplitCell(Cols, Rows);
};
CDrawingsController.prototype.RemoveTable = function()
{
	this.DrawingObjects.tableRemoveTable();
};
CDrawingsController.prototype.SelectTable = function(Type)
{
	this.DrawingObjects.tableSelect(Type);
};
CDrawingsController.prototype.CanMergeTableCells = function()
{
	return this.DrawingObjects.tableCheckMerge();
};
CDrawingsController.prototype.CanSplitTableCells = function()
{
	return this.DrawingObjects.tableCheckSplit();
};
CDrawingsController.prototype.UpdateInterfaceState = function()
{
	var oTargetTextObject = AscFormat.getTargetTextObject(this.DrawingObjects);
	if (oTargetTextObject)
	{
		this.LogicDocument.Interface_Update_DrawingPr();
		this.DrawingObjects.documentUpdateInterfaceState();
	}
	else
	{
		this.DrawingObjects.resetInterfaceTextPr();
		this.DrawingObjects.updateTextPr();
		this.LogicDocument.Interface_Update_DrawingPr();
		this.DrawingObjects.updateParentParagraphParaPr();
	}
};
CDrawingsController.prototype.UpdateRulersState = function()
{
	// Вызываем данную функцию, чтобы убрать рамку буквицы
	this.DrawingDocument.Set_RulerState_Paragraph(null);
	this.LogicDocument.Document_UpdateRulersStateBySection(this.LogicDocument.CurPos.ContentPos);
	this.DrawingObjects.documentUpdateRulersState();
};
CDrawingsController.prototype.UpdateSelectionState = function()
{
	this.DrawingObjects.documentUpdateSelectionState();
	this.LogicDocument.Document_UpdateTracks();
};
CDrawingsController.prototype.GetSelectionState = function()
{
	return this.DrawingObjects.getSelectionState();
};
CDrawingsController.prototype.SetSelectionState = function(State, StateIndex)
{
	this.DrawingObjects.setSelectionState(State, StateIndex);
};
CDrawingsController.prototype.AddHyperlink = function(Props)
{
	this.DrawingObjects.hyperlinkAdd(Props);
};
CDrawingsController.prototype.ModifyHyperlink = function(Props)
{
	this.DrawingObjects.hyperlinkModify(Props);
};
CDrawingsController.prototype.RemoveHyperlink = function()
{
	this.DrawingObjects.hyperlinkRemove();
};
CDrawingsController.prototype.CanAddHyperlink = function(bCheckInHyperlink)
{
	return this.DrawingObjects.hyperlinkCanAdd(bCheckInHyperlink);
};
CDrawingsController.prototype.IsCursorInHyperlink = function(bCheckEnd)
{
	return this.DrawingObjects.hyperlinkCheck(bCheckEnd);
};
CDrawingsController.prototype.AddComment = function(Comment)
{
	if (true !== this.DrawingObjects.isSelectedText())
	{
		var ParaDrawing = this.DrawingObjects.getMajorParaDrawing();
		if (null != ParaDrawing)
		{
			var Paragraph = ParaDrawing.Parent;
			Paragraph.AddCommentToObject(Comment, ParaDrawing.Get_Id());
		}
	}
	else
	{
		this.DrawingObjects.addComment(Comment);
	}
};
CDrawingsController.prototype.CanAddComment = function()
{
	if (true != this.DrawingObjects.isSelectedText())
		return true;
	else
		return this.DrawingObjects.canAddComment();
};
CDrawingsController.prototype.GetSelectionAnchorPos = function()
{
	var ParaDrawing = this.DrawingObjects.getMajorParaDrawing();
	return {
		X0   : ParaDrawing.GraphicObj.x,
		Y    : ParaDrawing.GraphicObj.y,
		X1   : ParaDrawing.GraphicObj.x + ParaDrawing.GraphicObj.extX,
		Page : ParaDrawing.PageNum
	};
};
CDrawingsController.prototype.StartSelectionFromCurPos = function()
{
	this.DrawingObjects.startSelectionFromCurPos();
};
CDrawingsController.prototype.SaveDocumentStateBeforeLoadChanges = function(State)
{
	this.DrawingObjects.Save_DocumentStateBeforeLoadChanges(State);
};
CDrawingsController.prototype.RestoreDocumentStateAfterLoadChanges = function(State)
{
	if (true !== this.DrawingObjects.Load_DocumentStateAfterLoadChanges(State))
	{
		var LogicDocument = this.LogicDocument;
		LogicDocument.Set_DocPosType(docpostype_Content);

		var ContentPos = 0;
		if (LogicDocument.Pages[LogicDocument.CurPage])
			ContentPos = LogicDocument.Pages[LogicDocument.CurPage].Pos + 1;
		else
			ContentPos = 0;

		ContentPos = Math.max(0, Math.min(LogicDocument.Content.length - 1, ContentPos));
		LogicDocument.CurPos.ContentPos = ContentPos;
		LogicDocument.Content[ContentPos].MoveCursorToStartPos(false);
	}
};
CDrawingsController.prototype.GetColumnSize = function()
{
	// TODO: Переделать
	var _w = Math.max(1, AscCommon.Page_Width - (AscCommon.X_Left_Margin + AscCommon.X_Right_Margin));
	var _h = Math.max(1, AscCommon.Page_Height - (AscCommon.Y_Top_Margin + AscCommon.Y_Bottom_Margin));

	return {
		W : AscCommon.Page_Width - (AscCommon.X_Left_Margin + AscCommon.X_Right_Margin),
		H : AscCommon.Page_Height - (AscCommon.Y_Top_Margin + AscCommon.Y_Bottom_Margin)
	};
};
CDrawingsController.prototype.GetCurrentSectionPr = function()
{
	return null;
};
CDrawingsController.prototype.RemoveTextSelection = function()
{
	this.DrawingObjects.removeTextSelection();
};
CDrawingsController.prototype.AddContentControl = function(nContentControlType)
{
	return this.DrawingObjects.AddContentControl(nContentControlType);
};