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

Asc['asc_docs_api'].prototype.asc_addComment = function(AscCommentData)
{
	if (true === AscCommon.CollaborativeEditing.Get_GlobalLock())
		return;

	var oLogicDocument = this.WordControl.m_oLogicDocument;

	if (!oLogicDocument)
		return;

	// Комментарий без цитаты позволяем добавить всегда
	if (true !== this.can_AddQuotedComment() || false === oLogicDocument.Document_Is_SelectionLocked(AscCommon.changestype_Paragraph_Content, null, true, oLogicDocument.IsEditCommentsMode()))
	{
		var CommentData = new CCommentData();
		CommentData.Read_FromAscCommentData(AscCommentData);

		this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_AddComment);
		var Comment = this.WordControl.m_oLogicDocument.AddComment(CommentData);
		if (null != Comment)
		{
			this.sync_AddComment(Comment.Get_Id(), CommentData);
		}

		return Comment.Get_Id();
	}
};
Asc['asc_docs_api'].prototype.asc_GetCommentsReportByAuthors = function()
{
	var oReport = {};

	function privateProcessCommentData(isTopComment, oCommentData)
	{
		var sUserName = oCommentData.GetUserName();
		var nDateTime = oCommentData.GetDateTime();

		if (!oReport[sUserName])
			oReport[sUserName] = [];

		var arrUserComments = oReport[sUserName];

		var nPos = 0;
		var nLen = arrUserComments.length;
		while (nPos < nLen)
		{
			if (nDateTime < arrUserComments[nPos].Data.GetDateTime())
				break;

			nPos++;
		}

		arrUserComments.splice(nPos, 0, {Top : isTopComment, Data : oCommentData});

		for (var nIndex = 0, nCount = oCommentData.GetRepliesCount(); nIndex < nCount; ++nIndex)
		{
			privateProcessCommentData(false, oCommentData.GetReply(nIndex))
		}
	}

	var oLogicDocument = this.WordControl.m_oLogicDocument;
	if (!oLogicDocument)
		return oReport;

	var oAllComments = oLogicDocument.Comments.GetAllComments();
	for (var sId in oAllComments)
	{
		var oComment = oAllComments[sId];
		privateProcessCommentData(true, oComment.GetData());
	}

	return oReport;
};

Asc['asc_docs_api'].prototype['asc_addComment']                 = Asc['asc_docs_api'].prototype.asc_addComment;
Asc['asc_docs_api'].prototype['asc_GetCommentsReportByAuthors'] = Asc['asc_docs_api'].prototype.asc_GetCommentsReportByAuthors;
