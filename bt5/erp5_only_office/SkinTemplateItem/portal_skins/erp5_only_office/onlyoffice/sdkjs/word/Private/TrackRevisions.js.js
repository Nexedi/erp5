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
var changestype_2_ElementsArray_and_Type = AscCommon.changestype_2_ElementsArray_and_Type;
var History = AscCommon.History;

//----------------------------------------------------------------------------------------------------------------------
// Работаем с рецензированием
//----------------------------------------------------------------------------------------------------------------------
Asc['asc_docs_api'].prototype.asc_SetTrackRevisions = function(bTrack)
{
    return this.WordControl.m_oLogicDocument.Set_TrackRevisions(bTrack);
};
Asc['asc_docs_api'].prototype.asc_IsTrackRevisions = function()
{
    return this.WordControl.m_oLogicDocument.Is_TrackRevisions();
};
Asc['asc_docs_api'].prototype.sync_BeginCatchRevisionsChanges = function()
{
    this.RevisionChangesStack = [];
};
Asc['asc_docs_api'].prototype.sync_EndCatchRevisionsChanges = function()
{
    this.sendEvent("asc_onShowRevisionsChange", this.RevisionChangesStack);
};
Asc['asc_docs_api'].prototype.asc_GetRevisionsChangesStack = function()
{
	return this.RevisionChangesStack;
};
Asc['asc_docs_api'].prototype.sync_AddRevisionsChange = function(Change)
{
    this.RevisionChangesStack.push(Change);
};
Asc['asc_docs_api'].prototype.asc_AcceptChanges = function(Change)
{
    if (undefined !== Change)
        this.WordControl.m_oLogicDocument.Accept_RevisionChange(Change);
    else
        this.WordControl.m_oLogicDocument.AcceptRevisionChangesBySelection();
};
Asc['asc_docs_api'].prototype.asc_RejectChanges = function(Change)
{
    if (undefined !== Change)
        this.WordControl.m_oLogicDocument.Reject_RevisionChange(Change);
    else
        this.WordControl.m_oLogicDocument.RejectRevisionChangesBySelection();
};
Asc['asc_docs_api'].prototype.asc_HaveRevisionsChanges = function()
{
    this.WordControl.m_oLogicDocument.Have_RevisionChanges();
};
Asc['asc_docs_api'].prototype.asc_HaveNewRevisionsChanges = function()
{
    return this.asc_HaveRevisionsChanges();
};
Asc['asc_docs_api'].prototype.asc_GetNextRevisionsChange = function()
{
    return this.WordControl.m_oLogicDocument.Get_NextRevisionChange();
};
Asc['asc_docs_api'].prototype.asc_GetPrevRevisionsChange = function()
{
    return this.WordControl.m_oLogicDocument.Get_PrevRevisionChange();
};
Asc['asc_docs_api'].prototype.sync_UpdateRevisionsChangesPosition = function(X, Y)
{
    this.sendEvent("asc_onUpdateRevisionsChangesPosition", X, Y);
};
Asc['asc_docs_api'].prototype.asc_AcceptAllChanges = function()
{
    this.WordControl.m_oLogicDocument.Accept_AllRevisionChanges();
};
Asc['asc_docs_api'].prototype.asc_RejectAllChanges = function()
{
    this.WordControl.m_oLogicDocument.Reject_AllRevisionChanges();
};
Asc['asc_docs_api'].prototype.asc_GetTrackRevisionsReportByAuthors = function()
{
	var oResult = {};
	var oAllChanges = this.WordControl.m_oLogicDocument.TrackRevisionsManager.Get_AllChanges();
	for (var ParaId in oAllChanges)
	{
		var arrChanges = oAllChanges[ParaId];
		for (var nIndex = 0, nCount = arrChanges.length; nIndex < nCount; ++nIndex)
		{
			var oChange   = arrChanges[nIndex];
			var sUserName = oChange.get_UserName();
			var nDateTime = oChange.get_DateTime();

			if (!oResult[sUserName])
				oResult[sUserName] = [];

			var arrUserChanges = oResult[sUserName];

			var nPos = 0;
			var nLen = arrUserChanges.length;
			while (nPos < nLen)
			{
				if (nDateTime < arrUserChanges[nPos].get_DateTime())
					break;

				nPos++;
			}

			arrUserChanges.splice(nPos, 0, oChange);
		}
	}

	return oResult;
};

Asc['asc_docs_api'].prototype['asc_SetTrackRevisions']                = Asc['asc_docs_api'].prototype.asc_SetTrackRevisions;
Asc['asc_docs_api'].prototype['asc_IsTrackRevisions']                 = Asc['asc_docs_api'].prototype.asc_IsTrackRevisions;
Asc['asc_docs_api'].prototype['sync_BeginCatchRevisionsChanges']      = Asc['asc_docs_api'].prototype.sync_BeginCatchRevisionsChanges;
Asc['asc_docs_api'].prototype['sync_EndCatchRevisionsChanges']        = Asc['asc_docs_api'].prototype.sync_EndCatchRevisionsChanges;
Asc['asc_docs_api'].prototype['sync_AddRevisionsChange']              = Asc['asc_docs_api'].prototype.sync_AddRevisionsChange;
Asc['asc_docs_api'].prototype['asc_AcceptChanges']                    = Asc['asc_docs_api'].prototype.asc_AcceptChanges;
Asc['asc_docs_api'].prototype['asc_RejectChanges']                    = Asc['asc_docs_api'].prototype.asc_RejectChanges;
Asc['asc_docs_api'].prototype['asc_HaveRevisionsChanges']             = Asc['asc_docs_api'].prototype.asc_HaveRevisionsChanges;
Asc['asc_docs_api'].prototype['asc_HaveNewRevisionsChanges']          = Asc['asc_docs_api'].prototype.asc_HaveNewRevisionsChanges;
Asc['asc_docs_api'].prototype['asc_GetNextRevisionsChange']           = Asc['asc_docs_api'].prototype.asc_GetNextRevisionsChange;
Asc['asc_docs_api'].prototype['asc_GetPrevRevisionsChange']           = Asc['asc_docs_api'].prototype.asc_GetPrevRevisionsChange;
Asc['asc_docs_api'].prototype['sync_UpdateRevisionsChangesPosition']  = Asc['asc_docs_api'].prototype.sync_UpdateRevisionsChangesPosition;
Asc['asc_docs_api'].prototype['asc_AcceptAllChanges']                 = Asc['asc_docs_api'].prototype.asc_AcceptAllChanges;
Asc['asc_docs_api'].prototype['asc_RejectAllChanges']                 = Asc['asc_docs_api'].prototype.asc_RejectAllChanges;
Asc['asc_docs_api'].prototype['asc_GetTrackRevisionsReportByAuthors'] = Asc['asc_docs_api'].prototype.asc_GetTrackRevisionsReportByAuthors;
//----------------------------------------------------------------------------------------------------------------------
// CDocument
//----------------------------------------------------------------------------------------------------------------------
CDocument.prototype.Set_TrackRevisions = function(bTrack)
{
    this.TrackRevisions = bTrack;
};
CDocument.prototype.Continue_TrackRevisions = function()
{
    this.TrackRevisionsManager.Continue_TrackRevisions();
};
CDocument.prototype.Get_NextRevisionChange = function()
{
    this.TrackRevisionsManager.Continue_TrackRevisions();
    var Change = this.TrackRevisionsManager.Get_NextChange();
    if (null !== Change)
    {
        this.RemoveSelection();
        var Para = Change.get_Paragraph();
        Para.Selection.Use = true;
        Para.Set_SelectionContentPos(Change.get_StartPos(), Change.get_EndPos());
        Para.Set_ParaContentPos(Change.get_StartPos(), false, -1, -1);
        Para.Document_SetThisElementCurrent(false);

        this.Document_UpdateSelectionState();
        this.Document_UpdateInterfaceState(true);
    }
};
CDocument.prototype.Get_PrevRevisionChange = function()
{
    this.TrackRevisionsManager.Continue_TrackRevisions();
    var Change = this.TrackRevisionsManager.Get_PrevChange();
    if (null !== Change)
    {
        this.RemoveSelection();
        var Para = Change.get_Paragraph();
        Para.Selection.Use = true;
        Para.Set_SelectionContentPos(Change.get_StartPos(), Change.get_EndPos());
        Para.Set_ParaContentPos(Change.get_StartPos(), false, -1, -1);
        Para.Document_SetThisElementCurrent(false);

        this.Document_UpdateSelectionState();
        this.Document_UpdateInterfaceState(true);
    }
};
CDocument.prototype.GetRevisionsChangeParagraph = function(Direction, CurrentPara)
{
    return this.private_GetRevisionsChangeParagraph(Direction, CurrentPara).Get_FoundedParagraph();
};
CDocument.prototype.private_GetRevisionsChangeParagraph = function(Direction, CurrentPara)
{
    var SearchEngine = new CRevisionsChangeParagraphSearchEngine(Direction, CurrentPara, this.TrackRevisionsManager);
    if (null === CurrentPara)
    {
        CurrentPara = this.GetCurrentParagraph();
        if (null === CurrentPara)
            return SearchEngine;

        SearchEngine.Set_CurrentParagraph(CurrentPara);
        SearchEngine.Set_FoundedParagraph(CurrentPara);
        if (true === SearchEngine.Is_Found())
            return SearchEngine;
    }

    var oFootnote = CurrentPara.Parent ? CurrentPara.Parent.Get_TopDocumentContent() : null;
    if (!(oFootnote instanceof CFootEndnote))
    	oFootnote = null;

    var HdrFtr = CurrentPara.Get_HdrFtr();
    if (null !== HdrFtr)
    {
        this.private_GetRevisionsChangeParagraphInHdrFtr(SearchEngine, HdrFtr);

        if (Direction > 0)
		{
			if (true !== SearchEngine.Is_Found())
				this.private_GetRevisionsChangeParagraphInDocument(SearchEngine, 0);

			if (true !== SearchEngine.Is_Found())
				this.private_GetRevisionsChangeParagraphInFooters(SearchEngine, null);
		}
		else
		{
			if (true !== SearchEngine.Is_Found())
				this.private_GetRevisionsChangeParagraphInFooters(SearchEngine, null);

			if (true !== SearchEngine.Is_Found())
				this.private_GetRevisionsChangeParagraphInDocument(SearchEngine, this.Content.length - 1);
		}


        if (true !== SearchEngine.Is_Found())
            this.private_GetRevisionsChangeParagraphInHdrFtr(SearchEngine, null);
    }
    else if (oFootnote)
	{
		this.private_GetRevisionsChangeParagraphInFooters(SearchEngine, oFootnote);

		if (Direction > 0)
		{
			if (true !== SearchEngine.Is_Found())
				this.private_GetRevisionsChangeParagraphInHdrFtr(SearchEngine, null);

			if (true !== SearchEngine.Is_Found())
				this.private_GetRevisionsChangeParagraphInDocument(SearchEngine, 0);
		}
		else
		{
			if (true !== SearchEngine.Is_Found())
				this.private_GetRevisionsChangeParagraphInDocument(SearchEngine, this.Content.length - 1);

			if (true !== SearchEngine.Is_Found())
				this.private_GetRevisionsChangeParagraphInHdrFtr(SearchEngine, null);
		}

		if (true !== SearchEngine.Is_Found())
			this.private_GetRevisionsChangeParagraphInFooters(SearchEngine, null);
	}
    else
    {
        var Pos = (true === this.Selection.Use && docpostype_DrawingObjects !== this.Get_DocPosType() ? (this.Selection.StartPos <= this.Selection.EndPos ? this.Selection.StartPos : this.Selection.EndPos) : this.CurPos.ContentPos);
        this.private_GetRevisionsChangeParagraphInDocument(SearchEngine, Pos);

        if (Direction > 0)
		{
			if (true !== SearchEngine.Is_Found())
				this.private_GetRevisionsChangeParagraphInFooters(SearchEngine, null);

			if (true !== SearchEngine.Is_Found())
				this.private_GetRevisionsChangeParagraphInHdrFtr(SearchEngine, null);
		}
		else
		{
			if (true !== SearchEngine.Is_Found())
				this.private_GetRevisionsChangeParagraphInHdrFtr(SearchEngine, null);

			if (true !== SearchEngine.Is_Found())
				this.private_GetRevisionsChangeParagraphInFooters(SearchEngine, null);
		}

        if (true !== SearchEngine.Is_Found())
            this.private_GetRevisionsChangeParagraphInDocument(SearchEngine, Direction > 0 ? 0 : this.Content.length - 1);
    }

    return SearchEngine;
};
CDocument.prototype.private_GetRevisionsChangeParagraphInDocument = function(SearchEngine, Pos)
{
    var Direction = SearchEngine.Get_Direction();
    this.Content[Pos].GetRevisionsChangeParagraph(SearchEngine);
    while (true !== SearchEngine.Is_Found())
    {
        Pos = (Direction > 0 ? Pos + 1 : Pos - 1);
        if (Pos >= this.Content.length || Pos < 0)
            break;

        this.Content[Pos].GetRevisionsChangeParagraph(SearchEngine);
    }
};
CDocument.prototype.private_GetRevisionsChangeParagraphInHdrFtr = function(SearchEngine, HdrFtr)
{
    var AllHdrFtrs = this.SectionsInfo.Get_AllHdrFtrs();
    var Count = AllHdrFtrs.length;

    if (Count <= 0)
        return;

    var Pos = -1;
    if (null !== HdrFtr)
    {
        for (var Index = 0; Index < Count; ++Index)
        {
            if (HdrFtr === AllHdrFtrs[Index])
            {
                Pos = Index;
                break;
            }
        }
    }

    var Direction = SearchEngine.Get_Direction();
    if (Pos < 0 || Pos >= Count)
    {
        if (Direction > 0)
            Pos = 0;
        else
            Pos = Count - 1;
    }

    AllHdrFtrs[Pos].GetRevisionsChangeParagraph(SearchEngine);
    while (true !== SearchEngine.Is_Found())
    {
        Pos = (Direction > 0 ? Pos + 1 : Pos - 1);
        if (Pos >= Count || Pos < 0)
            break;

        AllHdrFtrs[Pos].GetRevisionsChangeParagraph(SearchEngine);
    }
};
CDocument.prototype.private_GetRevisionsChangeParagraphInFooters = function(SearchEngine, oFootnote)
{
	var arrFootnotes = this.Get_FootnotesList(null, null);
	var nCount = arrFootnotes.length;
	if (nCount <= 0)
		return;

	var nPos = -1;
	if (oFootnote)
	{
		for (var nIndex = 0; nIndex < nCount; ++nIndex)
		{
			if (arrFootnotes[nPos] === oFootnote)
			{
				nPos = nIndex;
				break;
			}
		}
	}

	var nDirection = SearchEngine.Get_Direction();
	if (nPos < 0 || nPos >= nCount)
	{
		if (nDirection > 0)
			nPos = 0;
		else
			nPos = nCount - 1;
	}

	arrFootnotes[nPos].GetRevisionsChangeParagraph(SearchEngine);
	while (true !== SearchEngine.Is_Found())
	{
		nPos = (nDirection > 0 ? nPos + 1 : nPos - 1);
		if (nPos >= nCount || nPos < 0)
			break;

		arrFootnotes[nPos].GetRevisionsChangeParagraph(SearchEngine);
	}
};
CDocument.prototype.private_SelectRevisionChange = function(Change)
{
    if (undefined !== Change && Change.get_Paragraph())
    {
        this.RemoveSelection();
        var Para = Change.get_Paragraph();
        Para.Selection.Use = true;
        Para.Set_SelectionContentPos(Change.get_StartPos(), Change.get_EndPos());
        Para.Set_ParaContentPos(Change.get_StartPos(), false, -1, -1);
        Para.Document_SetThisElementCurrent(false);
    }
};
CDocument.prototype.Accept_RevisionChange = function(Change)
{
    if (undefined !== Change)
    {
        var RelatedParas = this.TrackRevisionsManager.Get_ChangeRelatedParagraphs(Change, true);
        if (false === this.Document_Is_SelectionLocked(AscCommon.changestype_None, { Type : changestype_2_ElementsArray_and_Type, Elements : RelatedParas, CheckType : AscCommon.changestype_Paragraph_Content}))
        {
            this.Create_NewHistoryPoint(AscDFH.historydescription_Document_AcceptRevisionChange);
            this.private_SelectRevisionChange(Change);
            this.AcceptRevisionChanges(Change.get_Type(), false);
        }
    }
};
CDocument.prototype.Reject_RevisionChange = function(Change)
{
    if (undefined !== Change)
    {
        var RelatedParas = this.TrackRevisionsManager.Get_ChangeRelatedParagraphs(Change, false);
        if (false === this.Document_Is_SelectionLocked(AscCommon.changestype_None, { Type : changestype_2_ElementsArray_and_Type, Elements : RelatedParas, CheckType : AscCommon.changestype_Paragraph_Content}))
        {
            this.Create_NewHistoryPoint(AscDFH.historydescription_Document_RejectRevisionChange);
            this.private_SelectRevisionChange(Change);
            this.RejectRevisionChanges(Change.get_Type(), false);
        }
    }
};
CDocument.prototype.AcceptRevisionChangesBySelection = function()
{
    var CurrentChange = this.TrackRevisionsManager.Get_CurrentChange();
    if (null !== CurrentChange)
        this.Accept_RevisionChange(CurrentChange);
    else
    {
        var SelectedParagraphs = this.GetAllParagraphs({Selected : true});
        var RelatedParas = this.TrackRevisionsManager.Get_AllChangesRelatedParagraphsBySelectedParagraphs(SelectedParagraphs, true);
        if (false === this.Document_Is_SelectionLocked(AscCommon.changestype_None, { Type : changestype_2_ElementsArray_and_Type, Elements : RelatedParas, CheckType : AscCommon.changestype_Paragraph_Content}))
        {
            this.Create_NewHistoryPoint(AscDFH.historydescription_Document_AcceptRevisionChangesBySelection);
            this.AcceptRevisionChanges(undefined, false);

            if (true === this.History.Is_LastPointEmpty())
                this.History.Remove_LastPoint();
        }
    }

    this.Get_NextRevisionChange();
};
CDocument.prototype.RejectRevisionChangesBySelection = function()
{
    var CurrentChange = this.TrackRevisionsManager.Get_CurrentChange();
    if (null !== CurrentChange)
        this.Reject_RevisionChange(CurrentChange);
    else
    {
        var SelectedParagraphs = this.GetAllParagraphs({Selected : true});
        var RelatedParas = this.TrackRevisionsManager.Get_AllChangesRelatedParagraphsBySelectedParagraphs(SelectedParagraphs, false);
        if (false === this.Document_Is_SelectionLocked(AscCommon.changestype_None, { Type : changestype_2_ElementsArray_and_Type, Elements : RelatedParas, CheckType : AscCommon.changestype_Paragraph_Content}))
        {
            this.Create_NewHistoryPoint(AscDFH.historydescription_Document_AcceptRevisionChangesBySelection);
            this.RejectRevisionChanges(undefined, false);

            if (true === this.History.Is_LastPointEmpty())
                this.History.Remove_LastPoint();
        }
    }

    this.Get_NextRevisionChange();
};
CDocument.prototype.Accept_AllRevisionChanges = function(isSkipCheckLock)
{
    var RelatedParas = this.TrackRevisionsManager.Get_AllChangesRelatedParagraphs(true);
    if (true === isSkipCheckLock || false === this.Document_Is_SelectionLocked(AscCommon.changestype_None, { Type : changestype_2_ElementsArray_and_Type, Elements : RelatedParas, CheckType : AscCommon.changestype_Paragraph_Content}))
    {
        this.Create_NewHistoryPoint(AscDFH.historydescription_Document_AcceptAllRevisionChanges);
        var LogicDocuments = this.TrackRevisionsManager.Get_AllChangesLogicDocuments();
        for (var LogicDocId in LogicDocuments)
        {
            var LogicDoc = AscCommon.g_oTableId.Get_ById(LogicDocId);
            if (LogicDoc)
            {
                LogicDoc.AcceptRevisionChanges(undefined, true);
            }
        }

        if (true !== isSkipCheckLock && true === this.History.Is_LastPointEmpty())
        {
            this.History.Remove_LastPoint();
            return;
        }

        this.RemoveSelection();
        this.private_CorrectDocumentPosition();
        this.Recalculate();
        this.Document_UpdateSelectionState();
        this.Document_UpdateInterfaceState();
    }
};
CDocument.prototype.Reject_AllRevisionChanges = function(isSkipCheckLock)
{
    var RelatedParas = this.TrackRevisionsManager.Get_AllChangesRelatedParagraphs(false);
    if (true === isSkipCheckLock || false === this.Document_Is_SelectionLocked(AscCommon.changestype_None, { Type : changestype_2_ElementsArray_and_Type, Elements : RelatedParas, CheckType : AscCommon.changestype_Paragraph_Content}))
    {
        this.Create_NewHistoryPoint(AscDFH.historydescription_Document_RejectAllRevisionChanges);
        var LogicDocuments = this.TrackRevisionsManager.Get_AllChangesLogicDocuments();
        for (var LogicDocId in LogicDocuments)
        {
            var LogicDoc = AscCommon.g_oTableId.Get_ById(LogicDocId);
            if (LogicDoc)
            {
                LogicDoc.RejectRevisionChanges(undefined, true);
            }
        }

        if (true !== isSkipCheckLock && true === this.History.Is_LastPointEmpty())
        {
            this.History.Remove_LastPoint();
            return;
        }

        this.RemoveSelection();
        this.private_CorrectDocumentPosition();
        this.Recalculate();
        this.Document_UpdateSelectionState();
        this.Document_UpdateInterfaceState();
    }
};
CDocument.prototype.AcceptRevisionChanges = function(Type, bAll)
{
    // Принимаем все изменения, которые попали в селект.
    // Принимаем изменения в следующей последовательности:
    // 1. Изменение настроек параграфа
    // 2. Изменение настроек текста
    // 3. Добавление/удаление текста
    // 4. Добавление/удаление параграфа
    if (docpostype_Content === this.CurPos.Type || true === bAll)
    {
        if (true === this.Selection.Use || true === bAll)
        {
            var StartPos = this.Selection.StartPos;
            var EndPos = this.Selection.EndPos;
            if (StartPos > EndPos)
            {
                StartPos = this.Selection.EndPos;
                EndPos = this.Selection.StartPos;
            }

            var LastElement = this.Content[EndPos];
            var LastParaEnd = (type_Paragraph === LastElement.Get_Type() && true === LastElement.Selection_CheckParaEnd() ? true : false);

            if (true === bAll)
            {
                StartPos = 0;
                EndPos = this.Content.length - 1;
                LastParaEnd = true;
            }

            if (undefined === Type || c_oAscRevisionsChangeType.ParaPr === Type)
            {
                for (var CurPos = StartPos; CurPos <= EndPos; CurPos++)
                {
                    var Element = this.Content[CurPos];
                    if (type_Paragraph === Element.Get_Type() && (true === Element.IsSelectedAll() || true == bAll) && true === Element.Have_PrChange())
                    {
                        Element.Accept_PrChange();
                    }
                }
            }

            for (var CurPos = StartPos; CurPos <= EndPos; CurPos++)
            {
                var Element = this.Content[CurPos];
                Element.AcceptRevisionChanges(Type, bAll);
            }

            if (undefined === Type || c_oAscRevisionsChangeType.ParaAdd === Type || c_oAscRevisionsChangeType.ParaRem === Type)
            {
                EndPos = (true === LastParaEnd ? EndPos : EndPos - 1);
                for (var CurPos = EndPos; CurPos >= StartPos; CurPos--)
                {
                    var Element = this.Content[CurPos];
                    if (type_Paragraph === Element.Get_Type())
                    {
                        var ReviewType = Element.Get_ReviewType();
                        if (reviewtype_Add === ReviewType && (undefined === Type || c_oAscRevisionsChangeType.ParaAdd === Type))
                        {
                            Element.Set_ReviewType(reviewtype_Common);
                        }
                        else if (reviewtype_Remove === ReviewType && (undefined === Type || c_oAscRevisionsChangeType.ParaRem === Type))
                        {
                            Element.Set_ReviewType(reviewtype_Common);
                            this.Concat_Paragraphs(CurPos);
                        }
                    }
                }
            }
        }
    }
    else if (docpostype_HdrFtr === this.CurPos.Type)
    {
        this.HdrFtr.AcceptRevisionChanges(Type, bAll);
    }
    else if (docpostype_DrawingObjects === this.CurPos.Type)
    {
        this.DrawingObjects.AcceptRevisionChanges(Type, bAll);
    }
    else if (docpostype_Footnotes === this.CurPos.Type)
	{
		this.Footnotes.AcceptRevisionChanges(Type, bAll);
	}

    if (true !== bAll)
    {
        this.Recalculate();
        this.Document_UpdateInterfaceState();
        this.Document_UpdateSelectionState();
    }
};
CDocument.prototype.RejectRevisionChanges = function(Type, bAll)
{
    // Отменяем все изменения, которые попали в селект.
    // Отменяем изменения в следующей последовательности:
    // 1. Изменение настроек параграфа
    // 2. Изменение настроек текста
    // 3. Добавление/удаление текста
    // 4. Добавление/удаление параграфа

    if (docpostype_Content === this.CurPos.Type || true === bAll)
    {
        if (true === this.Selection.Use || true === bAll)
        {
            var StartPos = this.Selection.StartPos;
            var EndPos = this.Selection.EndPos;
            if (StartPos > EndPos)
            {
                StartPos = this.Selection.EndPos;
                EndPos = this.Selection.StartPos;
            }

            var LastElement = this.Content[EndPos];
            var LastParaEnd = (type_Paragraph === LastElement.Get_Type() && true === LastElement.Selection_CheckParaEnd() ? true : false);

            if (true === bAll)
            {
                StartPos = 0;
                EndPos = this.Content.length - 1;
                LastParaEnd = true;
            }

            if (undefined === Type || c_oAscRevisionsChangeType.ParaPr === Type)
            {
                for (var CurPos = StartPos; CurPos <= EndPos; CurPos++)
                {
                    var Element = this.Content[CurPos];
                    if (type_Paragraph === Element.Get_Type() && (true === Element.IsSelectedAll() || true === bAll) && true === Element.Have_PrChange())
                    {
                        Element.Reject_PrChange();
                    }
                }
            }

            for (var CurPos = StartPos; CurPos <= EndPos; CurPos++)
            {
                var Element = this.Content[CurPos];
                Element.RejectRevisionChanges(Type, bAll);
            }

            if (undefined === Type || c_oAscRevisionsChangeType.ParaAdd === Type || c_oAscRevisionsChangeType.ParaRem === Type)
            {
                EndPos = (true === LastParaEnd ? EndPos : EndPos - 1);
                for (var CurPos = EndPos; CurPos >= StartPos; CurPos--)
                {
                    var Element = this.Content[CurPos];
                    if (type_Paragraph === Element.Get_Type())
                    {
                        var ReviewType = Element.Get_ReviewType();
                        if (reviewtype_Add === ReviewType && (undefined === Type || c_oAscRevisionsChangeType.ParaAdd === Type))
                        {
                            Element.Set_ReviewType(reviewtype_Common);
                            this.Concat_Paragraphs(CurPos);
                        }
                        else if (reviewtype_Remove === ReviewType && (undefined === Type || c_oAscRevisionsChangeType.ParaRem === Type))
                        {
                            Element.Set_ReviewType(reviewtype_Common);
                        }
                    }
                }
            }
        }
    }
    else if (docpostype_HdrFtr === this.CurPos.Type)
    {
        this.HdrFtr.RejectRevisionChanges(Type, bAll);
    }
    else if (docpostype_DrawingObjects === this.CurPos.Type)
    {
        this.DrawingObjects.RejectRevisionChanges(Type, bAll);
    }
    else if (docpostype_Footnotes === this.CurPos.Type)
	{
		this.Footnotes.RejectRevisionChanges(Type, bAll);
	}

    if (true !== bAll)
    {
        this.Recalculate();
        this.Document_UpdateInterfaceState();
        this.Document_UpdateSelectionState();
    }
};
CDocument.prototype.Have_RevisionChanges = function()
{
    this.TrackRevisionsManager.Continue_TrackRevisions();
    return this.TrackRevisionsManager.Have_Changes();
};
//----------------------------------------------------------------------------------------------------------------------
// CHeaderFooterController
//----------------------------------------------------------------------------------------------------------------------
CHeaderFooterController.prototype.AcceptRevisionChanges = function(Type, bAll)
{
    if (null !== this.CurHdrFtr)
        this.CurHdrFtr.Content.AcceptRevisionChanges(Type, bAll);
};
CHeaderFooterController.prototype.RejectRevisionChanges = function(Type, bAll)
{
    if (null !== this.CurHdrFtr)
        this.CurHdrFtr.Content.RejectRevisionChanges(Type, bAll);
};
//----------------------------------------------------------------------------------------------------------------------
// CDocumentContent
//----------------------------------------------------------------------------------------------------------------------
CDocumentContent.prototype.AcceptRevisionChanges = function(Type, bAll)
{
    if (docpostype_Content === this.CurPos.Type || true === bAll)
    {
        if (true === this.Selection.Use || true === bAll)
        {
            var StartPos = this.Selection.StartPos;
            var EndPos   = this.Selection.EndPos;
            if (StartPos > EndPos)
            {
                StartPos = this.Selection.EndPos;
                EndPos   = this.Selection.StartPos;
            }
            var LastElement = this.Content[EndPos];
            var LastParaEnd = (type_Paragraph === LastElement.Get_Type() && true === LastElement.Selection_CheckParaEnd() ? true : false);

            if (true === bAll)
            {
                StartPos    = 0;
                EndPos      = this.Content.length - 1;
                LastParaEnd = true;
            }

            if (undefined === Type || c_oAscRevisionsChangeType.ParaPr === Type)
            {
                for (var CurPos = StartPos; CurPos <= EndPos; CurPos++)
                {
                    var Element = this.Content[CurPos];
                    if (type_Paragraph === Element.Get_Type() && (true === Element.IsSelectedAll() || true === bAll) && true === Element.Have_PrChange())
                    {
                        Element.Accept_PrChange();
                    }
                }
            }

            for (var CurPos = StartPos; CurPos <= EndPos; CurPos++)
            {
                var Element = this.Content[CurPos];
                Element.AcceptRevisionChanges(Type, bAll);
            }

            if (undefined === Type || c_oAscRevisionsChangeType.ParaAdd === Type || c_oAscRevisionsChangeType.ParaRem === Type)
            {
                EndPos = (true === LastParaEnd ? EndPos : EndPos - 1);
                for (var CurPos = EndPos; CurPos >= StartPos; CurPos--)
                {
                    var Element = this.Content[CurPos];
                    if (type_Paragraph === Element.Get_Type())
                    {
                        var ReviewType = Element.Get_ReviewType();
                        if (reviewtype_Add === ReviewType && (undefined === Type || c_oAscRevisionsChangeType.ParaAdd === Type))
                        {
                            Element.Set_ReviewType(reviewtype_Common);
                        }
                        else if (reviewtype_Remove === ReviewType && (undefined === Type || c_oAscRevisionsChangeType.ParaRem === Type))
                        {
                            Element.Set_ReviewType(reviewtype_Common);
                            this.Concat_Paragraphs(CurPos);
                        }
                    }
                }
            }
        }
    }
    else if (docpostype_DrawingObjects === this.CurPos.Type)
    {
        this.DrawingObjects.AcceptRevisionChanges(Type, bAll);
    }
};
CDocumentContent.prototype.RejectRevisionChanges = function(Type, bAll)
{
    if (docpostype_Content === this.CurPos.Type || true === bAll)
    {
        if (true === this.Selection.Use || true === bAll)
        {
            var StartPos = this.Selection.StartPos;
            var EndPos = this.Selection.EndPos;
            if (StartPos > EndPos)
            {
                StartPos = this.Selection.EndPos;
                EndPos = this.Selection.StartPos;
            }
            var LastElement = this.Content[EndPos];
            var LastParaEnd = (type_Paragraph === LastElement.Get_Type() && true === LastElement.Selection_CheckParaEnd() ? true : false);

            if (true === bAll)
            {
                StartPos = 0;
                EndPos = this.Content.length - 1;
                LastParaEnd = true;
            }

            if (undefined === Type || c_oAscRevisionsChangeType.ParaPr === Type)
            {
                for (var CurPos = StartPos; CurPos <= EndPos; CurPos++)
                {
                    var Element = this.Content[CurPos];
                    if (type_Paragraph === Element.Get_Type() && (true === Element.IsSelectedAll() || true === bAll) && true === Element.Have_PrChange())
                    {
                        Element.Reject_PrChange();
                    }
                }
            }

            for (var CurPos = StartPos; CurPos <= EndPos; CurPos++)
            {
                var Element = this.Content[CurPos];
                Element.RejectRevisionChanges(Type, bAll);
            }

            if (undefined === Type || c_oAscRevisionsChangeType.ParaAdd === Type || c_oAscRevisionsChangeType.ParaRem === Type)
            {
                EndPos = (true === LastParaEnd ? EndPos : EndPos - 1);
                for (var CurPos = EndPos; CurPos >= StartPos; CurPos--)
                {
                    var Element = this.Content[CurPos];
                    if (type_Paragraph === Element.Get_Type())
                    {
                        var ReviewType = Element.Get_ReviewType();
                        if (reviewtype_Add === ReviewType && (undefined === Type || c_oAscRevisionsChangeType.ParaAdd === Type))
                        {
                            Element.Set_ReviewType(reviewtype_Common);
                            this.Concat_Paragraphs(CurPos);
                        }
                        else if (reviewtype_Remove === ReviewType && (undefined === Type || c_oAscRevisionsChangeType.ParaRem === Type))
                        {
                            Element.Set_ReviewType(reviewtype_Common);
                        }
                    }
                }
            }
        }
    }
    else if (docpostype_DrawingObjects === this.CurPos.Type)
    {
        this.DrawingObjects.RejectRevisionChanges(Type, bAll);
    }
};
CDocumentContent.prototype.GetRevisionsChangeParagraph = function(SearchEngine)
{
    if (true === SearchEngine.Is_Found())
        return;

    var Direction = SearchEngine.Get_Direction();
    var Pos = 0;
    if (true !== SearchEngine.Is_CurrentFound())
    {
        Pos = (true === this.Selection.Use ? (this.Selection.StartPos <= this.Selection.EndPos ? this.Selection.StartPos : this.Selection.EndPos) : this.CurPos.ContentPos);
    }
    else
    {
        if (Direction > 0)
        {
            Pos = 0;
        }
        else
        {
            Pos = this.Content.length - 1;
        }
    }

    this.Content[Pos].GetRevisionsChangeParagraph(SearchEngine);
    while (true !== SearchEngine.Is_Found())
    {
        Pos = (Direction > 0 ? Pos + 1 : Pos - 1);
        if (Pos >= this.Content.length || Pos < 0)
            break;

        this.Content[Pos].GetRevisionsChangeParagraph(SearchEngine);
    }
};
//----------------------------------------------------------------------------------------------------------------------
// CFootnotesController
//----------------------------------------------------------------------------------------------------------------------
CFootnotesController.prototype.AcceptRevisionChanges = function(Type, bAll)
{
	if (null !== this.CurFootnote)
		this.CurFootnote.AcceptRevisionChanges(Type, bAll);
};
CFootnotesController.prototype.RejectRevisionChanges = function(Type, bAll)
{
	if (null !== this.CurFootnote)
		this.CurFootnote.RejectRevisionChanges(Type, bAll);
};